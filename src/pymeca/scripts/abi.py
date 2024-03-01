import pathlib
import logging
import pymeca.utils
import argparse
import os
import json


logger = logging.getLogger(__name__)


ABI_NAMES = pymeca.utils.ABI_NAMES
DEFAULT_FILE_NAMES = {
    "dao": "MecaContract.sol",
    "scheduler": "SchedulerAbstract.sol",
    "host": "HostAbstract.sol",
    "task": "TaskAbstract.sol",
    "tower": "TowerAbstract.sol"
}
DEFAULT_CONTRACT_NAMES = {
    "dao": "MecaDaoContract",
    "scheduler": "MecaSchedulerAbstractContract",
    "host": "MecaHostAbstractContract",
    "task": "MecaTaskAbstractContract",
    "tower": "MecaTowerAbstractContract"
}
ABI_DIRECTORY = str(pymeca.utils.ABI_DIRECTORY)


def compile_abi(
    contract_file_path: str,
    contract_name: str,
    contract_type: str,
    abi_directory: str
) -> bool:
    r"""
    Compile ABI
    """
    contract_abi, _ = pymeca.utils.get_contract_compile_info(
        contract_file_path=contract_file_path,
        contract_name=contract_name,
        output_values=["abi"]
    )
    abi_directory = pathlib.Path(abi_directory).absolute()
    abi_file_path = (
        abi_directory /
        f"{ABI_NAMES[contract_type]}.json"
    ).resolve()
    with open(abi_file_path, "w", encoding="utf-8") as f:
        json.dump(contract_abi, f, ensure_ascii=False, indent=4)


def get_parser(
    ABI_DIRECTORY: str,
    ABI_NAMES: dict,
    DEFAULT_FILE_NAMES: dict,
    DEFAULT_CONTRACT_NAMES: dict
) -> argparse.ArgumentParser:
    r"""
    Get parser
    """
    parser = argparse.ArgumentParser(
        prog="abi.py",
        description="Compile ABI CLI for the MECA contracts",
        allow_abbrev=True,
        add_help=True
    )

    # make the parser
    # destination abi directory
    parser.add_argument(
        "--abi-directory",
        dest="abi_directory",
        help="Path to the directory where the ABI files will be saved",
        type=str,
        default=ABI_DIRECTORY,
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
        help="Compile the ABI of one contract"
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
        choices=list(ABI_NAMES.keys()),
        action="store"
    )
    all_contracts_parser = action_subparsers.add_parser(
        "all-contracts",
        help="Compile the ABI of all contracts"
    )
    all_contracts_parser.add_argument(
        "--contracts-directory",
        dest="contracts_directory",
        help="Path to the contracts directory",
        type=str,
        required=True,
        action="store"
    )
    all_contracts_parser.add_argument(
        "--dao-file-name",
        dest="dao_file_name",
        help="The dao contract file name",
        type=str,
        default=DEFAULT_FILE_NAMES["dao"],
        action="store"
    )
    all_contracts_parser.add_argument(
        "--dao-contract-name",
        dest="dao_contract_name",
        help="The dao contract name",
        type=str,
        default=DEFAULT_CONTRACT_NAMES["dao"],
        action="store"
    )
    all_contracts_parser.add_argument(
        "--scheduler-file-name",
        dest="scheduler_file_name",
        help="The scheduler contract file name",
        type=str,
        default=DEFAULT_FILE_NAMES["scheduler"],
        action="store"
    )
    all_contracts_parser.add_argument(
        "--scheduler-contract-name",
        dest="scheduler_contract_name",
        help="The scheduler contract name",
        type=str,
        default=DEFAULT_CONTRACT_NAMES["scheduler"],
        action="store"
    )
    all_contracts_parser.add_argument(
        "--host-file-name",
        dest="host_file_name",
        help="The host contract file name",
        type=str,
        default=DEFAULT_FILE_NAMES["host"],
        action="store"
    )
    all_contracts_parser.add_argument(
        "--host-contract-name",
        dest="host_contract_name",
        help="The host contract name",
        type=str,
        default=DEFAULT_CONTRACT_NAMES["host"],
        action="store"
    )
    all_contracts_parser.add_argument(
        "--task-file-name",
        dest="task_file_name",
        help="The task contract file name",
        type=str,
        default=DEFAULT_FILE_NAMES["task"],
        action="store"
    )
    all_contracts_parser.add_argument(
        "--task-contract-name",
        dest="task_contract_name",
        help="The task contract name",
        type=str,
        default=DEFAULT_CONTRACT_NAMES["task"],
        action="store"
    )
    all_contracts_parser.add_argument(
        "--tower-file-name",
        dest="tower_file_name",
        help="The tower contract file name",
        type=str,
        default=DEFAULT_FILE_NAMES["tower"],
        action="store"
    )
    all_contracts_parser.add_argument(
        "--tower-contract-name",
        dest="tower_contract_name",
        help="The tower contract name",
        type=str,
        default=DEFAULT_CONTRACT_NAMES["tower"],
        action="store"
    )
    return parser


def execute_action(
    args: argparse.Namespace
) -> None:
    r"""
    Execute action
    """
    os.makedirs(
        args.abi_directory,
        exist_ok=True
    )
    # print(args.action)
    if args.action == "contract":
        compile_abi(
            contract_file_path=args.contract_file_path,
            contract_name=args.contract_name,
            contract_type=args.contract_type,
            abi_directory=args.abi_directory
        )
    elif args.action == "all-contracts":
        args.contracts_directory = pathlib.Path(args.contracts_directory)
        compile_abi(
            contract_file_path=str(
                args.contracts_directory /
                args.dao_file_name
            ),
            contract_name=args.dao_contract_name,
            contract_type="dao",
            abi_directory=args.abi_directory
        )
        compile_abi(
            contract_file_path=str(
                args.contracts_directory /
                args.scheduler_file_name
            ),
            contract_name=args.scheduler_contract_name,
            contract_type="scheduler",
            abi_directory=args.abi_directory
        )
        compile_abi(
            contract_file_path=str(
                args.contracts_directory /
                args.host_file_name
            ),
            contract_name=args.host_contract_name,
            contract_type="host",
            abi_directory=args.abi_directory
        )
        compile_abi(
            contract_file_path=(
                args.contracts_directory /
                args.task_file_name
            ),
            contract_name=args.task_contract_name,
            contract_type="task",
            abi_directory=args.abi_directory
        )
        compile_abi(
            contract_file_path=str(
                args.contracts_directory /
                args.tower_file_name
            ),
            contract_name=args.tower_contract_name,
            contract_type="tower",
            abi_directory=args.abi_directory
        )
    else:
        raise ValueError(
            "Invalid action"
        )


def get_default_parser() -> argparse.ArgumentParser:
    r"""
    Get default parser
    """
    return get_parser(
        ABI_DIRECTORY=ABI_DIRECTORY,
        ABI_NAMES=ABI_NAMES,
        DEFAULT_FILE_NAMES=DEFAULT_FILE_NAMES,
        DEFAULT_CONTRACT_NAMES=DEFAULT_CONTRACT_NAMES
    )


def main():
    parser = get_default_parser()
    args = parser.parse_args()
    execute_action(args)


if __name__ == "__main__":
    main()
