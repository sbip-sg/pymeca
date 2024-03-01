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
        Execute the transaction

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


def task_from_tuple(
    task_tuple: tuple
) -> dict:
    r"""
    Task from tuple

    Args:
        task_tuple : task tuple
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
    Task from tuple

    Args:
        task_tuple : task tuple
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
    Task from tuple

    Args:
        task_tuple : task tuple
    """
    return {
        "ipfsSha256": "0x" + running_task_tuple[0].hex().strip(),
        "inputHash": "0x" + running_task_tuple[1].hex().strip(),
        "size": running_task_tuple[2],
        "towerAddress": running_task_tuple[3],
        "hostAddress": running_task_tuple[4],
        "owner": running_task_tuple[5],
        "startBlock": running_task_tuple[6],
        "blockTimeout": running_task_tuple[7],
        "fee": running_task_fee_from_tuple(running_task_tuple[8])
    }


def host_from_tuple(
    host_tuple: tuple
) -> dict:
    r"""
    Host from tuple

    Args:
        host_tuple : host tuple
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
    Tower from tuple

    Args:
        tower_tuple : tower tuple
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
        Meca Active Actor

        Args:
            w3 : web3 instance
            private_key : private key
            contract_address : contract address
        """
        super().__init__(w3=w3, private_key=private_key)

        # get the dao contract
        self.dao_contract = self.w3.eth.contract(
            address=dao_contract_address,
            abi=pymeca.utils.MECA_DAO_ABI
        )

    def _bytes_from_hex(
        self,
        hex_string: str
    ) -> bytes:
        if hex_string.startswith("0x"):
            hex_string = hex_string[2:]
        return bytes.fromhex(hex_string)

    def get_scheduler_contract_address(self) -> str:
        return self.dao_contract.functions.getSchedulerContract().call()

    def get_scheduler_contract(self) -> web3.contract.Contract:
        return self.w3.eth.contract(
            address=self.get_scheduler_contract_address(),
            abi=pymeca.utils.MECA_SCHEDULER_ABI
        )

    def get_scheduler_flag(self) -> bool:
        return self.get_scheduler_contract().functions.schedulerFlag().call()

    def get_tower_contract_address(self) -> str:
        return self.get_scheduler_contract(
        ).functions.getTowerContract().call()

    def get_tower_contract(self) -> web3.contract.Contract:
        return self.w3.eth.contract(
            address=self.get_tower_contract_address(),
            abi=pymeca.utils.MECA_TOWER_ABI
        )

    def get_host_contract_address(self) -> str:
        return self.get_scheduler_contract().functions.getHostContract().call()

    def get_host_contract(self) -> web3.contract.Contract:
        return self.w3.eth.contract(
            address=self.get_host_contract_address(),
            abi=pymeca.utils.MECA_HOST_ABI
        )

    def get_task_contract_address(self) -> str:
        return self.get_scheduler_contract().functions.getTaskContract().call()

    def get_task_contract(self) -> web3.contract.Contract:
        return self.w3.eth.contract(
            address=self.get_task_contract_address(),
            abi=pymeca.utils.MECA_TASK_ABI
        )

    def get_scheduler_fee(self) -> int:
        return self.get_scheduler_contract().functions.SCHEDULER_FEE().call()

    def get_host_first_available_block(
        self,
        host_address: str
    ) -> int:
        return self.get_scheduler_contract(
        ).functions.getHostFirstAvailableBlock(
            host_address
        ).call()

    def get_tower_current_size(
        self,
        tower_address: str
    ) -> int:
        return self.get_scheduler_contract(
        ).functions.getTowerCurrentSize(
            tower_address
        ).call()

    def get_running_task(
        self,
        task_id: str
    ) -> dict:
        tuple_running_task = self.get_scheduler_contract(
        ).functions.getRunningTask(
            taskId=self._bytes_from_hex(task_id)
        ).call()
        return running_task_from_tuple(tuple_running_task)

    def get_host_register_fee(
        self
    ) -> int:
        return self.get_host_contract().functions.HOST_REGISTER_FEE().call()

    def get_host_task_register_fee(
        self
    ) -> int:
        return self.get_host_contract().functions.TASK_REGISTER_FEE().call()

    def get_host_initial_stake(
        self
    ) -> int:
        return self.get_host_contract().functions.HOST_INITIAL_STAKE().call()

    def get_host_failed_task_penalty(
        self
    ) -> int:
        return self.get_host_contract().functions.FAILED_TASK_PENALTY().call()

    def get_host_public_key(
        self,
        host_address: str
    ) -> str:
        bytes_array = self.get_host_contract().functions.getHostPublicKey(
            host_address
        ).call()
        return "0x" + "".join([
                x.hex().strip() for x in bytes_array
        ])

    def get_host_block_timeout_limit(
        self,
        host_address: str
    ) -> int:
        return self.get_host_contract().functions.getHostBlockTimeoutLimit(
            host_address
        ).call()

    def get_host_stake(
        self,
        host_address: str
    ) -> int:
        return self.get_host_contract().functions.getHostStake(
            host_address
        ).call()

    def get_hosts(
        self
    ) -> list:
        tuple_hots = self.get_host_contract().functions.getHosts().call()
        return [host_from_tuple(host) for host in tuple_hots]

    def get_host_task_block_timeout(
        self,
        host_address: str,
        ipfs_sha256: str
    ) -> int:
        return self.get_host_contract().functions.getTaskBlockTimeout(
            host_address,
            ipfs_sha256
        ).call()

    def get_host_task_fee(
        self,
        host_address: str,
        ipfs_sha256: str
    ) -> int:
        return self.get_host_contract().functions.getTaskFee(
            host_address,
            ipfs_sha256
        ).call()

    def get_host_tasks(
        self,
        host_address: str
    ) -> list:
        r"""
        Get host tasks
        """
        all_tasks = self.get_tasks()
        host_tasks = []
        for task in all_tasks:
            block_timeout = self.get_host_task_block_timeout(
                host_address, task["ipfsSha256"]
            )
            if block_timeout > 0:
                host_tasks.append(task)
        return host_tasks

    def get_tower_initial_stake(
        self
    ) -> int:
        return self.get_tower_contract().functions.TOWER_INITIAL_STAKE().call()

    def get_tower_failed_task_penalty(
        self
    ) -> int:
        return self.get_tower_contract().functions.FAILED_TASK_PENALTY().call()

    def get_tower_host_request_fee(
        self
    ) -> int:
        return self.get_tower_contract().functions.HOST_REQUEST_FEE().call()

    def get_tower_size_limit(
        self,
        tower_address: str
    ) -> int:
        return self.get_tower_contract().functions.getTowerSizeLimit(
            tower_address
        ).call()

    def get_tower_public_uri(
        self,
        tower_address: str
    ) -> str:
        return self.get_tower_contract().functions.getTowerPublicConnection(
            tower_address
        ).call()

    def get_tower_fee(
        self,
        tower_address: str,
        size: int,
        block_timeout_limit: int
    ) -> int:
        return self.get_tower_contract().functions.getTowerFee(
            tower_address,
            size,
            block_timeout_limit
        ).call()

    def get_tower_stake(
        self,
        tower_address: str
    ) -> int:
        return self.get_tower_contract().functions.getTowerStake(
            tower_address
        ).call()

    def get_tower_hosts(
        self,
        tower_address: str
    ) -> list:
        return self.get_tower_contract().functions.getTowerHosts(
            tower_address
        ).call()

    def get_tower_pending_hosts(
        self,
        tower_address: str
    ) -> list:
        return self.get_tower_contract().functions.getTowerPendingHosts(
            tower_address
        ).call()

    def get_towers(
        self
    ) -> list:
        tuple_towers = self.get_tower_contract().functions.getTowers().call()
        return [tower_from_tuple(tower) for tower in tuple_towers]

    def get_task_addition_fee(
        self
    ) -> int:
        return self.get_task_contract().functions.TASK_ADDITION_FEE().call()

    def get_task_task_fee(
        self,
        ipfs_sha256: str
    ) -> int:
        return self.get_task_contract().functions.getTaskFee(
            ipfs_sha256
        ).call()

    def get_task_task_size(
        self,
        ipfs_sha256: str
    ) -> int:
        return self.get_task_contract().functions.getTaskSize(
            ipfs_sha256
        ).call()

    def get_task_computing_type(
        self,
        ipfs_sha256: str
    ) -> int:
        return self.get_task_contract().functions.getTaskComputingType(
            ipfs_sha256
        ).call()

    def get_task_owner(
        self,
        ipfs_sha256: str
    ) -> str:
        return self.get_task_contract().functions.getTaskOwner(
            ipfs_sha256
        ).call()

    def get_tasks(
        self
    ) -> list:
        tuple_list = self.get_task_contract().functions.getTasks().call()
        return [task_from_tuple(task) for task in tuple_list]
