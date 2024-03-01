import pathlib
import logging
import web3
import pymeca.utils
import pymeca.pymeca

logger = logging.getLogger(__name__)

# get the current directory
CURRENT_DIR = pathlib.Path(__file__).parent.absolute()
# get the default dao address file path
DEFAULT_DAO_ADDRESS_FILE_PATH = (
    CURRENT_DIR / "dao_contract_address.txt"
).resolve()


def get_DAO_ADDRESS():
    r"""
    Get the dao contract address

    Returns:
        str : dao contract address
    """
    try:
        with open(DEFAULT_DAO_ADDRESS_FILE_PATH, "r") as f:
            return f.read().strip()
    except Exception as e:
        logger.error(e)
        return "0x" + "0" * 40


class MecaDAOOwner(pymeca.pymeca.MecaActor):
    def __init__(
        self,
        w3: web3.Web3,
        private_key: str,
        contract_address: str
    ) -> None:
        r"""
        Initialize the MecaDAO

        Args:
            w3 : web3 instance
            private_key : private key of the account
            contract_address : dao contract address
        """
        super().__init__(
            w3=w3,
            private_key=private_key
        )
        # get the contract abi
        self.contract = self.w3.eth.contract(
            address=contract_address,
            abi=pymeca.utils.MECA_DAO_ABI
        )
        # verify if the account is the owner
        if self.account.address != self.contract.functions.owner().call():
            raise pymeca.utils.MecaError(
                "The account is not the owner of the contract"
            )

    def get_scheduler_address(self) -> str:
        r"""
        Get the scheduler address.

        Returns:
            str : scheduler contract address
        """
        return self.contract.functions.getSchedulerContract(
        ).call()

    def set_scheduler(
        self,
        contract_address: str
    ) -> bool:
        r"""
        Set scheduler to the dao

        Args:
            contract_address : address of the scheduler contract

        Returns:
            bool : success status
        """
        transaction = (
            self.contract.functions.setSchedulerContract(
                newSchedulerContract=contract_address
            ).build_transaction({
                "from": self.account.address,
                "nonce": self.w3.eth.get_transaction_count(
                    self.account.address
                )
            })
        )

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1


