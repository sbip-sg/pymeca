import logging
from eth_account import Account
import web3
import pymeca.utils

logger = logging.getLogger(__name__)


class MecaActor():
    def __init__(
        self,
        w3: web3.Web3,
        private_key: str
    ) -> None:
        r"""
        Meca Actor

        Args:
            w3 : web3 instance
            private_key : private key
        """
        self.w3 = w3
        self.private_key = private_key
        self.account = Account.from_key(private_key)

    def _execute_transaction(
        self,
        transaction: dict
    ) -> web3.datastructures.AttributeDict:
        r"""
        Execute the given transaction

        Args:
            transaction : transaction
        """
        # verify the balance
        account_balance = self.w3.eth.get_balance(self.account.address)
        if account_balance < (transaction["gas"] * self.w3.eth.gas_price):
            raise ValueError(
                "Insufficient balance"
            )

        return pymeca.utils.sign_send_wait_transaction(
            w3=self.w3,
            transaction=transaction,
            private_key=self.private_key
        )

    def sign_bytes(
        self,
        bytes_to_sign: bytes
    ) -> bytes:
        r"""
        Sign the given bytes

        Args:
            bytes_to_sign : bytes

        Returns:
            bytes : The signature
        """
        return pymeca.utils.sign_bytes(
            private_key=self.private_key,
            message_bytes=bytes_to_sign
        )


def task_from_tuple(
    task_tuple: tuple
) -> dict:
    r"""
    Transform task tuple from the web3 result in
    a dictionary

    Args:
        task_tuple : task tuple

    Returns:
        task : task dictionary
        {
            "ipfsSha256"
            "owner"
            "fee"
            "computingType"
            "size"
        }
    """
    return {
        "ipfsSha256": "0x" + task_tuple[0].hex().strip(),
        "owner": task_tuple[1],
        "fee": task_tuple[2],
        "computingType": task_tuple[3],
        "size": task_tuple[4]
    }


def running_task_fee_from_tuple(
    running_task_fee_tuple: tuple
) -> dict:
    r"""
    Transform a running task fee tuple from the web3 result in
    a dictionary

    Args:
        running_task_fee_tuple : The fee of a runing task

    Returns:
        running_task_fee : running task fee dictionary
        {
            "tower"
            "host"
            "scheduler"
            "task"
            "insurance"
        }
    """
    return {
        "tower": running_task_fee_tuple[0],
        "host": running_task_fee_tuple[1],
        "scheduler": running_task_fee_tuple[2],
        "task": running_task_fee_tuple[3],
        "insurance": running_task_fee_tuple[4]
    }


def running_task_from_tuple(
    running_task_tuple: tuple
) -> dict:
    r"""
    Transform a running task tuple from the web3 result in
    a dictionary

    Args:
        running_task_tuple : running task tuple

    Returns:
        running_task : running task dictionary
        {
            "ipfsSha256"
            "inputHash"
            "outputHash"
            "size"
            "towerAddress"
            "hostAddress"
            "owner"
            "startBlock"
            "blockTimeout"
            "fee"
        }
    """
    # raise ValueError(running_task_tuple)
    return {
        "ipfsSha256": "0x" + running_task_tuple[0].hex().strip(),
        "inputHash": "0x" + running_task_tuple[1].hex().strip(),
        "outputHash": "0x" + running_task_tuple[2].hex().strip(),
        "size": running_task_tuple[3],
        "towerAddress": running_task_tuple[4],
        "hostAddress": running_task_tuple[5],
        "owner": running_task_tuple[6],
        "startBlock": running_task_tuple[7],
        "blockTimeout": running_task_tuple[8],
        "fee": running_task_fee_from_tuple(running_task_tuple[9])
    }


def tee_task_from_tuple(
    tee_task_tuple: tuple
) -> dict:
    r"""
    Transform a tee task tuple from the web3 result in
    a dictionary

    Args:
        tee_task_tuple : tee task tuple

    Returns:
        tee_task : tee task dictionary
        {
            "encryptedInputHash"
            "initialInputHash"
        }
    """
    return {
        "encryptedInputHash": "0x" + tee_task_tuple[0].hex().strip(),
        "initialInputHash": "0x" + tee_task_tuple[1].hex().strip(),
    }


def host_from_tuple(
    host_tuple: tuple
) -> dict:
    r"""
    Transform a host tuple from the web3 result in
    a dictionary

    Args:
        host_tuple : host tuple

    Returns:
        host : host dictionary
        {
            "owner"
            "eccPublicKey"
            "blockTimeoutLimit"
            "stake"
        }
    """
    return {
        "owner": host_tuple[0],
        "eccPublicKey": "0x" + "".join([
            x.hex().strip() for x in host_tuple[1]
        ]),
        "blockTimeoutLimit": host_tuple[2],
        "stake": host_tuple[3]
    }


