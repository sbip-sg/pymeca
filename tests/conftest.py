import pathlib
import json
import subprocess
import random
import requests
import web3
from eth_account import Account
import pytest
import pymeca.dao
import pymeca.host
import pymeca.tower
import pymeca.task
import pymeca.user
import pymeca.utils


# accounts with initial balance
@pytest.fixture(scope="session")
def INITIAL_BALANCE():
    return 1000


@pytest.fixture(scope="session")
def accounts(
    INITIAL_BALANCE
):
    # set the seed to be reproductible
    random.seed(0)
    return pymeca.utils.generate_meca_simulate_accounts(
        initial_balance=INITIAL_BALANCE
    )


# constrctor contracts default values
@pytest.fixture(scope="session")
def SCHEDULER_FEE():
    return 10


@pytest.fixture(scope="session")
def HOST_REGISTER_FEE():
    return 10


@pytest.fixture(scope="session")
def HOST_INITIAL_STAKE():
    return 100


@pytest.fixture(scope="session")
def HOST_FAILED_TASK_PENALTY():
    return 8


@pytest.fixture(scope="session")
def HOST_TASK_REGISTER_FEE():
    return 5


@pytest.fixture(scope="session")
def TOWER_INITIAL_STAKE():
    return 100


@pytest.fixture(scope="session")
def TOWER_HOST_REQUEST_FEE():
    return 10


@pytest.fixture(scope="session")
def TOWER_FAILED_TASK_PENALTY():
    return 8


@pytest.fixture(scope="session")
def TASK_ADDITION_FEE():
    return 5


# ports of the ganache servers with different setups of
# the blockchain environment and meca actors and contracts
@pytest.fixture(scope="session")
def CLEAN_PORT():
    return 8546


@pytest.fixture(scope="session")
def SIMPLE_PORT():
    return 8547


@pytest.fixture(scope="session")
def REGISTER_PORT():
    return 8548


@pytest.fixture(scope="session")
def FILL_PORT():
    return 8549


# the ganache script path
@pytest.fixture(scope="session")
def GANAHE_SERVER_SCRIPT_PATH():
    tests_dir = pathlib.Path(__file__).absolute().parent
    return (
        tests_dir.parent /
        "meca-contracts" /
        "src" /
        "ganache" /
        'index.js'
    ).resolve()


def ganache_web3(
    accounts: dict,
    ganache_server_script_path: str,
    port: int
) -> tuple[web3.Web3, subprocess.Popen]:
    r"""
    Start a ganache server and return a web3 instance.

    Args:
        accounts : Accounts with initial balance.
        ganache_server_script_path : Ganache server script path.
        port : Port of the ganache server.

    Returns:
        tuple[web3.Web3, subprocess.Popen] : (web3_instance, server_process)
    """
    # start the ganache server
    server_process = subprocess.Popen(
        [
            "node",
            ganache_server_script_path,
            str(port),
            json.dumps(accounts)
        ]
    )
    endpoint_uri = "http://localhost:" + str(port)
    # wait for the server to start
    web3_instance = web3.Web3(web3.Web3.HTTPProvider(endpoint_uri))
    index: int = 0
    while index < 5:
        try:
            web3_instance.eth.get_block("latest")
            break
        except requests.exceptions.ConnectionError:
            index += 1
            pass
        except Exception as e:
            assert False, e
    assert index < 5
    return (web3_instance, server_process)


@pytest.fixture(scope="session", autouse=True)
def clean_web3(
    accounts,
    GANAHE_SERVER_SCRIPT_PATH
):
    r"""
    Return a function to start a clean web3 instance for the
    accounts definied. The clean web has only the accounts
    with the initial balance.
    """
    def _clean_web3(port: int) -> tuple[web3.Web3, subprocess.Popen]:
        r"""
        Start a ganaches server with the accounts definied
        on the given port. The blockchain environment does
        not have any contract and the accounts have the initial balance.

        Args:
            port : Port of the ganache server.

        Returns:
            tuple[web3.Web3, subprocess.Popen] :
                (web3_instance, server_process)
        """
        web3_instance, server_process = ganache_web3(
            accounts,
            GANAHE_SERVER_SCRIPT_PATH,
            port
        )
        return (web3_instance, server_process)

    return _clean_web3


@pytest.fixture(scope="class")
def clean_setup(
    clean_web3,
    CLEAN_PORT
):
    r"""
    Return a clean web3 instance for the accounts definied on
    the given port. The blockchain environment does not have
    any contract and the accounts have the initial balance.
    """
    w3, server_process = clean_web3(CLEAN_PORT)
    yield w3
    server_process.terminate()