class MecaSchedulerOwner(pymeca.pymeca.MecaActor):
    def __init__(
        self,
        w3: web3.Web3,
        private_key: str,
        contract_address: str
    ) -> None:
        r"""
        Initialize the MecaScheduler

        Args:
            w3 : web3 instance
            private_key : private key of the account
            contract_address : scheduler contract address
        """
        super().__init__(
            w3=w3,
            private_key=private_key
        )

        # get the contract abi
        self.contract = self.w3.eth.contract(
            address=contract_address,
            abi=pymeca.utils.MECA_SCHEDULER_ABI
        )
        # verify if the account is the owner
        if self.account.address != self.contract.functions.owner().call():
            raise pymeca.utils.MecaError(
                "The account is not the owner of the contract"
            )

    def clear(self) -> bool:
        r"""
        Clear the scheduler

        Returns:
            bool : success status
        """
        transaction = (
            self.contract.functions.clear().build_transaction({
                "from": self.account.address,
                "nonce": self.w3.eth.get_transaction_count(
                    self.account.address
                )
            })
        )

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def get_flag(self) -> bool:
        r"""
        Get the scheduler flag

        Returns:
            bool : scheduler flag
        """
        return self.contract.functions.schedulerFlag(
        ).call()

    def set_flag(
        self,
        flag: bool
    ) -> bool:
        r"""
        Set the scheduler flag

        Args:
            flag : scheduler flag

        Returns:
            bool : success status
        """
        transaction = (
            self.contract.functions.setSchedulerFlag(
                newSchedulerFlag=flag
            ).build_transaction({
                "from": self.account.address,
                "nonce": self.w3.eth.get_transaction_count(
                    self.account.address
                )
            })
        )

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def _set_contract(
        self,
        contract_address: str,
        contract_type: int
    ) -> bool:
        r"""
        Set a contract on the scheduler.

        Args:
            contract_address : address of the contract
            contract_type : type of the contract (0: host, 1: tower, 2: task)

        Returns:
            bool : success status
        """
        contract_functions = {
            0: self.contract.functions.setHostContract,
            1: self.contract.functions.setTowerContract,
            2: self.contract.functions.setTaskContract
        }
        if contract_type not in contract_functions:
            raise pymeca.utils.MecaError(
                f"Invalid contract type {contract_type}"
            )

        transaction = (
            contract_functions[contract_type](
                newAddress=contract_address
            ).build_transaction({
                "from": self.account.address,
                "nonce": self.w3.eth.get_transaction_count(
                    self.account.address
                )
            })
        )

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def set_host_contract(
        self,
        contract_address: str
    ) -> bool:
        r"""
        Set a new host contract for the scheduler

        Args:
            contract_address : address of the host contract

        Returns:
            bool : success status
        """
        return self._set_contract(
            contract_address=contract_address,
            contract_type=0
        )

    def set_tower_contract(
        self,
        contract_address: str
    ) -> bool:
        r"""
        Set a new tower contract for the scheduler

        Args:
            contract_address : address of the tower contract

        Returns:
            bool : success status
        """
        return self._set_contract(
            contract_address=contract_address,
            contract_type=1
        )

    def set_task_contract(
        self,
        contract_address: str
    ) -> bool:
        r"""
        Set a new task contract for the scheduler

        Args:
            contract_address : address of the task contract

        Returns:
            bool : success status
        """
        return self._set_contract(
            contract_address=contract_address,
            contract_type=2
        )

    def _get_contract_address(
        self,
        contract_type: int
    ) -> str:
        r"""
        Get the contract address of one of the contracts
        from the scheduler.

        Args:
            contract_type : type of the contract (0: host, 1: tower, 2: task)

        Returns:
            str : contract address
        """
        contract_functions = {
            0: self.contract.functions.getHostContract,
            1: self.contract.functions.getTowerContract,
            2: self.contract.functions.getTaskContract
        }
        if contract_type not in contract_functions:
            raise pymeca.utils.MecaError(
                f"Invalid contract type {contract_type}"
            )
        return contract_functions[contract_type]().call()

    def get_host_contract_address(self) -> str:
        r"""
        Get the host contract address

        Returns:
            str : host contract address
        """
        return self._get_contract_address(0)

    def get_tower_contract_address(self) -> str:
        r"""
        Get the tower contract address

        Returns:
            str : tower contract address
        """
        return self._get_contract_address(1)

    def get_task_contract_address(self) -> str:
        r"""
        Get the task contract address

        Returns:
            str : task contract address
        """
        return self._get_contract_address(2)


class MecaTowerContractOwner(pymeca.pymeca.MecaActor):
    def __init__(
        self,
        w3: web3.Web3,
        private_key: str,
        contract_address: str
    ) -> None:
        r"""
        Initialize the MecaTowerContract

        Args:
            w3 : web3 instance
            private_key : private key of the account
            contract_address : tower contract address
        """
        super().__init__(
            w3=w3,
            private_key=private_key
        )

        # get the contract abi
        self.contract = self.w3.eth.contract(
            address=contract_address,
            abi=pymeca.utils.MECA_TOWER_ABI
        )
        # verify if the account is the owner
        if self.account.address != self.contract.functions.owner().call():
            raise pymeca.utils.MecaError(
                "The account is not the owner of the contract"
            )

    def get_scheduler_address(self) -> str:
        r"""
        Get the scheduler address

        Returns:
            str : scheduler contract address
        """
        return self.contract.functions.schedulerContractAddress(
        ).call()

    def set_scheduler(
        self,
        contract_address: str
    ) -> bool:
        r"""
        Set a new scheduler contract for the tower.

        Args:
            contract_address : address of the scheduler contract

        Returns:
            bool : success status
        """
        transaction = (
            self.contract.functions.setSchedulerContractAddress(
                newSchedulerContractAddress=contract_address
            ).build_transaction({
                "from": self.account.address,
                "nonce": self.w3.eth.get_transaction_count(
                    self.account.address
                )
            })
        )

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def clear(self) -> bool:
        r"""
        Clear the tower contract

        Returns:
            bool : success status
        """
        transaction = (
            self.contract.functions.clear().build_transaction({
                "from": self.account.address,
                "nonce": self.w3.eth.get_transaction_count(
                    self.account.address
                )
            })
        )

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1


