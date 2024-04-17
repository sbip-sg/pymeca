import pathlib
import logging
import secrets
import random
import json
import web3
from solcx import compile_source
from eth_account import Account
import eth_keys
import multiformats_cid

logger = logging.getLogger(__name__)


ABI_NAMES = {
    "dao": "MecaDAO",
    "scheduler": "MecaScheduler",
    "host": "MecaHost",
    "task": "MecaTask",
    "tower": "MecaTower"
}
CURRENT_DIRECTORY = pathlib.Path(__file__).absolute().parent
ABI_DIRECTORY = (
    CURRENT_DIRECTORY /
    "contracts_abi"
).resolve()


class MecaError(Exception):
    r"""
    Meca Error
    """
    pass


def get_contract_compile_info(
    contract_file_path: str,
    contract_name: str,
    output_values: list[str] = ["abi", "bin"],
    evm_version: str = "shanghai"
) -> tuple[str, str]:
    r"""
    Get the contract compile info

    Args:
        contract_file_path : path to the contract file
        contract_name : name of the contract
        output_values : if "abi" and "bin" are present, then the abi and bin
            will be returned
        evm_version : evm version

    Returns:
        contract abi and bytecode
    """
    logger.info(
        f"Compiling the contract {contract_name} at {contract_file_path}"
    )
    # contracts path
    contract_file_path: pathlib.Path = pathlib.Path(
        contract_file_path).resolve().absolute()

    contracts_path = contract_file_path.parent

    # read the contract code
    contract_code = contract_file_path.read_text()

    # compile the contract
    compiled_sol = compile_source(
        contract_code,
        base_path=contracts_path,
        output_values=output_values,
        evm_version=evm_version,
        optimize=True
    )

    compiled_contract_name = f'<stdin>:{contract_name}'
    if compiled_contract_name not in compiled_sol:
        raise MecaError(
            f"Contract {contract_name} not found in the compiled contracts"
        )
    # get the contract abi
    if "abi" in output_values:
        contract_abi = compiled_sol[f'<stdin>:{contract_name}']['abi']
    else:
        contract_abi = ""
    # get the contract bytecode
    if "bin" in output_values:
        contract_bytecode = compiled_sol[f'<stdin>:{contract_name}']['bin']
    else:
        contract_bytecode = ""

    return (contract_abi, contract_bytecode)


# load the abi files for the contracts
try:
    with open(str(ABI_DIRECTORY / ABI_NAMES["dao"]) + ".json", "r") as f:
        MECA_DAO_ABI = json.load(f)
    with open(str(ABI_DIRECTORY / ABI_NAMES["scheduler"]) + ".json", "r") as f:
        MECA_SCHEDULER_ABI = json.load(f)
    with open(str(ABI_DIRECTORY / ABI_NAMES["host"]) + ".json", "r") as f:
        MECA_HOST_ABI = json.load(f)
    with open(str(ABI_DIRECTORY / ABI_NAMES["task"]) + ".json", "r") as f:
        MECA_TASK_ABI = json.load(f)
    with open(str(ABI_DIRECTORY / ABI_NAMES["tower"]) + ".json", "r") as f:
        MECA_TOWER_ABI = json.load(f)
except Exception as e:
    raise MecaError(
        f"Error loading the abi files: {e}"
    )


def get_gas_to_send(
    w3: web3.Web3,
    account: Account,
    gas_estimate: int,
    gas_extra: int = 100000
) -> int:
    r"""
    Get the gas to send with the transaction

    Args:
        w3 : web3 instance
        account : account
        gas_estimate : gas estimate
        gas_extra : extra gas

    Returns:
        gas to send
    """
    # verify the balance
    account_balance = w3.eth.get_balance(account.address)
    if account_balance < (gas_estimate + gas_extra) * w3.eth.gas_price:
        raise MecaError(
            f"""Insufficient balance {account_balance}
            < {(gas_estimate + gas_extra) * w3.eth.gas_price}
            """
        )

    return gas_estimate + gas_extra


def sign_send_wait_transaction(
    w3: web3.Web3,
    transaction: dict,
    private_key: str
) -> web3.datastructures.AttributeDict:
    r"""
    Sign, send and wait for the transaction

    Args:
        w3 : web3 instance
        account : account
        transaction : transaction
        private_key : private key

    Returns:
        transaction receipt
    """
    # sign the transaction
    singed_transaction = w3.eth.account.sign_transaction(
        transaction, private_key
    )
    # send the transaction
    tx_hash = w3.eth.send_raw_transaction(
        singed_transaction.rawTransaction
    )
    # wait for the transaction receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    if tx_receipt.status != 1:
        raise MecaError(
            "Transaction failed"
        )

    return tx_receipt


