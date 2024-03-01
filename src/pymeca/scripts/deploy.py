import logging
import pymeca.utils
import argparse
import pymeca.dao
import web3

logger = logging.getLogger(__name__)


DEFAULT_CONTRACT_NAMES = {
    "dao": "MecaDaoContract",
    "scheduler": "MecaSchedulerContract",
    "host": "MecaHostContract",
    "tower": "MecaTowerContract",
    "task": "MecaTaskContract"
}
DEFAULT_DAO_ADDRESS_FILE_PATH = str(pymeca.dao.DEFAULT_DAO_ADDRESS_FILE_PATH)
DEFAULT_SCHEDULER_FEE = 10
DEFAULT_HOST_REGISTER_FEE = 10
DEFAULT_HOST_INITIAL_STAKE = 100
DEFAULT_HOST_TASK_REGISTER_FEE = 5
DEFAULT_HOST_FAILED_TASK_PENALTY = 8
DEFAULT_TOWER_INITIAL_STAKE = 100
DEFAULT_TOWER_HOST_REQUEST_FEE = 10
DEFAULT_TOWER_FAILED_TASK_PENALTY = 8
DEFAULT_TASK_ADDITION_FEE = 5


def args_add_contracts_info(
    parser: argparse.ArgumentParser,
    DEFAULT_CONTRACT_NAMES: dict
) -> None:
    parser.add_argument(
        "--dao-file-path",
        dest="dao_file_path",
        help="The dao contract file path",
        type=str,
        required=True,
        action="store"
    )
    parser.add_argument(
        "--dao-contract-name",
        dest="dao_contract_name",
        help="The dao contract name",
        type=str,
        default=DEFAULT_CONTRACT_NAMES["dao"],
        action="store"
    )
    parser.add_argument(
        "--scheduler-file-path",
        dest="scheduler_file_path",
        help="The scheduler contract file path",
        type=str,
        required=True,
        action="store"
    )
    parser.add_argument(
        "--scheduler-contract-name",
        dest="scheduler_contract_name",
        help="The scheduler contract name",
        type=str,
        default=DEFAULT_CONTRACT_NAMES["scheduler"],
        action="store"
    )
    parser.add_argument(
        "--host-file-path",
        dest="host_file_path",
        help="The host contract file path",
        type=str,
        required=True,
        action="store"
    )
    parser.add_argument(
        "--host-contract-name",
        dest="host_contract_name",
        help="The host contract name",
        type=str,
        default=DEFAULT_CONTRACT_NAMES["host"],
        action="store"
    )
    parser.add_argument(
        "--tower-file-path",
        dest="tower_file_path",
        help="The tower contract file path",
        type=str,
        required=True,
        action="store"
    )
    parser.add_argument(
        "--tower-contract-name",
        dest="tower_contract_name",
        help="The tower contract name",
        type=str,
        default=DEFAULT_CONTRACT_NAMES["tower"],
        action="store"
    )
    parser.add_argument(
        "--task-file-path",
        dest="task_file_path",
        help="The task contract file path",
        type=str,
        required=True,
        action="store"
    )
    parser.add_argument(
        "--task-contract-name",
        dest="task_contract_name",
        help="The task contract name",
        type=str,
        default=DEFAULT_CONTRACT_NAMES["task"],
        action="store"
    )


