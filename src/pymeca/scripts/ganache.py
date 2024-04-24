r"""
The CLI script to start a ganache server with the MECA contracts deployed
and the accounts and dao contract address saved in files.


Example of use:
python3 ganache.py \
--host http://localhost \
--port 9000 \
--ganache-server-script-path ../../../meca-contracts/src/ganache/index.js \
--generate-accounts \
--accounts_file_path ../../config/accounts.json \
--dao-address-file-path ../dao_contract_address.txt \
--dao-file-path \
../../../meca-contracts/src/contracts/MecaContract.sol \
--scheduler-file-path \
../../../meca-contracts/src/contracts/SchedulerContract.sol \
--host-file-path \
../../../meca-contracts/src/contracts/HostContract.sol \
--tower-file-path \
../../../meca-contracts/src/contracts/TowerContract.sol \
--task-file-path \
../../../meca-contracts/src/contracts/TaskContract.sol \
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
import logging
import json
import subprocess
import random
import os
import web3
import argparse
import requests
import pymeca
import deploy


logger = logging.getLogger(__name__)


def ganache_accounts():
    r"""
    Generate the simulate accounts.

    Returns:
        dict : Simulate accounts.
        {
            "meca_dao": {
                "private_key": str,
                "balance": int
            },
            "meca_scheduler": {
                "private_key": str,
                "balance": int
            },
            "meca_host": {
                "private_key": str,
                "balance": int
            },
            "meca_tower": {
                "private_key": str,
                "balance": int
            },
            "meca_task_developer": {
                "private_key": str,
                "balance": int
            }
        }
    """
    # set the seed to be reproductible
    random.seed(0)
    return pymeca.utils.generate_meca_simulate_accounts()


def ganache_web3(
    accounts: dict,
    ganache_server_script_path: str,
    port: int
) -> tuple[web3.Web3, subprocess.Popen]:
    r"""
    Start the ganache server and return the web3 instance and the
    subprocess of the server handler.

    Args:
        accounts : Simulate accounts.
        ganache_server_script_path : Path to the ganache server script.
        port : Port of the server.

    Returns:
        tuple[web3.Web3, subprocess.Popen] : (web3 instance, server process)
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
    Get the CLI parser fro ganeche server starter.

    Args:
        DEFAULT_DAO_ADDRESS_FILE_PATH : Default DAO address file path.
        DEFAULT_CONTRACT_NAMES : Default contract names.
        DEFAULT_SCHEDULER_FEE : Default scheduler fee.
        DEFAULT_HOST_REGISTER_FEE : Default host register fee.
        DEFAULT_HOST_INITIAL_STAKE : Default host initial stake.
        DEFAULT_HOST_TASK_REGISTER_FEE : Default host task register fee.
        DEFAULT_HOST_FAILED_TASK_PENALTY : Default host failed task penalty.
        DEFAULT_TOWER_INITIAL_STAKE : Default tower initial stake.
        DEFAULT_TOWER_HOST_REQUEST_FEE : Default tower host request fee.
        DEFAULT_TOWER_FAILED_TASK_PENALTY : Default tower failed task penalty.
        DEFAULT_TASK_ADDITION_FEE : Default task addition fee.

    Returns:
        argparse.ArgumentParser : CLI parser.

    CLI:
        ganache.py [-h] 
            [--host HOST]
            [--port PORT]
            [--ganache-server-script-path GANACHE_SERVER_SCRIPT_PATH]
            [--generate-accounts]
            --accounts_file_path ACCOUNTS_FILE_PATH
            [--dao-address-file-path DAO_ADDRESS_FILE_PATH]
            [options]

        options:
            --dao-file-path DAO_FILE_PATH
            --dao-contract-name DAO_CONTRACT_NAME
            --scheduler-file-path SCHEDULER_FILE_PATH
            --scheduler-contract-name SCHEDULER_CONTRACT_NAME
            --scheduler-fee SCHEDULER_FEE
            --host-file-path HOST_FILE_PATH
            --host-contract-name HOST_CONTRACT_NAME
            --host-register-fee HOST_REGISTER_FEE
            --host-initial-stake HOST_INITIAL_STAKE
            --host-task-register-fee HOST_TASK_REGISTER_FEE
            --host-failed-task-penalty HOST_FAILED_TASK_PENALTY
            --tower-file-path TOWER_FILE_PATH
            --tower-contract-name TOWER_CONTRACT_NAME
            --tower-initial-stake TOWER_INITIAL_STAKE
            --tower-host-request-fee TOWER_HOST_REQUEST_FEE
            --tower-failed-task-penalty TOWER_FAILED_TASK_PENALTY
            --task-file-path TASK_FILE_PATH
            --task-contract-name TASK_CONTRACT_NAME
            --task-addition-fee TASK_ADDITION_FEE
    """
    parser = argparse.ArgumentParser(
        description="Ganache server CLI starter",
        prog="ganache.py",
        allow_abbrev=True,
        add_help=True
    )
    parser.add_argument(
        "--host",
        dest="host",
        type=str,
        default="http://localhost",
        help="Host, default http://localhost",
        action="store"
    )
    parser.add_argument(
        "--port",
        dest="port",
        type=int,
        default=8545,
        help="Port, default 8545",
        action="store"
    )
    parser.add_argument(
        "--ganache-server-script-path",
        dest="ganache_server_script_path",
        help="Ganache server script path",
        type=str,
        required=False,
        action="store"
    )
    parser.add_argument(
        "--generate-accounts",
        dest="generate_accounts",
        help="Generate accounts if argument is present",
        action="store_true"
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

    # add the contracts info paths and names
    deploy.args_add_contracts_info(
        parser=parser,
        DEFAULT_CONTRACT_NAMES=DEFAULT_CONTRACT_NAMES
    )
    # add the contracts constructor arguments
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
    r"""
    Get the default CLI parser.

    Returns:
        argparse.ArgumentParser : CLI parser.
    """
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
    Execute the action of the ganache CLI.

    Args:
        args : CLI arguments.
    """
    args.endpoint_uri = str(args.host) + ":" + str(args.port)
    
    if args.generate_accounts:
        accounts = ganache_accounts()
        config_dir = os.path.dirname(args.accounts_file_path)
        os.makedirs(
            config_dir,
            exist_ok=True
        )
        with open(args.accounts_file_path, "w", encoding="utf-8") as f:
            json.dump(accounts, f, ensure_ascii=False, indent=4)
    else:
        with open(args.accounts_file_path, "r") as f:
            accounts = json.load(f)

    if args.ganache_server_script_path:
        logger.info("Starting the ganache server")
        web3_instance, server_process = ganache_web3(
            accounts=accounts,
            ganache_server_script_path=args.ganache_server_script_path,
            port=args.port
        )
        logger.info("Ganache server started")

    args.private_key = accounts["meca_dao"]["private_key"]
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

    if args.ganache_server_script_path:
        logger.info("Press enter to stop the server")
        input()
        server_process.terminate()
        logger.info("Ganache server stopped")


def main():
    r"""
    Main function.
    """
    logger.setLevel(logging.INFO)
    parser = get_default_parser()
    args = parser.parse_args()
    execute_action(args)


if __name__ == "__main__":
    main()