# contracts directory and default contract file names
@pytest.fixture(scope="session")
def CONTRACTS_DIRECTORY():
    return (
        pathlib.Path(__file__).absolute().parent.parent /
        "meca-contracts" /
        "src" /
        "contracts"
    ).resolve()


@pytest.fixture(scope="session")
def DEFAULT_CONTRACT_FILE_NAMES():
    return {
        "dao": "MecaContract.sol",
        "scheduler": "SchedulerContract.sol",
        "host": "HostContract.sol",
        "task": "TaskContract.sol",
        "tower": "TowerContract.sol"
    }


@pytest.fixture(scope="session")
def DEFAULT_CONTRACT_NAMES():
    return {
        "dao": "MecaDaoContract",
        "scheduler": "MecaSchedulerContract",
        "host": "MecaHostContract",
        "tower": "MecaTowerContract",
        "task": "MecaTaskContract"
    }


@pytest.fixture(scope="session", autouse=True)
def simple_web3(
    accounts,
    clean_web3,
    SCHEDULER_FEE,
    HOST_REGISTER_FEE,
    HOST_INITIAL_STAKE,
    HOST_FAILED_TASK_PENALTY,
    HOST_TASK_REGISTER_FEE,
    TOWER_INITIAL_STAKE,
    TOWER_HOST_REQUEST_FEE,
    TOWER_FAILED_TASK_PENALTY,
    TASK_ADDITION_FEE,
    CONTRACTS_DIRECTORY,
    DEFAULT_CONTRACT_FILE_NAMES,
    DEFAULT_CONTRACT_NAMES
):
    r"""
    Return a function to start a simple web3 instance for the
    accounts definied on the given port. The blockchain environment
    has the meca contracts and the actors are initialized.

    Args:
        accounts : Accounts with initial balance.
        clean_web3 : Clean web3 instance.
        SCHEDULER_FEE : Scheduler fee.
        HOST_REGISTER_FEE : Host register fee.
        HOST_INITIAL_STAKE : Host initial stake.
        HOST_FAILED_TASK_PENALTY : Host failed task penalty.
        HOST_TASK_REGISTER_FEE : Host task register fee.
        TOWER_INITIAL_STAKE : Tower initial stake.
        TOWER_HOST_REQUEST_FEE : Tower host request fee.
        TOWER_FAILED_TASK_PENALTY : Tower failed task penalty.
        TASK_ADDITION_FEE : Task addition fee.
        CONTRACTS_DIRECTORY : Contracts directory.
        DEFAULT_CONTRACT_FILE_NAMES : Default contract file names.
        DEFAULT_CONTRACT_NAMES : Default contract names.

    Returns:
        function : Simple web3 instance.
    """
    def _simple_web3(
        port: int
    ) -> tuple[web3.Web3, subprocess.Popen, dict, dict]:
        r"""
        Start a blockchain environment with ganache
        for the accounts definied on
        the given port. The blockchain environment has the meca
        contracts and the actors are initialized.

        Args:
            port : Port of the ganache server.

        Returns:
            tuple[web3.Web3, subprocess.Popen, dict, dict] :
                (web3_instance, server_process, addresses, actors)
            web3_instance : Web3 instance.
            server_process : Ganache server process.
            addresses : Addresses of the contracts.
            actors : Meca actors.
        """
        w3, server_process = clean_web3(port)
        # deploy the contracts
        addresses = pymeca.dao.init_meca_envirnoment(
            endpoint_uri="http://localhost:" + str(port),
            private_key=accounts["meca_dao"]["private_key"],
            dao_contract_file_path=str(
                CONTRACTS_DIRECTORY /
                DEFAULT_CONTRACT_FILE_NAMES["dao"]
            ),
            dao_contract_name=DEFAULT_CONTRACT_NAMES["dao"],
            scheduler_contract_file_path=str(
                CONTRACTS_DIRECTORY /
                DEFAULT_CONTRACT_FILE_NAMES["scheduler"]
            ),
            scheduler_contract_name=DEFAULT_CONTRACT_NAMES["scheduler"],
            scheduler_fee=SCHEDULER_FEE,
            host_contract_file_path=str(
                CONTRACTS_DIRECTORY /
                DEFAULT_CONTRACT_FILE_NAMES["host"]
            ),
            host_contract_name=DEFAULT_CONTRACT_NAMES["host"],
            host_register_fee=HOST_REGISTER_FEE,
            host_initial_stake=HOST_INITIAL_STAKE,
            host_failed_task_penalty=HOST_FAILED_TASK_PENALTY,
            host_task_register_fee=HOST_TASK_REGISTER_FEE,
            tower_contract_file_path=str(
                CONTRACTS_DIRECTORY /
                DEFAULT_CONTRACT_FILE_NAMES["tower"]
            ),
            tower_contract_name=DEFAULT_CONTRACT_NAMES["tower"],
            tower_initial_stake=TOWER_INITIAL_STAKE,
            tower_host_request_fee=TOWER_HOST_REQUEST_FEE,
            tower_failed_task_penalty=TOWER_FAILED_TASK_PENALTY,
            task_contract_file_path=str(
                CONTRACTS_DIRECTORY /
                DEFAULT_CONTRACT_FILE_NAMES["task"]
            ),
            task_contract_name=DEFAULT_CONTRACT_NAMES["task"],
            task_addition_fee=TASK_ADDITION_FEE
        )
        # init the actors
        meca_user = pymeca.user.MecaUser(
            w3=w3,
            private_key=accounts["meca_user"]["private_key"],
            dao_contract_address=addresses["dao_contract_address"]
        )
        meca_host = pymeca.host.MecaHost(
            w3=w3,
            private_key=accounts["meca_host"]["private_key"],
            dao_contract_address=addresses["dao_contract_address"]
        )
        meca_tower = pymeca.tower.MecaTower(
            w3=w3,
            private_key=accounts["meca_tower"]["private_key"],
            dao_contract_address=addresses["dao_contract_address"]
        )
        meca_task_developer = pymeca.task.MecaTaskDeveloper(
            w3=w3,
            private_key=accounts["meca_task"]["private_key"],
            dao_contract_address=addresses["dao_contract_address"]
        )
        actors = dict(
            user=meca_user,
            host=meca_host,
            tower=meca_tower,
            task_developer=meca_task_developer
        )

        return (w3, server_process, addresses, actors)

    return _simple_web3