class MecaHostContractOwner(pymeca.pymeca.MecaActor):
    def __init__(
        self,
        w3: web3.Web3,
        private_key: str,
        contract_address: str
    ) -> None:
        r"""
        Initialize the MecaHostContract

        Args:
            w3 : web3 instance
            private_key : private key of the account
            contract_address : host contract address
        """
        super().__init__(
            w3=w3,
            private_key=private_key
        )

        # get the contract abi
        self.contract = self.w3.eth.contract(
            address=contract_address,
            abi=pymeca.utils.MECA_HOST_ABI
        )
        # verify if the account is the owner
        if self.account.address != self.contract.functions.owner().call():
            raise pymeca.utils.MecaError(
                "The account is not the owner of the contract"
            )

    def get_scheduler_address(self) -> str:
        r"""
        Get the scheduler address

        Returns:
            str : scheduler contract address
        """
        return self.contract.functions.schedulerContractAddress(
        ).call()

    def set_scheduler(
        self,
        contract_address: str
    ) -> bool:
        r"""
        Set a new scheduler contract for the host.

        Args:
            contract_address : address of the scheduler contract

        Returns:
            bool : success status
        """
        transaction = (
            self.contract.functions.setSchedulerContractAddress(
                newSchedulerContractAddress=contract_address
            ).build_transaction({
                "from": self.account.address,
                "nonce": self.w3.eth.get_transaction_count(
                    self.account.address
                )
            })
        )

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def clear(self) -> bool:
        r"""
        Clear the host contract

        Returns:
            bool : success status
        """
        transaction = (
            self.contract.functions.clear().build_transaction({
                "from": self.account.address,
                "nonce": self.w3.eth.get_transaction_count(
                    self.account.address
                )
            })
        )

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1


class MecaTaskContractOwner(pymeca.pymeca.MecaActor):
    def __init__(
        self,
        w3: web3.Web3,
        private_key: str,
        contract_address: str
    ) -> None:
        r"""
        Initialize the MecaTaskContract

        Args:
            w3 : web3 instance
            private_key : private key of the account
            contract_address : task contract address
        """
        super().__init__(
            w3=w3,
            private_key=private_key
        )

        # get the contract abi
        self.contract = self.w3.eth.contract(
            address=contract_address,
            abi=pymeca.utils.MECA_TASK_ABI
        )
        # verify if the account is the owner
        if self.account.address != self.contract.functions.owner().call():
            raise pymeca.utils.MecaError(
                "The account is not the owner of the contract"
            )

    def clear(self) -> bool:
        r"""
        Clear the task contract

        Returns:
            bool : success status
        """
        transaction = (
            self.contract.functions.clear().build_transaction({
                "from": self.account.address,
                "nonce": self.w3.eth.get_transaction_count(
                    self.account.address
                )
            })
        )

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1


