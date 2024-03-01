import web3
import logging
import pymeca.pymeca
import pymeca.utils

logger = logging.getLogger(__name__)


class MecaTaskDeveloper(pymeca.pymeca.MecaActiveActor):
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

    def register_task(
        self,
        ipfs_sha256: str,
        fee: int,
        computing_type: int,
        size: int
    ) -> bool:
        transaction = self.get_task_contract().functions.addTask(
            ipfsSha256=self._bytes_from_hex(ipfs_sha256),
            fee=fee,
            computingType=computing_type,
            size=size
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            ),
            "value": self.get_task_addition_fee()
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def register_task_cid(
        self,
        cid: str,
        fee: int,
        computing_type: int,
        size: int
    ) -> bool:
        return self.register_task(
            ipfs_sha256=pymeca.utils.get_sha256_from_cid(cid),
            fee=fee,
            computing_type=computing_type,
            size=size
        )

    def get_my_tasks(self) -> list:
        all_tasks = self.get_tasks()
        my_tasks = []
        for task in all_tasks:
            print(task)
            if task["owner"] == self.account.address:
                my_tasks.append(task)
        return my_tasks

    def update_task_fee(
        self,
        ipfs_sha256: str,
        fee: int
    ) -> bool:
        transaction = self.get_task_contract().functions.updateTaskFee(
            ipfsSha256=self._bytes_from_hex(ipfs_sha256),
            newFee=fee
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            )
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def update_task_size(
        self,
        ipfs_sha256: str,
        size: int
    ) -> bool:
        transaction = self.get_task_contract().functions.updateTaskSize(
            ipfsSha256=ipfs_sha256,
            newSize=size
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            )
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def update_task_owner(
        self,
        ipfs_sha256: str,
        new_owner: str
    ) -> bool:
        transaction = self.get_task_contract().functions.updateTaskOwner(
            ipfsSha256=self._bytes_from_hex(ipfs_sha256),
            newOwner=new_owner
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            )
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def delete_task(
        self,
        ipfs_sha256: str
    ) -> bool:
        transaction = self.get_task_contract().functions.deleteTask(
            ipfsSha256=self._bytes_from_hex(ipfs_sha256)
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            )
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1