@pytest.fixture(scope="class")
def simple_setup(
    simple_web3,
    SIMPLE_PORT
):
    r"""
    Creates simple setup for the blockchain environment
    for the accounts definied on he given port. The blockchain
    environment has the meca contracts and the actors are initialized.
    """
    w3, server_process, addresses, actors = simple_web3(SIMPLE_PORT)
    yield (w3, addresses, actors)
    server_process.terminate()


# initial values for the actors when they are registered
# on the blockchain and interact with meca ecosystem
@pytest.fixture(scope="session")
def initial_tower(accounts):
    return dict(
        owner=Account.from_key(
            accounts["meca_tower"]["private_key"]
        ).address,
        sizeLimit=10000,
        publicConnection="htpp://localhost:8080",
        feeType=0,
        fee=10,
        stake=300
    )


@pytest.fixture(scope="session")
def initial_host(accounts):
    return dict(
        owner=Account.from_key(
            accounts["meca_host"]["private_key"]
        ).address,
        eccPublicKey="0x" + "2" * 128,
        blockTimeoutLimit=30,
        stake=300
    )


@pytest.fixture(scope="session")
def initial_task(accounts):
    return dict(
        ipfsSha256="0x" + "1" * 64,
        owner=Account.from_key(
            accounts["meca_task"]["private_key"]
        ).address,
        fee=10,
        computingType=0,
        size=1024,
    )


@pytest.fixture(scope="session")
def initial_tee_task(accounts):
    return dict(
        ipfsSha256="0x" + "2" * 64,
        owner=Account.from_key(
            accounts["meca_task"]["private_key"]
        ).address,
        fee=10,
        computingType=2,
        size=1024,
        initialInputHash="0x" + "3" * 64,
        encryptedInputHash="0x" + "4" * 64,
    )