def deploy_contract(
    w3: web3.Web3,
    private_key: str,
    contract_file_path: str,
    contract_name: str,
    **kwargs
) -> str:
    r"""
    Deploy the a contract to the blockchain

    Args:
        w3 : web3 instance
        private_key : private key of the account
        contract_file_path : path to the contract file
        contract_name : name of the contract
        kwargs : constructor arguments

    Returns:
        contract address
    """
    logger.info(
        f"Deploying the contract {contract_name} at {contract_file_path}"
    )
    # get the accouynt
    account = Account.from_key(private_key)
    # compile the contract
    contract_abi, contract_bytecode = get_contract_compile_info(
        contract_file_path=contract_file_path,
        contract_name=contract_name,
        output_values=["abi", "bin"]
    )

    # deploy the contract
    # create the contract instance
    contract = w3.eth.contract(
        abi=contract_abi,
        bytecode=contract_bytecode
    )

    constructor_function = (
        contract.constructor()
        if len(kwargs) == 0
        else contract.constructor(**kwargs)
    )

    # estimate the gas for the transaction
    gas_estimate = constructor_function.estimate_gas()
    # how much gas to send with the transaction
    gas_to_send = get_gas_to_send(
        w3=w3,
        account=account,
        gas_estimate=gas_estimate
    )
    # build the transaction
    contract_transaction = constructor_function.build_transaction({
        "from": account.address,
        "gas": gas_to_send,
        "nonce": w3.eth.get_transaction_count(account.address)
    })

    # sign send and wait for the transaction
    tx_receipt = sign_send_wait_transaction(
        w3=w3,
        transaction=contract_transaction,
        private_key=private_key
    )

    return tx_receipt.contractAddress


def get_sha256_from_cid(
    cid: str
) -> str:
    r"""
    Get the sha256 from the cid

    Args:
        cid : cid of the directory/file

    Returns:
        sha256
    """
    # convert the cid to class
    cid = multiformats_cid.make_cid(cid)
    if type(cid) is multiformats_cid.CIDv0:
        cid = cid.to_v1()
    # encode in hex
    hex_cid_bytes = cid.encode("base16")
    hex_cid_hex_string = str(hex_cid_bytes)
    hex_cid_hex_string = hex_cid_hex_string[3:-1]
    cid_version = hex_cid_hex_string[:2]
    hex_cid_hex_string = hex_cid_hex_string[2:]
    cid_codec = hex_cid_hex_string[:2]
    hex_cid_hex_string = hex_cid_hex_string[2:]
    cid_multihash_type = hex_cid_hex_string[:2]
    hex_cid_hex_string = hex_cid_hex_string[2:]
    cid_multihash_length = hex_cid_hex_string[:2]
    hex_cid_hex_string = hex_cid_hex_string[2:]
    cid_multihash = hex_cid_hex_string
    if cid_version != "01":
        raise MecaError(
            "Invalid cid version"
        )
    if cid_codec != "70":
        raise MecaError(
            "Invalid cid codec"
        )
    # sha3
    if cid_multihash_type != "12":
        raise MecaError(
            "Invalid cid multihash type"
        )

    # 32 bytes
    if cid_multihash_length != "20":
        raise MecaError(
            "Invalid cid multihash length"
        )

    # verify length 32 bytes -> 64 hex caracters
    if len(cid_multihash) != 64:
        raise MecaError(
            "Invalid cid multihash string length"
        )

    return cid_multihash


def cidv1_object_from_sha256(
    sha256: str
) -> multiformats_cid.CIDv1:
    r"""
    Get the cid version 1 object from the sha256

    Args:
        sha256 : sha256

    Returns:
        cid version 1
    """
    # cid version
    version = "01"
    # codec dag-pb
    codec = "70"
    # sha3
    multihash_type = "12"
    # length of sha3
    multihash_length = "20"
    # convert the sha256
    if not sha256.startswith("0x"):
        raise MecaError(
            "Invalid sha256"
        )
    sha256 = sha256[2:]
    if len(sha256) != 64:
        raise MecaError(
            "Invalid sha256 length"
        )
    # sha256 hash
    multihash = sha256

    # 0x
    hex_cid_hex_string = (
        version +
        codec +
        multihash_type +
        multihash_length +
        multihash
    )
    # convert to bytes
    hex_cid_bytes = bytes.fromhex(hex_cid_hex_string)
    # convert to cid
    return multiformats_cid.make_cid(hex_cid_bytes)


