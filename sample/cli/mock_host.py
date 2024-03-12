import asyncio
import hashlib
import pathlib
from web3 import Web3
import json
import websockets
import requests
import ipfs_api
from ecies.utils import generate_eth_key
import docker

import pymeca.utils
from pymeca.host import MecaHost
from pymeca.dao import get_DAO_ADDRESS
from cli import MecaCLI

TASK_EXECUTOR_URL = "http://host.docker.internal:2591"
IPFS_HOST = "localhost"
IPFS_PORT = 8080
BLOCKCHAIN_URL = "http://localhost:9000"
DAO_CONTRACT_ADDRESS = get_DAO_ADDRESS()
ACCOUNTS = json.load(open("../../src/config/accounts.json", "r"))
CONTAINER_FOLDER = pathlib.Path("./build")

CONTAINER_NAME_LIMIT = 10
DEFAULT_BLOCK_TIMEOUT_LIMIT = 10


class MecaHostCLI(MecaCLI):
    def __init__(self):
        web3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_URL))
        meca_host = MecaHost(
            w3=web3,
            private_key=ACCOUNTS["meca_host"]["private_key"],
            dao_contract_address=DAO_CONTRACT_ADDRESS,
        )
        print("Started host with address:", meca_host.account.address)

        self.docker_client = docker.APIClient()
        super().__init__(meca_host)

    async def run_func(self, func, args):
        if func.__name__ == "add_task":
            ipfs_sha = args[0]
            ipfs_cid = pymeca.utils.cid_from_sha256(ipfs_sha)

            # Download IPFS folder in CONTAINER_FOLDER
            CONTAINER_FOLDER.mkdir(exist_ok=True)
            with ipfs_api.ipfshttpclient.connect(f"/dns/{IPFS_HOST}/tcp/{IPFS_PORT}/http") as client:
                client.get(ipfs_cid, target=CONTAINER_FOLDER)
            print("Downloaded IPFS folder.")

            # Build docker image from IPFS folder
            generator = self.docker_client.build(path=f"./{CONTAINER_FOLDER}/{ipfs_cid}",
                                                 tag=f"{ipfs_cid[-CONTAINER_NAME_LIMIT:]}",
                                                 decode=True)
            while True:
                try:
                    line = next(generator)
                    print(line)
                except StopIteration:
                    break
                except Exception as e:
                    print(e)
            print("Built docker image.")
        print(func.__name__, ":")
        print(await super().run_func(func, args))

    def shutdown(self):
        self.docker_client.close()


async def main():
    cli = MecaHostCLI()
    meca_host = cli.actor

    # Generate asymmetric keys for host decryption and user encryption
    eth_k = generate_eth_key()
    sk_hex = eth_k.to_hex()
    pk_hex = eth_k.public_key.to_hex()
    default_public_key = pk_hex

    # Register host if not registered
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

    # Blocking function to wait for tasks from a given tower
    async def wait_for_task(tower_uri: str):
        host_address = meca_host.account.address
        if tower_uri.startswith("http://"):
            tower_uri = tower_uri[len("http://"):]
        async with websockets.connect(f'ws://{tower_uri}/ws/{host_address}') as websocket:
            print("Waiting for tasks on websocket...")
            while True:
                packet = await websocket.recv()
                json_packet = json.loads(packet)
                if "taskId" not in json_packet or "message" not in json_packet:
                    print("Invalid packet received.")
                    continue
                task_id = json_packet["taskId"]
                message_str = json_packet["message"]

                # Verify task on blockchain
                running_task = meca_host.get_running_task(task_id)
                if running_task is None:
                    print(f"Task {task_id} not found.")
                    continue
                # Verify message input
                calculated_hash = "0x" + hashlib.sha256(message_str.encode("utf-8")).hexdigest()
                if running_task["inputHash"] != calculated_hash:
                    print("Task hash mismatch.")
                    continue

                print(f"Received message from server: {message_str}")
                message = json.loads(message_str)
                message["id"] = message["id"][-CONTAINER_NAME_LIMIT:] + ":latest"

                # Send task to executor
                res = requests.post(TASK_EXECUTOR_URL, json=message)
                print(res.text)
                await websocket.send(res.text)

    cli.add_method(wait_for_task)
    cli.add_method(meca_host.get_tasks)
    await cli.start()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