def init_meca_envirnoment(
    endpoint_uri: str,
    private_key: str,
    dao_contract_file_path: str,
    dao_contract_name: str,
    scheduler_contract_file_path: str,
    scheduler_contract_name: str,
    scheduler_fee: int,
    host_contract_file_path: str,
    host_contract_name: str,
    host_register_fee: int,
    host_initial_stake: int,
    host_task_register_fee: int,
    host_failed_task_penalty: int,
    tower_contract_file_path: str,
    tower_contract_name: str,
    tower_initial_stake: int,
    tower_host_request_fee: int,
    tower_failed_task_penalty: int,
    task_contract_file_path: str,
    task_contract_name: str,
    task_addition_fee: int
) -> dict:
    r"""
    Initialize the MECA ecosystem by deploying the contracts
    and connecting them.

    Args:
        endpoint_uri : blockchain endpoint uri
        private_key : private key of the account
        dao_contract_file_path : dao contract file path
        dao_contract_name : dao contract name
        scheduler_contract_file_path : scheduler contract file path
        scheduler_contract_name : scheduler contract name
        scheduler_fee : scheduler fee
        host_contract_file_path : host contract file path
        host_contract_name : host contract name
        host_register_fee : host register fee
        host_initial_stake : host initial stake
        host_task_register_fee : host task register fee
        host_failed_task_penalty : host failed task penalty
        tower_contract_file_path : tower contract file path
        tower_contract_name : tower contract name
        tower_initial_stake : tower initial stake
        tower_host_request_fee : tower host request fee
        tower_failed_task_penalty : tower failed task penalty
        task_contract_file_path : task contract file path
        task_contract_name : task contract name
        task_addition_fee : task addition fee

    Returns:
        dict : addresses of the contracts
    """
    # initialize the web3 instance
    w3 = web3.Web3(web3.HTTPProvider(endpoint_uri))
    if not w3.is_connected():
        raise pymeca.utils.MecaError("Blockchain endpoint is not connected")

    logger.info("Blockchain endpoint is connected")

    logger.info("Adding contracts to the blockchain")
    logger.debug(f"""DAO Contract {dao_contract_name} :
                 {dao_contract_file_path}""")
    logger.debug(f"""Scheduler Contract {scheduler_contract_name} :
                 {scheduler_contract_file_path}""")
    logger.debug(f"""Host Contract {host_contract_name} :
                 {host_contract_file_path}""")
    logger.debug(f"""Tower Contract {tower_contract_name} :
                 {tower_contract_file_path}""")
    logger.debug(f"""Task Contract {task_contract_name} :
                 {task_contract_file_path}""")

    dao_contract_address = pymeca.utils.deploy_contract(
        w3=w3,
        private_key=private_key,
        contract_file_path=dao_contract_file_path,
        contract_name=dao_contract_name
    )

    logger.debug(f"DAO Contract Address : {dao_contract_address}")

    scheduler_contract_address = pymeca.utils.deploy_contract(
        w3=w3,
        private_key=private_key,
        contract_file_path=scheduler_contract_file_path,
        contract_name=scheduler_contract_name,
        schedulerFee=scheduler_fee
    )

    logger.debug(f"Scheduler Contract Address : {scheduler_contract_address}")

    host_contract_address = pymeca.utils.deploy_contract(
        w3=w3,
        private_key=private_key,
        contract_file_path=host_contract_file_path,
        contract_name=host_contract_name,
        hostRegisterFee=host_register_fee,
        hostInitialStake=host_initial_stake,
        failedTaskPenalty=host_failed_task_penalty,
        taskRegisterFee=host_task_register_fee
    )

    logger.debug(f"Host Contract Address : {host_contract_address}")

    tower_contract_address = pymeca.utils.deploy_contract(
        w3=w3,
        private_key=private_key,
        contract_file_path=tower_contract_file_path,
        contract_name=tower_contract_name,
        towerInitialStake=tower_initial_stake,
        hostRequestFee=tower_host_request_fee,
        failedTaskPenalty=tower_failed_task_penalty
    )

    logger.debug(f"Tower Contract Address : {tower_contract_address}")

    task_contract_address = pymeca.utils.deploy_contract(
        w3=w3,
        private_key=private_key,
        contract_file_path=task_contract_file_path,
        contract_name=task_contract_name,
        taskAdditionFee=task_addition_fee
    )

    logger.debug(f"Task Contract Address : {task_contract_address}")

    # set the class for every contract
    meca_dao_owner = MecaDAOOwner(
        w3=w3,
        private_key=private_key,
        contract_address=dao_contract_address
    )
    meca_scheduler_owner = MecaSchedulerOwner(
        w3=w3,
        private_key=private_key,
        contract_address=scheduler_contract_address
    )
    meca_host_owner = MecaHostContractOwner(
        w3=w3,
        private_key=private_key,
        contract_address=host_contract_address
    )
    meca_tower_owner = MecaTowerContractOwner(
        w3=w3,
        private_key=private_key,
        contract_address=tower_contract_address
    )

    logger.info("Made the contracts owner instances")

    # set the scheduler to the dao
    meca_dao_owner.set_scheduler(scheduler_contract_address)

    # set the scheduler to the host
    meca_host_owner.set_scheduler(scheduler_contract_address)

    # set the scheduler to the tower
    meca_tower_owner.set_scheduler(scheduler_contract_address)

    # set the task to the scheduler
    meca_scheduler_owner.set_task_contract(task_contract_address)

    # set the host to the scheduler
    meca_scheduler_owner.set_host_contract(host_contract_address)

    # set the tower to the scheduler
    meca_scheduler_owner.set_tower_contract(tower_contract_address)

    # set the scheduler flag
    meca_scheduler_owner.set_flag(True)

    # save the addresses to the file
    addresses = {
        "dao_contract_address": dao_contract_address,
        "scheduler_contract_address": scheduler_contract_address,
        "host_contract_address": host_contract_address,
        "tower_contract_address": tower_contract_address,
        "task_contract_address": task_contract_address
    }

    return addresses