@pytest.fixture(scope="session")
def register_web3(
    simple_web3,
    initial_host,
    initial_tower,
    initial_task,
    initial_tee_task
):
    r"""
    Return a function to start a register web3 instance for the
    accounts definied on the given port. The blockchain environment
    has the meca contracts and the actors are initialized. Also, the
    actors are registered on the blockchain and interact with meca ecosystem.
    """
    def _register_web3(
        port: int
    ) -> tuple[web3.Web3, subprocess.Popen, dict, dict]:
        r"""
        Start a blockchain environment with ganache
        for the accounts definied on
        the given port. The blockchain environment has the meca
        contracts and the actors are initialized.

        Args:
            port : Port of the ganache server.

        Returns:
            tuple[web3.Web3, subprocess.Popen, dict, dict] :
                (web3_instance, server_process, addresses, actors)
            web3_instance : Web3 instance.
            server_process : Ganache server process.
            addresses : Addresses of the contracts.
            actors : Meca actors.
        """
        w3, server_process, addresses, actors = simple_web3(port)
        # register the host
        actors["host"].register(
            block_timeout_limit=initial_host["blockTimeoutLimit"],
            public_key=initial_host["eccPublicKey"],
            initial_deposit=initial_host["stake"]
        )
        # register the tower
        actors["tower"].register_tower(
            size_limit=initial_tower["sizeLimit"],
            public_connection=initial_tower["publicConnection"],
            fee=initial_tower["fee"],
            fee_type=initial_tower["feeType"],
            initial_deposit=initial_tower["stake"]
        )
        # register the task
        actors["task_developer"].register_task(
            ipfs_sha256=initial_task["ipfsSha256"],
            fee=initial_task["fee"],
            computing_type=initial_task["computingType"],
            size=initial_task["size"]
        )
        # register the tee task
        actors["task_developer"].register_task(
            ipfs_sha256=initial_tee_task["ipfsSha256"],
            fee=initial_tee_task["fee"],
            computing_type=initial_tee_task["computingType"],
            size=initial_tee_task["size"]
        )

        return (w3, server_process, addresses, actors)

    return _register_web3


@pytest.fixture(scope="class")
def register_setup(
    register_web3,
    REGISTER_PORT
):
    r"""
    Creates setup for the blockchain environment
    for the accounts definied on he given port. The blockchain
    environment has the meca contracts and the actors are initialized.
    The host register itself on the host contract.
    The tower register itself on the tower contract.
    The task developer register the task on the task contract.
    """
    w3, server_process, addresses, actors = register_web3(REGISTER_PORT)
    yield (w3, addresses, actors)
    server_process.terminate()


# the initial task for the host
@pytest.fixture(scope="class")
def initial_host_task(initial_task):
    return dict(
        ipfsSha256=initial_task["ipfsSha256"],
        fee=10,
        blockTimeout=1
    )


# the initial tee task for the host
@pytest.fixture(scope="class")
def initial_host_tee_task(initial_tee_task):
    return dict(
        ipfsSha256=initial_tee_task["ipfsSha256"],
        fee=10,
        blockTimeout=3,
    )


@pytest.fixture(scope="class")
def fill_web3(
    register_web3,
    initial_host_task,
    initial_host_tee_task
):
    r"""
    Using the register environment it creates a flow for running a
    task on the blockchain. The host register the task for itself on
    the host contract. The host request to be registered on the tower
    list. The tower accept the host.
    """
    def _fill_web3(
        port: int
    ) -> tuple[web3.Web3, subprocess.Popen, dict, dict]:
        r"""
        Start a blockchain environment with ganache
        for the accounts definied on
        the given port. The blockchain environment has a functional
        task flow.

        Args:
            port : Port of the ganache server.

        Returns:
            tuple[web3.Web3, subprocess.Popen, dict, dict] :
                (web3_instance, server_process, addresses, actors)
            web3_instance : Web3 instance.
            server_process : Ganache server process.
            addresses : Addresses of the contracts.
            actors : Meca actors.
        """
        w3, server_process, addresses, actors = register_web3(port)
        # the host add the task
        actors["host"].add_task(
            ipfs_sha256=initial_host_task["ipfsSha256"],
            block_timeout=initial_host_task["blockTimeout"],
            fee=initial_host_task["fee"]
        )
        # the host add the tee task
        actors["host"].add_task(
            ipfs_sha256=initial_host_tee_task["ipfsSha256"],
            block_timeout=initial_host_tee_task["blockTimeout"],
            fee=initial_host_tee_task["fee"]
        )
        # the host request to ge tin the tower list
        actors["host"].register_for_tower(
            tower_address=actors["tower"].account.address
        )
        # the tower accepts the host
        actors["tower"].accept_host(
            host_address=actors["host"].account.address
        )

        return (w3, server_process, addresses, actors)

    return _fill_web3


@pytest.fixture(scope="class")
def fill_setup(
    fill_web3,
    FILL_PORT
):
    r"""
    Creates setup for the blockchain environment
    for the accounts definied on he given port. The blockchain
    environment has a functional task flow.
    """
    w3, server_process, addresses, actors = fill_web3(FILL_PORT)
    yield (w3, addresses, actors)
    server_process.terminate()
