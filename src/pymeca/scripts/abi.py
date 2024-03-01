import pathlib
import logging
import argparse
import os
import json
import pymeca.utils
import deploy


logger = logging.getLogger(__name__)


ABI_NAMES = pymeca.utils.ABI_NAMES
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
    deploy.args_add_contracts_info(
        parser=all_contracts_parser,
        DEFAULT_CONTRACT_NAMES=DEFAULT_CONTRACT_NAMES
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
        compile_abi(
            contract_file_path=args.dao_file_path,
            contract_name=args.dao_contract_name,
            contract_type="dao",
            abi_directory=args.abi_directory
        )
        compile_abi(
            contract_file_path=args.scheduler_file_path,
            contract_name=args.scheduler_contract_name,
            contract_type="scheduler",
            abi_directory=args.abi_directory
        )
        compile_abi(
            contract_file_path=args.host_file_path,
            contract_name=args.host_contract_name,
            contract_type="host",
            abi_directory=args.abi_directory
        )
        compile_abi(
            contract_file_path=args.tower_file_path,
            contract_name=args.tower_contract_name,
            contract_type="tower",
            abi_directory=args.abi_directory
        )
        compile_abi(
            contract_file_path=args.task_file_path,
            contract_name=args.task_contract_name,
            contract_type="task",
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
        DEFAULT_CONTRACT_NAMES=DEFAULT_CONTRACT_NAMES
    )


def main():
    parser = get_default_parser()
    args = parser.parse_args()
    execute_action(args)


"""
Example of use:
1. One contract
python abi.py \
--abi-directory ../contracts_abi \
contract \
--contract-file-path \
../../../meca-contracts/src/contracts/MecaContract.sol \
--contract-name MecaDaoContract \
--contract-type dao
2. All contracts
python abi.py \
--abi-directory ../tcontracts_abi \
all-contracts \
--dao-file-path \
../../../meca-contracts/src/contracts/MecaContract.sol \
--dao-contract-name MecaDaoContract \
--scheduler-file-path \
../../../meca-contracts/src/contracts/SchedulerAbstract.sol \
--scheduler-contract-name MecaSchedulerAbstractContract \
--host-file-path \
../../../meca-contracts/src/contracts/HostAbstract.sol \
--host-contract-name MecaHostAbstractContract \
--tower-file-path \
../../../meca-contracts/src/contracts/TowerAbstract.sol \
--tower-contract-name MecaTowerAbstractContract \
--task-file-path \
../../../meca-contracts/src/contracts/TaskAbstract.sol \
--task-contract-name MecaTaskAbstractContract
"""
if __name__ == "__main__":
    main()