def tower_from_tuple(
    tower_tuple: tuple
) -> dict:
    r"""
    Transform a tower tuple from the web3 result in
    a dictionary

    Args:
        tower_tuple : tower tuple

    Returns:
        tower : tower dictionary
        {
            "owner"
            "sizeLimit"
            "publicConnection"
            "feeType"
            "fee"
            "stake"
        }
    """
    return {
        "owner": tower_tuple[0],
        "sizeLimit": tower_tuple[1],
        "publicConnection": tower_tuple[2],
        "feeType": tower_tuple[3],
        "fee": tower_tuple[4],
        "stake": tower_tuple[5]
    }


class MecaActiveActor(MecaActor):
    def __init__(
        self,
        w3: web3.Web3,
        private_key: str,
        dao_contract_address: str
    ) -> None:
        r"""
        Meca Active Actor which is interacting with the blockchain
        as a getter for infromation. Specific functions for diiferent
        type of actors are implemented in the derived classes.

        Args:
            w3 : web3 instance
            private_key : private key
            dao_contract_address : The DAO contract address
        """
        super().__init__(w3=w3, private_key=private_key)

        # get the dao contract
        self.dao_contract = self.w3.eth.contract(
            address=dao_contract_address,
            abi=pymeca.utils.MECA_DAO_ABI
        )
        """
        The DAO contract used to interact with the blockchain
        ecosystem
        """

    # helper functions
    def _bytes_from_hex(
        self,
        hex_string: str
    ) -> bytes:
        r"""
        Convert a hex string to bytes. Usseful for making
        the input for bytesX in the smart contracts

        Args:
            hex_string : hex string

        Returns:
            bytes : bytes
        """
        if hex_string.startswith("0x"):
            hex_string = hex_string[2:]
        return bytes.fromhex(hex_string)

    # dao contract functions
    def get_scheduler_contract_address(self) -> str:
        r"""
        Get the scheduler contract address

        Returns:
            str : The scheduler contract address
        """
        return self.dao_contract.functions.getSchedulerContract().call()

    def get_scheduler_contract(self) -> web3.contract.Contract:
        r"""
        Get the scheduler contract

        Returns:
            web3.contract.Contract : The scheduler contract
        """
        return self.w3.eth.contract(
            address=self.get_scheduler_contract_address(),
            abi=pymeca.utils.MECA_SCHEDULER_ABI
        )

    # scheduler contract functions
    def get_scheduler_flag(self) -> bool:
        r"""
        Get the scheduler flag

        Returns:
            bool : The scheduler flag
        """
        return self.get_scheduler_contract(
        ).functions.schedulerFlag().call()

    def get_tower_contract_address(self) -> str:
        r"""
        Get the tower contract address

        Returns:
            str : The tower contract address
        """
        return self.get_scheduler_contract(
        ).functions.getTowerContract().call()

    def get_tower_contract(self) -> web3.contract.Contract:
        r"""
        Get the tower contract

        Returns:
            web3.contract.Contract : The tower contract
        """
        return self.w3.eth.contract(
            address=self.get_tower_contract_address(),
            abi=pymeca.utils.MECA_TOWER_ABI
        )

    def get_host_contract_address(self) -> str:
        r"""
        Get the host contract address

        Returns:
            str : The host contract address
        """
        return self.get_scheduler_contract(
        ).functions.getHostContract().call()

    def get_host_contract(self) -> web3.contract.Contract:
        r"""
        Get the host contract

        Returns:
            web3.contract.Contract : The host contract
        """
        return self.w3.eth.contract(
            address=self.get_host_contract_address(),
            abi=pymeca.utils.MECA_HOST_ABI
        )

    def get_task_contract_address(self) -> str:
        r"""
        Get the task contract address

        Returns:
            str : The task contract address
        """
        return self.get_scheduler_contract(
        ).functions.getTaskContract().call()

    def get_task_contract(self) -> web3.contract.Contract:
        r"""
        Get the task contract

        Returns:
            web3.contract.Contract : The task contract
        """
        return self.w3.eth.contract(
            address=self.get_task_contract_address(),
            abi=pymeca.utils.MECA_TASK_ABI
        )

    def get_scheduler_fee(self) -> int:
        r"""
        Get the scheduler fee

        Returns:
            int : The scheduler fee
        """
        return self.get_scheduler_contract(
        ).functions.SCHEDULER_FEE().call()

    def get_host_first_available_block(
        self,
        host_address: str
    ) -> int:
        r"""
        Get the first available block number for a host when
        it can run the next task.

        Args:
            host_address : The host address

        Returns:
            int : The first available block number
        """
        return self.get_scheduler_contract(
        ).functions.getHostFirstAvailableBlock(
            hostAddress=host_address
        ).call()

    def get_tower_current_size(
        self,
        tower_address: str
    ) -> int:
        r"""
        Get the current used size of a tower.

        Args:
            tower_address : The tower address

        Returns:
            int : The current used size of the tower
        """
        return self.get_scheduler_contract(
        ).functions.getTowerCurrentSize(
            towerAddress=tower_address
        ).call()

    def get_running_task(
        self,
        task_id: str
    ) -> dict:
        r"""
        Get the running task information for a task which
        is running on the scheduler.

        Args:
            task_id : The task id on the scheduler

        Returns:
            dict : The running task
        """
        tuple_running_task = self.get_scheduler_contract(
        ).functions.getRunningTask(
            taskId=self._bytes_from_hex(task_id)
        ).call()
        return running_task_from_tuple(tuple_running_task)

    def get_tee_task(
        self,
        task_id: str
    ) -> dict:
        r"""
        Get the tee task information for a task which
        is running on the scheduler.

        Args:
            task_id : The task id on the scheduler

        Returns:
            dict : The tee task
        """
        tuple_tee_task = self.get_scheduler_contract(
        ).functions.getTeeTask(
            taskId=self._bytes_from_hex(task_id)
        ).call()
        return tee_task_from_tuple(tuple_tee_task)

    # host contract functions
    def get_host_register_fee(
        self
    ) -> int:
        r"""
        Get the fee to regiser a host on the host contract

        Returns:
            int : The host register fee (Wei)
        """
        return self.get_host_contract(
        ).functions.HOST_REGISTER_FEE().call()

    def get_host_task_register_fee(
        self
    ) -> int:
        r"""
        Get the fee to register a new task for a host
        on the host contract

        Returns:
            int : The host task register fee (Wei)
        """
        return self.get_host_contract(
        ).functions.TASK_REGISTER_FEE().call()

    def get_host_initial_stake(
        self
    ) -> int:
        r"""
        Get the initial stake a host has to deposit
        to be used in the system.

        Returns:
            int : The initial stake (Wei)
        """
        return self.get_host_contract(
        ).functions.HOST_INITIAL_STAKE().call()

    def get_host_failed_task_penalty(
        self
    ) -> int:
        r"""
        Get the penalty percentage out of 100 for a failed task
        for a host. TODO: maybe use a different concept for this

        Returns:
            int : The failed task penalty percentage
        """
        return self.get_host_contract(
        ).functions.FAILED_TASK_PENALTY().call()

    def get_host_public_key(
        self,
        host_address: str
    ) -> str:
        r"""
        Get the public key of a host.

        Args:
            host_address : The host address

        Returns:
            str : The public key of the host starting with 0x
        """
        bytes_array = self.get_host_contract(
        ).functions.getHostPublicKey(
            hostAddress=host_address
        ).call()
        return "0x" + "".join([
                x.hex().strip() for x in bytes_array
        ])

    def get_host_block_timeout_limit(
        self,
        host_address: str
    ) -> int:
        r"""
        Ge the number of nodes from the current block that
        a host accept task to run.

        Args:
            host_address : The host address

        Returns:
            int : The block timeout limit
        """
        return self.get_host_contract(
        ).functions.getHostBlockTimeoutLimit(
            hostAddress=host_address
        ).call()

    def get_host_stake(
        self,
        host_address: str
    ) -> int:
        r"""
        Get the stake of a host.

        Args:
            host_address : The host address

        Returns:
            int : The stake of the host
        """
        return self.get_host_contract(
        ).functions.getHostStake(
            hostAddress=host_address
        ).call()

    def get_hosts(
        self
    ) -> list:
        r"""
        Get all the hosts registered in the system

        Returns:
            list : The list of hosts
        """
        tuple_hots = self.get_host_contract(
        ).functions.getHosts().call()
        return [host_from_tuple(host) for host in tuple_hots]

    def get_host_task_block_timeout(
        self,
        host_address: str,
        ipfs_sha256: str
    ) -> int:
        r"""
        Get the number of blocks will take for a host to run
        a task.

        Args:
            host_address : The host address
            ipfs_sha256 : The ipfs sha256 hash of the task

        Returns:
            int : The number of block to run a task
        """
        return self.get_host_contract(
        ).functions.getTaskBlockTimeout(
            hostAddress=host_address,
            ipfsSha256=ipfs_sha256
        ).call()

    def get_host_task_fee(
        self,
        host_address: str,
        ipfs_sha256: str
    ) -> int:
        r"""
        Get the fee for a task to be run on a host.

        Args:
            host_address : The host address
            ipfs_sha256 : The ipfs sha256 hash of the task

        Returns:
            int : The fee for the task
        """
        return self.get_host_contract(
        ).functions.getTaskFee(
            hostAddress=host_address,
            ipfsSha256=ipfs_sha256
        ).call()

    def is_host_registered(
        self,
        address: str
    ) -> bool:
        r"""
        Check if a host is registered in the system.

        Args:
            address : The host address

        Returns:
            bool : True if the host is registered, False otherwise
        """
        hosts_list = self.get_hosts()
        for host in hosts_list:
            if host["owner"] == address:
                return True
        return False

    # tower contract functions
    def get_tower_initial_stake(
        self
    ) -> int:
        r"""
        Get the initial stake a tower has to deposit
        to be used in the system.

        Returns:
            int : The initial stake (Wei)
        """
        return self.get_tower_contract(
        ).functions.TOWER_INITIAL_STAKE().call()

    def get_tower_failed_task_penalty(
        self
    ) -> int:
        r"""
        Get the penalty percentage out of 100 for a failed task
        for a tower. TODO: maybe use a different concept for this

        Returns:
            int : The failed task penalty percentage
        """
        return self.get_tower_contract(
        ).functions.FAILED_TASK_PENALTY().call()

    def get_tower_host_request_fee(
        self
    ) -> int:
        r"""
        Get the fee for a host to request to be added to a tower.

        Returns:
            int : The host request fee (Wei)
        """
        return self.get_tower_contract(
        ).functions.HOST_REQUEST_FEE().call()

    def get_tower_size_limit(
        self,
        tower_address: str
    ) -> int:
        r"""
        Get the maximum size a tower can handle in a given time.

        Args:
            tower_address : The tower address

        Returns:
            int : The size limit
        """
        return self.get_tower_contract(
        ).functions.getTowerSizeLimit(
            towerAddress=tower_address
        ).call()

    def get_tower_public_uri(
        self,
        tower_address: str
    ) -> str:
        r"""
        Get the public URI of a tower, the public connection
        point for the tower.

        Args:
            tower_address : The tower address

        Returns:
            str : The public URI
        """
        return self.get_tower_contract(
        ).functions.getTowerPublicConnection(
            towerAddress=tower_address
        ).call()

    def get_tower_fee(
        self,
        tower_address: str,
        size: int,
        block_timeout_limit: int
    ) -> int:
        r"""
        Get the fee for a tower to run a task of
        a given size and for a number of blocks.

        Args:
            tower_address : The tower address
            size : The size of the task
            block_timeout_limit : The number of blocks to run the task

        Returns:
            int : The fee for the task to be run on the tower (Wei)
        """
        return self.get_tower_contract(
        ).functions.getTowerFee(
            towerAddress=tower_address,
            size=size,
            blockTimeoutLimit=block_timeout_limit
        ).call()

    def get_tower_stake(
        self,
        tower_address: str
    ) -> int:
        r"""
        Get the stake of a tower.

        Args:
            tower_address : The tower address

        Returns:
            int : The stake of the tower
        """
        return self.get_tower_contract(
        ).functions.getTowerStake(
            towerAddress=tower_address
        ).call()

    def get_tower_pending_hosts(
        self,
        tower_address: str
    ) -> list:
        r"""
        Get the pending hosts for a tower.

        Args:
            tower_address : The tower address

        Returns:
            list : The list of pending hosts
        """
        return self.get_tower_contract(
        ).functions.getTowerPendingHosts(
            towerAddress=tower_address
        ).call()

    def get_tower_hosts(
        self,
        tower_address: str
    ) -> list:
        r"""
        Get a list of hosts that the given tower has.

        Args:
            tower_address : The tower address

        Returns:
            list : The list of hosts
        """
        return self.get_tower_contract(
        ).functions.getTowerHosts(
            towerAddress=tower_address
        ).call()

    def get_towers(
        self
    ) -> list:
        r"""
        Get all the towers registered in the system

        Returns:
            list : The list of towers
        """
        tuple_towers = self.get_tower_contract(
        ).functions.getTowers().call()
        return [tower_from_tuple(tower) for tower in tuple_towers]

    def is_tower_registered(
        self,
        address: str
    ) -> bool:
        r"""
        Check if a tower is registered in the system.

        Args:
            address : The tower address

        Returns:
            bool : True if the tower is registered, False otherwise
        """
        towers_list = self.get_towers()
        for tower in towers_list:
            if tower["owner"] == address:
                return True
        return False

    # task contract functions
    def get_task_addition_fee(
        self
    ) -> int:
        r"""
        Get the fee to add a new task to the task contract
        by the owner of the task.

        Returns:
            int : The task addition fee (Wei)
        """
        return self.get_task_contract(
        ).functions.TASK_ADDITION_FEE().call()

    def get_task_task_fee(
        self,
        ipfs_sha256: str
    ) -> int:
        r"""
        Get the fee for a task to be sent to the task owner
        every time the task is run.

        Args:
            ipfs_sha256 : The ipfs sha256 hash of the task

        Returns:
            int : The task fee (Wei)
        """
        return self.get_task_contract(
        ).functions.getTaskFee(
            ipfsSha256=ipfs_sha256
        ).call()

    def get_task_task_size(
        self,
        ipfs_sha256: str
    ) -> int:
        r"""
        Get the size of a task on storage for tower/host.
        It is the comulative input and output size of the task.
        It is different from the size of the task itself.

        Args:
            ipfs_sha256 : The ipfs sha256 hash of the task

        Returns:
            int : The task size (bytes)
        """
        return self.get_task_contract(
        ).functions.getTaskSize(
            ipfsSha256=ipfs_sha256
        ).call()

    def get_task_computing_type(
        self,
        ipfs_sha256: str
    ) -> int:
        r"""
        Get the computing type of a task. (0: CPU, 1: GPU)

        Args:
            ipfs_sha256 : The ipfs sha256 hash of the task

        Returns:
            int : The computing type
        """
        return self.get_task_contract(
        ).functions.getTaskComputingType(
            ipfsSha256=ipfs_sha256
        ).call()

    def get_task_owner(
        self,
        ipfs_sha256: str
    ) -> str:
        r"""
        Get the owner of a task.

        Args:
            ipfs_sha256 : The ipfs sha256 hash of the task

        Returns:
            str : The owner of the task
        """
        return self.get_task_contract(
        ).functions.getTaskOwner(
            ipfsSha256=ipfs_sha256
        ).call()

    def get_tasks(
        self
    ) -> list:
        r"""
        Get all the tasks registered in the system

        Returns:
            list : The list of tasks
        """
        tuple_list = self.get_task_contract(
        ).functions.getTasks().call()
        return [task_from_tuple(task) for task in tuple_list]

    # combine contract functions
    def get_host_tasks(
        self,
        host_address: str
    ) -> list:
        r"""
        Get the tasks that a host can run.

        Args:
            host_address : The host address

        Returns:
            list : The list of tasks the host can run
        """
        all_tasks = self.get_tasks()
        host_tasks = []
        for task in all_tasks:
            block_timeout = self.get_host_task_block_timeout(
                host_address=host_address,
                ipfs_sha256=task["ipfsSha256"]
            )
            if block_timeout > 0:
                host_tasks.append(task)
        return host_tasks

    def get_host_towers(
        self,
        host_address: str
    ) -> list:
        r"""
        Get the towers that a host can run tasks for.

        Args:
            host_address : The host address

        Returns:
            list : The list of towers the host can run tasks for
        """
        towers = self.get_towers()
        host_towers = []
        for tower in towers:
            hosts = self.get_tower_hosts(
                tower_address=tower["owner"]
            )
            if host_address in hosts:
                host_towers.append(tower)
        return host_towers

    def get_towers_hosts_for_task(
        self,
        ipfs_sha256: str
    ) -> list:
        r"""
        Get the (tower, host) pairs with their fees and the block number
        when the results will be available for a given task.

        Args:
            ipfs_sha256 : The ipfs sha256 hash of the task

        Returns:
            list : The list of (tower, host, fee, endblock) pairs
        """
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

    def is_task_done(
        self,
        task_id: str
    ) -> bool:
        r"""
        Check if a task is done.

        Args:
            task_id : The task id

        Returns:
            bool : True if the task is done, False otherwise
        """
        running_task = self.get_running_task(
            task_id=task_id
        )
        return (
            self.w3.eth.get_block("latest")["number"] >
            (running_task["startBlock"] + running_task["blockTimeout"])
        )
