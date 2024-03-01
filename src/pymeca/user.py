import logging
import web3
import pymeca.pymeca
import pymeca.utils

logger = logging.getLogger(__name__)


class MecaUser(pymeca.pymeca.MecaActiveActor):
    def __init__(
        self,
        w3: web3.Web3,
        private_key: str,
        dao_contract_address: str
    ) -> None:
        super().__init__(
            w3=w3,
            private_key=private_key,
            dao_contract_address=dao_contract_address
        )

    def send_task_on_blockchain(
        self,
        ipfs_sha256: str,
        host_address: str,
        tower_address: str,
        input_hash: str
    ) -> tuple[bool, str]:
        task_fee = self.get_task_task_fee(
            ipfs_sha256=ipfs_sha256
        )
        task_size = self.get_task_task_size(
            ipfs_sha256=ipfs_sha256
        )
        task_block_timeout = self.get_host_task_block_timeout(
            host_address=host_address,
            ipfs_sha256=ipfs_sha256
        )
        tower_fee = self.get_tower_fee(
            tower_address=tower_address,
            size=task_size,
            block_timeout_limit=task_block_timeout
        )
        host_fee = self.get_host_task_fee(
            host_address=host_address,
            ipfs_sha256=ipfs_sha256
        )
        insurance_fee = (task_fee + tower_fee + host_fee) / 10
        total_fee = int(
            task_fee +
            tower_fee +
            host_fee +
            insurance_fee +
            self.get_scheduler_fee()
        )

        transaction = self.get_scheduler_contract().functions.sendTask(
            ipfsSha256=self._bytes_from_hex(ipfs_sha256),
            hostAddress=host_address,
            towerAddress=tower_address,
            inputHash=self._bytes_from_hex(input_hash)
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            ),
            "value": total_fee
        })

        tx_receipt = self._execute_transaction(transaction=transaction)

        # get logs of tx_receipt
        logs = self.get_scheduler_contract().events.TaskSent().process_receipt(
            tx_receipt
        )

        if len(logs) == 0:
            raise pymeca.utils.MecaError(
                "TaskSent event not found in transaction receipt"
            )
        if len(logs) > 1:
            raise pymeca.utils.MecaError(
                "More than one TaskSent event found in transaction receipt"
            )

        logs = logs[0]
        log = logs["args"]
        task_id = "0x" + log["taskId"].hex()

        return (tx_receipt.status == 1, task_id)

    def finish_task(
        self,
        task_id: str,
    ) -> bool:
        transaction = self.get_scheduler_contract().functions.finishTask(
            taskId=self._bytes_from_hex(task_id)
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            )
        })

        tx_receipt = self._execute_transaction(transaction=transaction)

        return tx_receipt.status == 1

    def get_towers_hosts_for_task(
        self,
        ipfs_sha256: str
    ) -> list:
        # get all hosts
        hosts = self.get_hosts()
        # filter the hosts that have the task
        # and compute the fees
        hosts = [
            {
                "owner": host["owner"],
                "eccPublicKey": host["eccPublicKey"],
                "blockTimeoutLimit": host["blockTimeoutLimit"],
                "fee": self.get_host_task_fee(
                    host_address=host["owner"],
                    ipfs_sha256=ipfs_sha256
                ),
                "blockTimeout": self.get_host_task_block_timeout(
                    host_address=host["owner"],
                    ipfs_sha256=ipfs_sha256
                )
            }
            for host in hosts
            if self.get_host_task_block_timeout(
                host_address=host["owner"],
                ipfs_sha256=ipfs_sha256
            ) > 0
        ]
        # get task size and task fee
        task_size = self.get_task_task_size(
            ipfs_sha256=ipfs_sha256
        )
        task_fee = self.get_task_task_fee(
            ipfs_sha256=ipfs_sha256
        )
        # get towers
        towers = self.get_towers()
        # filter the hosts which can run the task
        hosts = [
            {
                "owner": host["owner"],
                "eccPublicKey": host["eccPublicKey"],
                "endBlock": (
                    host["blockTimeout"] +
                    self.get_host_first_available_block(
                        host_address=host["owner"]
                    )
                ),
                "fee": host["fee"],
                "blockTimeout": host["blockTimeout"]
            }
            for host in hosts
            if (
                (
                    host["blockTimeout"] +
                    self.get_host_first_available_block(
                        host_address=host["owner"]
                    )
                ) <= (
                    self.w3.eth.get_block("latest")["number"] +
                    host["blockTimeoutLimit"]
                )
            )
        ]
        # filter the towers which have the size to run the task
        towers = [
            {
                "owner": tower["owner"],
                "publicConnection": tower["publicConnection"]
            }
            for tower in towers
            if (
                (
                    self.get_tower_current_size(tower_address=tower["owner"]) +
                    task_size
                ) <= (
                    tower["sizeLimit"]
                )
            )
        ]
        # make the join of towers and hosts and make the list of
        # possible combinations of running the tasks with pairs
        # of towers and hosts
        schedule_fee: int = self.get_scheduler_fee()

        def fee_dict(
            tower_fee: int,
            host_fee: int,
        ) -> dict:
            total_fee = (
                task_fee +
                tower_fee +
                host_fee +
                schedule_fee
            )
            insurance_fee = int(total_fee / 10)
            return {
                "insurance": insurance_fee,
                "tower": tower_fee,
                "host": host_fee,
                "schedule": schedule_fee,
                "task": task_fee
            }

        towers_hosts = [
            {
                "towerAddress": tower["owner"],
                "hostAddress": host["owner"],
                "endBlock": host["endBlock"],
                "fee": fee_dict(
                    tower_fee=self.get_tower_fee(
                        tower_address=tower["owner"],
                        size=task_size,
                        block_timeout_limit=host["blockTimeout"]
                    ),
                    host_fee=host["fee"]
                )
            }
            for tower in towers
            for host in hosts
            if (
                host["owner"] in self.get_tower_hosts(
                    tower_address=tower["owner"]
                )
            )
        ]
        return towers_hosts
