import asyncio
import os
import pathlib
from web3 import Web3
import json
from pymeca.host import MecaHost
import pymeca.utils
import websockets
import requests
import ipfsApi
from ecies.utils import generate_eth_key
from ecies import decrypt
import docker
from pymeca.dao import get_DAO_ADDRESS
from cli import MecaCLI

TASK_EXECUTOR_URL = "http://host.docker.internal:2591"
IPFS_HOST = "host.docker.internal"
IPFS_PORT = 8080
BLOCKCHAIN_URL = "http://localhost:9000"
DAO_CONTRACT_ADDRESS = get_DAO_ADDRESS()
ACCOUNTS = json.load(open("../../src/config/accounts.json", "r"))
CONTAINER_FOLDER = pathlib.Path("./build")

CONTAINER_NAME_LIMIT = 10
DEFAULT_BLOCK_TIMEOUT_LIMIT = 10

ipfs_client = ipfsApi.Client(IPFS_HOST, IPFS_PORT)
docker_client = docker.from_env()


class MecaHostCLI(MecaCLI):
    async def run_func(self, func, args):
        if func.__name__ == "add_task":
            ipfs_sha = args[0]
            ipfs_cid = pymeca.utils.cid_from_sha256(ipfs_sha)

            this_dir = os.getcwd()
            CONTAINER_FOLDER.mkdir(exist_ok=True)
            os.chdir(CONTAINER_FOLDER)
            ipfs_client.get(ipfs_cid)
            print("Downloaded IPFS folder.")

            docker_client.images.build(path=f"./{ipfs_cid}", tag=f"{ipfs_cid[-CONTAINER_NAME_LIMIT:]}")
            print("Built docker image.")
            os.chdir(this_dir)
        print(func.__name__, ":")
        print(await super().run_func(func, args))


async def main():
    web3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_URL))

    meca_host = MecaHost(
        w3=web3,
        private_key=ACCOUNTS["meca_host"]["private_key"],
        dao_contract_address=DAO_CONTRACT_ADDRESS,
    )

    print("Started host with address:", meca_host.account.address)

    eth_k = generate_eth_key()
    sk_hex = eth_k.to_hex()
    pk_hex = eth_k.public_key.to_hex()
    default_public_key = pk_hex

    if not meca_host.is_registered():
        default_block_timeout_limit = DEFAULT_BLOCK_TIMEOUT_LIMIT
        default_initial_deposit = meca_host.get_host_initial_stake()

        print("\nHost is not registered. Registering...")
        block_timeout_limit = int(input(f"Enter block timeout limit: ({default_block_timeout_limit}) ").strip() or default_block_timeout_limit)
        public_key = input(f"Enter public key: ({default_public_key}) ").strip() or default_public_key
        initial_deposit = int(input(f"Enter initial deposit: ({default_initial_deposit}) ").strip() or default_initial_deposit)
        meca_host.register(block_timeout_limit, public_key, initial_deposit)
    else:
        meca_host.update_block_timeout_limit(DEFAULT_BLOCK_TIMEOUT_LIMIT)
        print("Host block timeout limit updated.")
        meca_host.update_public_key(default_public_key)
        print("Host public key updated.")
    print("Host registered.")

    async def wait_for_task(tower_uri: str):
        host_address = meca_host.account.address
        if tower_uri.startswith("http://"):
            tower_uri = tower_uri[len("http://"):]
        async with websockets.connect(f'ws://{tower_uri}/ws/{host_address}') as websocket:
            print("Waiting for tasks on websocket...")
            while True:
                message = await websocket.recv()
                decrypted_data = json.loads(decrypt(sk_hex, bytes.fromhex(message)).decode("utf-8"))
                print(f"Received message from server: {decrypted_data}")
                decrypted_data["id"] = decrypted_data["id"][-CONTAINER_NAME_LIMIT:] + ":latest"
                res = requests.post(TASK_EXECUTOR_URL, json=decrypted_data)
                print(res.text)
                await websocket.send(res.text)

    cli = MecaHostCLI(meca_host)
    cli.add_method(wait_for_task)
    cli.add_method(meca_host.get_tasks)
    await cli.start()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