def cid_from_sha256(
    sha256: str
) -> str:
    r"""
    Get the cid string from the sha256

    Args:
        sha256 : sha256

    Returns:
        cid
    """
    return str(cidv1_object_from_sha256(sha256))


def generate_account() -> tuple[str, str]:
    r"""
    Generate an account using secrests

    Returns:
        (private_key, address)
    """
    private_key = "0x" + secrets.token_hex(32)
    account_address = Account.from_key(private_key).address
    return (private_key, account_address)


def generate_simulate_account() -> tuple[str, str]:
    r"""
    Generate an account for simulation using random

    Returns:
        (private_key, address)
    """
    private_key_bytes = random.randbytes(32).hex()
    private_key = "0x" + private_key_bytes
    account_address = Account.from_key(private_key).address
    return (private_key, account_address)


def generate_meca_simulate_accounts(
    initial_balance: int = 1000
) -> dict[str, dict[str, str]]:
    r"""
    Generate meca simulate accounts with the given
    initial balance.

    The accounts are the dao owner, a tower, a host, a user,
    and a task developer.

    Args:
        initial_balance : initial balance

    Returns:
        accounts -> {
            "meca_dao": {
                "private_key": private_key,
                "account_address": account_address,
                "balance": balance
            },
            "meca_tower": {
                "private_key": private_key,
                "account_address": account_address,
                "balance": balance
            },
            "meca_host": {
                "private_key": private_key,
                "account_address": account_address,
                "balance": balance
            },
            "meca_user": {
                "private_key": private_key,
                "account_address": account_address,
                "balance": balance
            },
            "meca_task": {
                "private_key": private_key,
                "account_address": account_address,
                "balance": balance
            }
        }
    """
    accounts = dict()
    # MECA DAO, MECA Tower, MECA Host, MECA User, MECA Task developer
    accounts_names = [
        "meca_dao",
        "meca_tower",
        "meca_host",
        "meca_user",
        "meca_task"
    ]
    for account_name in accounts_names:
        private_key, account_address = generate_simulate_account()
        accounts[account_name] = {
            "private_key": private_key,
            "account_address": account_address,
            "balance": hex(web3.Web3.to_wei(initial_balance, "ether"))
        }
    return accounts


def bytes_from_hex(
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


def verify_signature(
    message_bytes: bytes,
    signature_bytes: bytes
) -> bool:
    r"""
    Verify the signature of the message

    Args:
        message_bytes : message bytes
        signature_bytes : signature bytes

    Returns:
        bool : True if the signature is valid, False otherwise
    """
    signature = eth_keys.keys.Signature(signature_bytes)
    public_key = signature.recover_public_key_from_msg(message_bytes)
    return signature.verify_msg(message_bytes, public_key)


def get_public_key_from_signature(
    message_bytes: bytes,
    signature_bytes: bytes
) -> eth_keys.keys.PublicKey:
    r"""
    Get the public key from the signature

    Args:
        message_bytes : message bytes
        signature_bytes : signature bytes

    Returns:
        eth_keys.keys.PublicKey : public key
    """
    signature = eth_keys.keys.Signature(signature_bytes)
    return signature.recover_public_key_from_msg(message_bytes)


def get_eth_address_hex_from_signature(
    message_bytes: bytes,
    signature_bytes: bytes
) -> str:
    r"""
    Get the ethereum address hex from the signature

    Args:
        message_bytes : message bytes
        signature_bytes : signature bytes

    Returns:
        str : ethereum address hex
    """
    public_key = get_public_key_from_signature(
        message_bytes=message_bytes,
        signature_bytes=signature_bytes
    )
    return public_key.to_address()


def verify_signature_pub_key(
    message_bytes: bytes,
    signature_bytes: bytes,
    public_key: eth_keys.keys.PublicKey
) -> bool:
    r"""
    Verify the signature using the public key

    Args:
        signature_bytes : signature bytes
        public_key_bytes : public key bytes

    Returns:
        bool : True if the signature is valid, False otherwise
    """
    signature = eth_keys.keys.Signature(signature_bytes)
    return signature.verify_msg(message_bytes, public_key)


def sign_bytes(
    message_bytes: bytes,
    private_key: str
) -> bytes:
    r"""
    Sign the message bytes using the private key

    Args:
        message_bytes : message bytes
        private_key : private key

    Returns:
        bytes : signature bytes
    """
    signPrivateKeyBytes = eth_keys.keys.PrivateKey(
        bytes_from_hex(
            private_key
        )
    )
    return signPrivateKeyBytes.sign_msg(message_bytes).to_bytes()
