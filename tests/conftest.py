import pathlib
import json
import subprocess
import random
import web3
from eth_account import Account
import pytest
import pymeca.dao
import pymeca.host
import pymeca.tower
import pymeca.task
import pymeca.user
import pymeca.utils


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


@pytest.fixture(scope="session")
def CLEAN_PORT():
    return 8545


@pytest.fixture(scope="session")
def SIMPLE_PORT():
    return 8546


@pytest.fixture(scope="session")
def REGISTER_PORT():
    return 8547


@pytest.fixture(scope="session")
def FILL_PORT():
    return 8548


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
):
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
    while index < 100:
        try:
            web3_instance.eth.get_block("latest")
            break
        except web3.exceptions.ConnectionError:
            index += 1
            pass
        except Exception as e:
            assert False, e
    assert index < 100
    return (web3_instance, server_process)


@pytest.fixture(scope="session", autouse=True)
def clean_web3(
    accounts,
    GANAHE_SERVER_SCRIPT_PATH
):
    def _clean_web3(port: int):
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
    w3, server_process = clean_web3(CLEAN_PORT)
    yield w3
    server_process.terminate()


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
    def _simple_web3(port: int):
        w3, server_process = clean_web3(port)
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
    w3, server_process, addresses, actors = simple_web3(SIMPLE_PORT)
    yield (w3, addresses, actors)
    server_process.terminate()


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
def register_web3(
    accounts,
    simple_web3,
    initial_host,
    initial_tower,
    initial_task
):
    def _register_web3(port: int):
        w3, server_process, addresses, actors = simple_web3(port)

        actors["host"].register(
            block_timeout_limit=initial_host["blockTimeoutLimit"],
            public_key=initial_host["eccPublicKey"],
            initial_deposit=initial_host["stake"]
        )

        actors["tower"].register_tower(
            size_limit=initial_tower["sizeLimit"],
            public_connection=initial_tower["publicConnection"],
            fee=initial_tower["fee"],
            fee_type=initial_tower["feeType"],
            initial_deposit=initial_tower["stake"]
        )

        actors["task_developer"].register_task(
            ipfs_sha256=initial_task["ipfsSha256"],
            fee=initial_task["fee"],
            computing_type=initial_task["computingType"],
            size=initial_task["size"]
        )

        return (w3, server_process, addresses, actors)

    return _register_web3


@pytest.fixture(scope="class")
def register_setup(
    register_web3,
    REGISTER_PORT
):
    w3, server_process, addresses, actors = register_web3(REGISTER_PORT)
    yield (w3, addresses, actors)
    server_process.terminate()


@pytest.fixture(scope="class")
def initial_host_task(initial_task):
    return dict(
        ipfsSha256=initial_task["ipfsSha256"],
        fee=10,
        blockTimeout=7
    )


@pytest.fixture(scope="class")
def fill_web3(
    accounts,
    register_web3,
    initial_host_task
):
    def _fill_web3(port: int):
        w3, server_process, addresses, actors = register_web3(port)

        actors["host"].add_task(
            ipfs_sha256=initial_host_task["ipfsSha256"],
            block_timeout=initial_host_task["blockTimeout"],
            fee=initial_host_task["fee"]
        )

        actors["host"].register_for_tower(
            tower_address=actors["tower"].account.address
        )

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
    w3, server_process, addresses, actors = fill_web3(FILL_PORT)
    yield (w3, addresses, actors)
    server_process.terminate()
