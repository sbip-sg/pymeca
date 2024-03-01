import logging
import argparse
import json
import subprocess
import random
import web3
import pymeca.utils
import deploy


logger = logging.getLogger(__name__)


def ganache_accounts():
    # set the seed to be reproductible
    random.seed(0)
    return pymeca.utils.generate_meca_simulate_accounts()


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


def get_parser(
    DEFAULT_DAO_ADDRESS_FILE_PATH: str,
    DEFAULT_CONTRACT_NAMES: dict,
    DEFAULT_SCHEDULER_FEE: int,
    DEFAULT_HOST_REGISTER_FEE: int,
    DEFAULT_HOST_INITIAL_STAKE: int,
    DEFAULT_HOST_TASK_REGISTER_FEE: int,
    DEFAULT_HOST_FAILED_TASK_PENALTY: int,
    DEFAULT_TOWER_INITIAL_STAKE: int,
    DEFAULT_TOWER_HOST_REQUEST_FEE: int,
    DEFAULT_TOWER_FAILED_TASK_PENALTY: int,
    DEFAULT_TASK_ADDITION_FEE: int
) -> argparse.ArgumentParser:
    r"""
    Get parser
    """
    parser = argparse.ArgumentParser(
        description="Ganache server CLI starter",
        prog="ganache.py",
        allow_abbrev=True,
        add_help=True
    )
    parser.add_argument(
        "--port",
        dest="port",
        type=int,
        default=8545,
        help="Port",
        action="store"
    )
    parser.add_argument(
        "--ganache-server-script-path",
        dest="ganache_server_script_path",
        help="Ganache server script path",
        type=str,
        required=True,
        action="store"
    )
    parser.add_argument(
        "--accounts_file_path",
        dest="accounts_file_path",
        help="Accounts file path",
        type=str,
        required=True,
        action="store"
    )
    parser.add_argument(
        "--dao-address-file-path",
        dest="dao_address_file_path",
        help="Path to the file containing the DAO contract address",
        type=str,
        default=DEFAULT_DAO_ADDRESS_FILE_PATH,
        action="store"
    )

    deploy.args_add_contracts_info(
        parser=parser,
        DEFAULT_CONTRACT_NAMES=DEFAULT_CONTRACT_NAMES
    )
    deploy.args_contract_constructor(
        parser=parser,
        DEFAULT_SCHEDULER_FEE=DEFAULT_SCHEDULER_FEE,
        DEFAULT_HOST_REGISTER_FEE=DEFAULT_HOST_REGISTER_FEE,
        DEFAULT_HOST_INITIAL_STAKE=DEFAULT_HOST_INITIAL_STAKE,
        DEFAULT_HOST_TASK_REGISTER_FEE=DEFAULT_HOST_TASK_REGISTER_FEE,
        DEFAULT_HOST_FAILED_TASK_PENALTY=DEFAULT_HOST_FAILED_TASK_PENALTY,
        DEFAULT_TOWER_INITIAL_STAKE=DEFAULT_TOWER_INITIAL_STAKE,
        DEFAULT_TOWER_HOST_REQUEST_FEE=DEFAULT_TOWER_HOST_REQUEST_FEE,
        DEFAULT_TOWER_FAILED_TASK_PENALTY=DEFAULT_TOWER_FAILED_TASK_PENALTY,
        DEFAULT_TASK_ADDITION_FEE=DEFAULT_TASK_ADDITION_FEE
    )

    return parser


