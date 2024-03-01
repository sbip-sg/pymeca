import logging
import web3
import pymeca.pymeca
import pymeca.utils

logger = logging.getLogger(__name__)


class MecaHost(pymeca.pymeca.MecaActiveActor):
    def __init__(
        self,
        w3: web3.Web3,
        private_key: str,
        dao_contract_address: str
    ):
        super().__init__(
            w3=w3,
            private_key=private_key,
            dao_contract_address=dao_contract_address
        )
        self.registered = None

    def _bytes_from_hex_public_key(
        self,
        public_key: str
    ) -> list[bytes]:
        r"""
        Bytes from hex public key
        """
        if public_key.startswith("0x"):
            public_key = public_key[2:]
        if len(public_key) != 128:
            raise ValueError(
                "The public key must be 64 bytes long"
            )
        return [
            bytes.fromhex(public_key[:64]),
            bytes.fromhex(public_key[64:])
        ]

    def is_host_registered(
        self,
        address: str
    ) -> bool:
        r"""
        Is host registered
        """
        hosts_list = self.get_hosts()
        for host in hosts_list:
            if host["owner"] == address:
                return True
        return False

    def is_registered(self) -> bool:
        r"""
        Is registered
        """
        if self.registered is None:
            self.registered = self.is_host_registered(self.account.address)
        return self.registered

    def register(
        self,
        block_timeout_limit: int,
        public_key: str,
        initial_deposit: int
    ) -> bool:
        r"""
        Register
        """
        if self.is_registered():
            raise ValueError(
                "The host is already registered"
            )
        if initial_deposit < self.get_host_initial_stake():
            raise ValueError(
                "The initial deposit is less than the minimum deposit"
            )
        transaction = self.get_host_contract().functions.registerAsHost(
            publicKey=self._bytes_from_hex_public_key(public_key),
            blockTimeoutLimit=block_timeout_limit
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(self.account.address),
            "value": initial_deposit
        })

        tx_receipt = self._execute_transaction(transaction)

        self.registered = self.is_host_registered(self.account.address)

        return tx_receipt.status == 1

    def increase_stake(
        self,
        amount: int
    ) -> bool:
        r"""
        Increase stake
        """
        if not self.is_registered():
            raise ValueError(
                "The host is not registered"
            )
        transaction = (
            self.get_host_contract().functions.addStake(
            ).build_transaction({
                "from": self.account.address,
                "nonce": self.w3.eth.get_transaction_count(
                    self.account.address
                ),
                "value": amount
            })
        )

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def update_public_key(
        self,
        public_key: str
    ) -> bool:
        r"""
        Update public key
        """
        if not self.is_registered():
            raise ValueError(
                "The host is not registered"
            )
        transaction = self.get_host_contract().functions.updatePublicKey(
            self._bytes_from_hex_public_key(public_key)
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(self.account.address)
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def update_block_timeout_limit(
        self,
        new_block_timeout_limit: int
    ) -> bool:
        r"""
        Update block timeout limit
        """
        if not self.is_registered():
            raise ValueError(
                "The host is not registered"
            )
        transaction = self.get_host_contract(
        ).functions.updateBlockTimeoutLimit(
            newBlockTimeoutLimit=new_block_timeout_limit
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(self.account.address)
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def unregister(
        self
    ) -> bool:
        r"""
        Unregister
        """
        if not self.is_registered():
            raise ValueError(
                "The host is not registered"
            )
        transaction = self.get_host_contract().functions.deleteHost(
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(self.account.address)
        })

        tx_receipt = self._execute_transaction(transaction)

        self.registered = self.is_host_registered(self.account.address)

        return tx_receipt.status == 1

    def get_my_tasks(
        self
    ) -> list:
        r"""
        Get my tasks
        """
        if not self.is_registered():
            raise ValueError(
                "The host is not registered"
            )
        return self.get_host_tasks(self.account.address)

    def add_task(
        self,
        ipfs_sha256: str,
        block_timeout: int,
        fee: int
    ) -> bool:
        r"""
        Add task
        """
        if not self.is_registered():
            raise ValueError(
                "The host is not registered"
            )
        transaction = self.get_host_contract().functions.addTask(
            ipfs_sha256, block_timeout, fee
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(self.account.address),
            "value": self.get_host_task_register_fee()
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def get_task_block_timeout(
        self,
        ipfs_sha256: str
    ) -> int:
        r"""
        Get task block timeout
        """
        return self.get_host_task_block_timeout(
            host_address=self.account.address,
            ipfs_sha256=ipfs_sha256
        )

    def update_task_block_timeout(
        self,
        ipfs_sha256: str,
        block_timeout: int
    ) -> bool:
        r"""
        Update task block timeout
        """
        if not self.is_registered():
            raise ValueError(
                "The host is not registered"
            )
        transaction = self.get_host_contract(
        ).functions.updateTaskBlockTimeout(
            ipfs_sha256, block_timeout
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(self.account.address)
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def get_task_fee(
        self,
        ipfs_sha256: str
    ) -> int:
        r"""
        Get task fee
        """
        return self.get_host_task_fee(
            host_address=self.account.address,
            ipfs_sha256=ipfs_sha256
        )

    def update_task_fee(
        self,
        ipfs_sha256: str,
        fee: int
    ) -> bool:
        r"""
        Update task fee
        """
        if not self.is_registered():
            raise ValueError(
                "The host is not registered"
            )
        transaction = self.get_host_contract().functions.updateTaskFee(
            ipfs_sha256, fee
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(self.account.address)
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def delete_task(
        self,
        ipfs_sha256: str
    ) -> bool:
        r"""
        Delete task
        """
        if not self.is_registered():
            raise ValueError(
                "The host is not registered"
            )
        transaction = self.get_host_contract().functions.deleteTask(
            ipfs_sha256
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(self.account.address)
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def register_for_tower(
        self,
        tower_address: str
    ) -> bool:
        r"""
        Register for tower
        """
        if not self.is_registered():
            raise ValueError(
                "The host is not registered"
            )
        transaction = self.get_tower_contract().functions.registerMeForTower(
            towerAddress=tower_address
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(self.account.address),
            "value": self.get_tower_host_request_fee()
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1