def args_contract_constructor(
    parser: argparse.ArgumentParser,
    DEFAULT_SCHEDULER_FEE: int,
    DEFAULT_HOST_REGISTER_FEE: int,
    DEFAULT_HOST_INITIAL_STAKE: int,
    DEFAULT_HOST_TASK_REGISTER_FEE: int,
    DEFAULT_HOST_FAILED_TASK_PENALTY: int,
    DEFAULT_TOWER_INITIAL_STAKE: int,
    DEFAULT_TOWER_HOST_REQUEST_FEE: int,
    DEFAULT_TOWER_FAILED_TASK_PENALTY: int,
    DEFAULT_TASK_ADDITION_FEE: int
) -> None:
    parser.add_argument(
        "--scheduler-fee",
        dest="scheduler_fee",
        help="The scheduler fee",
        type=int,
        default=DEFAULT_SCHEDULER_FEE,
        action="store"
    )
    parser.add_argument(
        "--host-register-fee",
        dest="host_register_fee",
        help="The host register fee",
        type=int,
        default=DEFAULT_HOST_REGISTER_FEE,
        action="store"
    )
    parser.add_argument(
        "--host-initial-stake",
        dest="host_initial_stake",
        help="The host initial stake",
        type=int,
        default=DEFAULT_HOST_INITIAL_STAKE,
        action="store"
    )
    parser.add_argument(
        "--host-task-register-fee",
        dest="host_task_register_fee",
        help="The host task register fee",
        type=int,
        default=DEFAULT_HOST_TASK_REGISTER_FEE,
        action="store"
    )
    parser.add_argument(
        "--host-failed-task-penalty",
        dest="host_failed_task_penalty",
        help="The host failed task penalty",
        type=int,
        default=DEFAULT_HOST_FAILED_TASK_PENALTY,
        action="store"
    )
    parser.add_argument(
        "--tower-initial-stake",
        dest="tower_initial_stake",
        help="The tower initial stake",
        type=int,
        default=DEFAULT_TOWER_INITIAL_STAKE,
        action="store"
    )
    parser.add_argument(
        "--tower-host-request-fee",
        dest="tower_host_request_fee",
        help="The tower host request fee",
        type=int,
        default=DEFAULT_TOWER_HOST_REQUEST_FEE,
        action="store"
    )
    parser.add_argument(
        "--tower-failed-task-penalty",
        dest="tower_failed_task_penalty",
        help="The tower failed task penalty",
        type=int,
        default=DEFAULT_TOWER_FAILED_TASK_PENALTY,
        action="store"
    )
    parser.add_argument(
        "--task-addition-fee",
        dest="task_addition_fee",
        help="The task addition fee",
        type=int,
        default=DEFAULT_TASK_ADDITION_FEE,
        action="store"
    )


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
        prog="deploy.py",
        description="Compile ABI CLI for the MECA contracts",
        allow_abbrev=True,
        add_help=True
    )

    # make the parser
    # destination abi directory
    parser.add_argument(
        "--dao-address-file-path",
        dest="dao_address_file_path",
        help="Path to the file containing the DAO contract address",
        type=str,
        default=DEFAULT_DAO_ADDRESS_FILE_PATH,
        action="store"
    )
    parser.add_argument(
        "--endpoint-uri",
        dest="endpoint_uri",
        help="The endpoint URI",
        type=str,
        required=True,
        action="store"
    )
    parser.add_argument(
        "--private-key",
        dest="private_key",
        help="The private key",
        type=str,
        required=True,
        action="store"
    )
    action_subparsers = parser.add_subparsers(
        title="actions",
        description="Actions to perform",
        help="Actions to perform",
        dest="action",
        required=True
    )
    one_contract_parser = action_subparsers.add_parser(
        "contract",
        help="Deploy one contract"
    )
    one_contract_parser.add_argument(
        "--contract-file-path",
        dest="contract_file_path",
        help="Path to the contract file",
        type=str,
        required=True,
        action="store"
    )
    one_contract_parser.add_argument(
        "--contract-name",
        dest="contract_name",
        help="Name of the contract",
        type=str,
        required=True,
        action="store"
    )
    one_contract_parser.add_argument(
        "--contract-type",
        dest="contract_type",
        help="Type of the contract",
        type=str,
        required=True,
        choices=list(DEFAULT_CONTRACT_NAMES.keys()),
        action="store"
    )
    all_contracts_parser = action_subparsers.add_parser(
        "all-contracts",
        help="Compile the ABI of all contracts"
    )
    args_add_contracts_info(
        parser=all_contracts_parser,
        DEFAULT_CONTRACT_NAMES=DEFAULT_CONTRACT_NAMES
    )
    args_contract_constructor(
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


def deploy_action(
    contract_file_path: str,
    contract_name: str,
    contract_type: str,
    args: argparse.Namespace
) -> None:
    r"""
    Deploy action
    """
    w3 = web3.Web3(
        web3.Web3.HTTPProvider(args.endpoint_uri)
    )
    match contract_type:
        case "dao":
            pymeca.utils.deploy_contract(
                w3=w3,
                private_key=args.private_key,
                contract_file_path=contract_file_path,
                contract_name=contract_name
            )
        case "scheduler":
            pymeca.utils.deploy_contract(
                w3=w3,
                private_key=args.private_key,
                contract_file_path=contract_file_path,
                contract_name=contract_name,
                schedulerFee=args.scheduler_fee
            )
        case "host":
            pymeca.utils.deploy_contract(
                w3=w3,
                private_key=args.private_key,
                contract_file_path=contract_file_path,
                contract_name=contract_name,
                hostRegisterFee=args.host_register_fee,
                hostInitialStake=args.host_initial_stake,
                failedTaskPenalty=args.host_failed_task_penalty,
                taskRegisterFee=args.host_task_register_fee
            )
        case "tower":
            pymeca.utils.deploy_contract(
                w3=w3,
                private_key=args.private_key,
                contract_file_path=contract_file_path,
                contract_name=contract_name,
                towerInitialStake=args.tower_initial_stake,
                hostRequestFee=args.tower_host_request_fee,
                failedTaskPenalty=args.tower_failed_task_penalty
            )
        case "task":
            pymeca.utils.deploy_contract(
                w3=w3,
                private_key=args.private_key,
                contract_file_path=contract_file_path,
                contract_name=contract_name,
                taskAdditionFee=args.task_addition_fee
            )
        case _:
            raise ValueError(
                "Unknown contract type"
            )


def execute_action(
    args: argparse.Namespace
) -> None:
    r"""
    Execute action
    """
    if args.action == "contract":
        deploy_action(
            contract_file_path=args.contract_file_path,
            contract_name=args.contract_name,
            contract_type=args.contract_type,
            args=args
        )
    elif args.action == "all-contracts":
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
    else:
        raise ValueError(
            "Unknown action"
        )


def get_default_parser() -> argparse.ArgumentParser:
    return get_parser(
        DEFAULT_DAO_ADDRESS_FILE_PATH=DEFAULT_DAO_ADDRESS_FILE_PATH,
        DEFAULT_CONTRACT_NAMES=DEFAULT_CONTRACT_NAMES,
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


def main():
    parser = get_default_parser()
    args = parser.parse_args()
    execute_action(args)


if __name__ == "__main__":
    main()