def get_default_parser() -> argparse.ArgumentParser:
    return get_parser(
        DEFAULT_DAO_ADDRESS_FILE_PATH=deploy.DEFAULT_DAO_ADDRESS_FILE_PATH,
        DEFAULT_CONTRACT_NAMES=deploy.DEFAULT_CONTRACT_NAMES,
        DEFAULT_SCHEDULER_FEE=deploy.DEFAULT_SCHEDULER_FEE,
        DEFAULT_HOST_REGISTER_FEE=deploy.DEFAULT_HOST_REGISTER_FEE,
        DEFAULT_HOST_INITIAL_STAKE=deploy.DEFAULT_HOST_INITIAL_STAKE,
        DEFAULT_HOST_TASK_REGISTER_FEE=deploy.DEFAULT_HOST_TASK_REGISTER_FEE,
        DEFAULT_HOST_FAILED_TASK_PENALTY=(
            deploy.DEFAULT_HOST_FAILED_TASK_PENALTY
        ),
        DEFAULT_TOWER_INITIAL_STAKE=deploy.DEFAULT_TOWER_INITIAL_STAKE,
        DEFAULT_TOWER_HOST_REQUEST_FEE=deploy.DEFAULT_TOWER_HOST_REQUEST_FEE,
        DEFAULT_TOWER_FAILED_TASK_PENALTY=(
            deploy.DEFAULT_TOWER_FAILED_TASK_PENALTY
        ),
        DEFAULT_TASK_ADDITION_FEE=deploy.DEFAULT_TASK_ADDITION_FEE
    )


def execute_action(
    args: argparse.Namespace
):
    r"""
    Execute action
    """
    logger.info("Starting the ganache server")
    accounts = ganache_accounts()
    with open(args.accounts_file_path, "w", encoding="utf-8") as f:
        json.dump(accounts, f, ensure_ascii=False, indent=4)
    args.private_key = accounts["meca_dao"]["private_key"]
    web3_instance, server_process = ganache_web3(
        accounts=accounts,
        ganache_server_script_path=args.ganache_server_script_path,
        port=args.port
    )
    logger.info("Ganache server started")
    args.endpoint_uri = "http://localhost:" + str(args.port)
    address = pymeca.dao.init_meca_envirnoment(
        endpoint_uri=args.endpoint_uri,
        private_key=args.private_key,
        dao_contract_file_path=args.dao_file_path,
        dao_contract_name=args.dao_contract_name,
        scheduler_contract_file_path=args.scheduler_file_path,
        scheduler_contract_name=args.scheduler_contract_name,
        scheduler_fee=args.scheduler_fee,
        host_contract_file_path=args.host_file_path,
        host_contract_name=args.host_contract_name,
        host_register_fee=args.host_register_fee,
        host_initial_stake=args.host_initial_stake,
        host_task_register_fee=args.host_task_register_fee,
        host_failed_task_penalty=args.host_failed_task_penalty,
        tower_contract_file_path=args.tower_file_path,
        tower_contract_name=args.tower_contract_name,
        tower_initial_stake=args.tower_initial_stake,
        tower_host_request_fee=args.tower_host_request_fee,
        tower_failed_task_penalty=args.tower_failed_task_penalty,
        task_contract_file_path=args.task_file_path,
        task_contract_name=args.task_contract_name,
        task_addition_fee=args.task_addition_fee
    )
    with open(
        args.dao_address_file_path,
        "w"
    ) as file:
        file.write(address["dao_contract_address"])
    logger.info("DAO contract address:", address["dao_contract_address"])
    logger.info("Contracts deployed")
    logger.info("Press enter to stop the server")
    input()
    server_process.terminate()
    logger.info("Ganache server stopped")


def main():
    logger.setLevel(logging.INFO)
    parser = get_default_parser()
    args = parser.parse_args()
    execute_action(args)


"""
python3 ganache.py \
--port 9000 \
--ganache-server-script-path ../../ganache/index.js \
--accounts_file_path ../../config/accounts.json \
--dao-address-file-path ../dao_contract_address.txt \
--dao-file-path ../../contracts/MecaContract.sol \
--scheduler-file-path ../../contracts/SchedulerContract.sol \
--host-file-path ../../contracts/HostContract.sol \
--task-file-path ../../contracts/TaskContract.sol \
--tower-file-path ../../contracts/TowerContract.sol \
--scheduler-fee 100 \
--host-register-fee 100 \
--host-initial-stake 100 \
--host-task-register-fee 100 \
--host-failed-task-penalty 100 \
--tower-initial-stake 100 \
--tower-host-request-fee 100 \
--tower-failed-task-penalty 100 \
--task-addition-fee 100
"""
if __name__ == "__main__":
    main()
