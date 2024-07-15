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
        r"""
        Init a user.

        Args:
            w3 : Web3 instance.
            private_key : Private key of the user
            dao_contract_address : DAO contract address.
        """
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
        r"""
        Send a task on the blockchain.

        Args:
            ipfs_sha256 : IPFS SHA256 hash of the task.
            host_address : Host address.
            tower_address : Tower address.
            input_hash : Input hash.

        Returns:
            tuple[bool, str] : (status, task_id)
        """
        # get the fees
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

        # send the task
        transaction = self.get_scheduler_contract(
        ).functions.sendTask(
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

        # get logs of tx_receipt to find out the task_id
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

    def register_tee_task_initial_input(
        self,
        task_id: str,
        hash_initial_input: bytes
    ) -> bool:
        r"""
        Register TEE task initial input.

        Args:
            task_id : Task ID.
            hash_initial_input : hash of the initial input.

        Returns:
            bool : True if the initial input was registered successfully.
        """
        transaction = self.get_scheduler_contract(
        ).functions.registerTeeTaskInitialInput(
            taskId=self._bytes_from_hex(task_id),
            initialInputHash=hash_initial_input
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            )
        })

        tx_receipt = self._execute_transaction(transaction=transaction)

        return tx_receipt.status == 1

    def register_tee_task_encrypted_input(
        self,
        task_id: str,
        hash_encrypted_input: bytes
    ) -> bool:
        r"""
        Register TEE task encrypted input.

        Args:
            task_id : Task ID.
            hash_encrypted_input : Encrypted input.

        Returns:
            bool : True if the encrypted input was registered successfully.
        """
        transaction = self.get_scheduler_contract(
        ).functions.registerTeeTaskEncryptedInput(
            taskId=self._bytes_from_hex(task_id),
            encryptedInputHash=hash_encrypted_input
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            )
        })

        tx_receipt = self._execute_transaction(transaction=transaction)

        return tx_receipt.status == 1

    def finish_task(
        self,
        task_id: str,
    ) -> bool:
        r"""
        Finish a task.

        Args:
            task_id : Task ID.

        Returns:
            bool : True if the task was finished successfully.
        """
        transaction = self.get_scheduler_contract(
        ).functions.finishTask(
            taskId=self._bytes_from_hex(task_id)
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            )
        })

        tx_receipt = self._execute_transaction(transaction=transaction)

        return tx_receipt.status == 1
