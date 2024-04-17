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
        r"""
        init the a meca host actor.

        Args:
            w3: web3 instance
            private_key: private key of the host
            dao_contract_address: dao contract address
        """
        super().__init__(
            w3=w3,
            private_key=private_key,
            dao_contract_address=dao_contract_address
        )
        self.registered = None
        r"""
        If the host is registered in the ecosystem
        """

    # helper functions
    def _bytes_from_hex_public_key(
        self,
        public_key: str
    ) -> list[bytes]:
        r"""
        Get the bytes from the hex public key. It transforms
        in an array of bytes32 of size 2

        Args:
            public_key: public key in hex

        Returns:
            list[bytes]: list of 2 bytes array of 32 bytes
        """
        if public_key.startswith("0x"):
            public_key = public_key[2:]
        if len(public_key) != 128:
            raise pymeca.utils.MecaError(
                "The public key must be 64 bytes long"
            )
        return [
            bytes.fromhex(public_key[:64]),
            bytes.fromhex(public_key[64:])
        ]

    def is_registered(self) -> bool:
        r"""
        Check if the host is registered

        Returns:
            bool: if the host is registered
        """
        if self.registered is None:
            self.registered = self.is_host_registered(
                address=self.account.address
            )
        return self.registered

    # helper getter functions
    # host related functions
    def get_my_tasks(
        self
    ) -> list:
        r"""
        Get the tasks of the host.

        Returns:
            list: list of tasks
        """
        if not self.is_registered():
            raise pymeca.utils.MecaError(
                "The host is not registered"
            )
        return self.get_host_tasks(self.account.address)

    # task related functions
    def get_task_block_timeout(
        self,
        ipfs_sha256: str
    ) -> int:
        r"""
        Get the number of blocks the task is allowed to be in the queue
        for the given host.

        Args:
            ipfs_sha256: ipfs sha256 of the task

        Returns:
            int: number of blocks
        """
        return self.get_host_task_block_timeout(
            host_address=self.account.address,
            ipfs_sha256=ipfs_sha256
        )

    def get_task_fee(
        self,
        ipfs_sha256: str
    ) -> int:
        r"""
        Get the fee of the task for the given host.

        Args:
            ipfs_sha256: ipfs sha256 of the task

        Returns:
            int: fee
        """
        return self.get_host_task_fee(
            host_address=self.account.address,
            ipfs_sha256=ipfs_sha256
        )

    # tower related functions
    def get_my_towers(
        self
    ) -> list:
        r"""
        Get the towers of the host.

        Returns:
            list: list of towers
        """
        if not self.is_registered():
            raise pymeca.utils.MecaError(
                "The host is not registered"
            )
        return self.get_host_towers(self.account.address)

    # setters
    # host related functions
    def register(
        self,
        block_timeout_limit: int,
        public_key: str,
        initial_deposit: int
    ) -> bool:
        r"""
        Register the host in the ecosystem

        Args:
            block_timeout_limit: the number of block gets for queue task
            public_key: public key of the host
            initial_deposit: initial deposit

        Returns:
            bool: if the registration was successful
        """
        if self.is_registered():
            raise pymeca.utils.MecaError(
                "The host is already registered"
            )
        if initial_deposit < self.get_host_initial_stake():
            raise pymeca.utils.MecaError(
                "The initial deposit is less than the minimum deposit"
            )
        transaction = self.get_host_contract(
        ).functions.registerAsHost(
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
        Increase stake of the host in the ecosystem.

        Args:
            amount: amount to increase

        Returns:
            bool: if the increase was successful
        """
        if not self.is_registered():
            raise pymeca.utils.MecaError(
                "The host is not registered"
            )
        transaction = (
            self.get_host_contract(
            ).functions.addStake(
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
        Update public key of the host.

        Args:
            public_key: public key in hex

        Returns:
            bool: if the update was successful
        """
        if not self.is_registered():
            raise pymeca.utils.MecaError(
                "The host is not registered"
            )
        transaction = self.get_host_contract(
        ).functions.updatePublicKey(
            newPublicKey=self._bytes_from_hex_public_key(public_key)
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
        Update block timeout limit of the host.

        Args:
            new_block_timeout_limit: new block timeout limit

        Returns:
            bool: if the update was successful
        """
        if not self.is_registered():
            raise pymeca.utils.MecaError(
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
        Unregister the host from the ecosystem.

        Returns:
            bool: if the unregister was successful
        """
        if not self.is_registered():
            raise pymeca.utils.MecaError(
                "The host is not registered"
            )
        transaction = self.get_host_contract(
        ).functions.deleteHost(
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(self.account.address)
        })

        tx_receipt = self._execute_transaction(transaction)

        self.registered = self.is_host_registered(self.account.address)

        return tx_receipt.status == 1

    # task related functions
    def add_task(
        self,
        ipfs_sha256: str,
        block_timeout: int,
        fee: int
    ) -> bool:
        r"""
        Add a task for the host in the ecosystem.

        Args:
            ipfs_sha256: ipfs sha256 of the task
            block_timeout: block timeout limit
            fee: fee of the task

        Returns:
            bool: if the add was successful
        """
        if not self.is_registered():
            raise pymeca.utils.MecaError(
                "The host is not registered"
            )
        transaction = self.get_host_contract(
        ).functions.addTask(
            ipfsSha256=ipfs_sha256,
            blockTimeout=block_timeout,
            fee=fee
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(self.account.address),
            "value": self.get_host_task_register_fee()
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def update_task_block_timeout(
        self,
        ipfs_sha256: str,
        block_timeout: int
    ) -> bool:
        r"""
        Update the number of blocks a task will take.

        Args:
            ipfs_sha256: ipfs sha256 of the task
            block_timeout: block timeout limit

        Returns:
            bool: if the update was successful
        """
        if not self.is_registered():
            raise pymeca.utils.MecaError(
                "The host is not registered"
            )
        transaction = self.get_host_contract(
        ).functions.updateTaskBlockTimeout(
            ipfsSha256=ipfs_sha256,
            newBlockTimeout=block_timeout
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(self.account.address)
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def update_task_fee(
        self,
        ipfs_sha256: str,
        fee: int
    ) -> bool:
        r"""
        Update the fee of the task for the host.

        Args:
            ipfs_sha256: ipfs sha256 of the task
            fee: fee of the task

        Returns:
            bool: if the update was successful
        """
        if not self.is_registered():
            raise pymeca.utils.MecaError(
                "The host is not registered"
            )
        transaction = self.get_host_contract(
        ).functions.updateTaskFee(
            ipfsSha256=ipfs_sha256,
            newFee=fee
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
        Remove the task from the host.

        Args:
            ipfs_sha256: ipfs sha256 of the task

        Returns:
            bool: if the delete was successful
        """
        if not self.is_registered():
            raise pymeca.utils.MecaError(
                "The host is not registered"
            )
        transaction = self.get_host_contract(
        ).functions.deleteTask(
            ipfsSha256=ipfs_sha256
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(self.account.address)
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    # tower related functions
    def register_for_tower(
        self,
        tower_address: str
    ) -> bool:
        r"""
        Register the host for a tower as pending host.

        Args:
            tower_address: tower address

        Returns:
            bool: if the register was successful
        """
        if not self.is_registered():
            raise pymeca.utils.MecaError(
                "The host is not registered"
            )
        transaction = self.get_tower_contract(
        ).functions.registerMeForTower(
            towerAddress=tower_address
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(self.account.address),
            "value": self.get_tower_host_request_fee()
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    # schedule related functions
    def register_task_output(
        self,
        task_id: str,
        output_hash: str
    ) -> bool:
        r"""
        Register the output of the task.

        Args:
            task_id : Task ID.
            output_hash: the hash of the output of the task

        Returns:
            bool: if the register was successful
        """
        if not self.is_registered():
            raise pymeca.utils.MecaError(
                "The host is not registered"
            )
        transaction = self.get_scheduler_contract(
        ).functions.registerTaskOutput(
            taskId=self._bytes_from_hex(task_id),
            outputHash=self._bytes_from_hex(output_hash)
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            )
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def wrong_input_hash(
        self,
        task_id: str
    ) -> bool:
        r"""
        Register the wrong input hash of the task.

        Args:
            task_id : Task ID.

        Returns:
            bool: if the register was successful
        """
        if not self.is_registered():
            raise pymeca.utils.MecaError(
                "The host is not registered"
            )
        transaction = self.get_scheduler_contract(
        ).functions.wrongInputHash(
            taskId=self._bytes_from_hex(task_id)
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            )
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1
