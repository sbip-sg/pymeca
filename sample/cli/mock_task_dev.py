import asyncio
from web3 import Web3
import json
import ipfs_api
import os

import pymeca.utils
from pymeca.task import MecaTaskDeveloper
from pymeca.dao import get_DAO_ADDRESS
from cli import MecaCLI

IPFS_HOST = "localhost"
IPFS_PORT = 5001
BLOCKCHAIN_URL = "http://localhost:9000"
DAO_CONTRACT_ADDRESS = get_DAO_ADDRESS()
ACCOUNTS = json.load(open("../../src/config/accounts.json", "r"))


async def add_folder_to_ipfs(folder_path: str):
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        print("Folder not found.")
        return
    with ipfs_api.ipfshttpclient.connect(f"/dns/{IPFS_HOST}/tcp/{IPFS_PORT}/http") as client:
        for res in client.add(folder_path, recursive=True, cid_version=1):
            print(res.as_json())


class TaskDeveloperCLI(MecaCLI):
    def __init__(self):
        web3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_URL))
        meca_task_developer = MecaTaskDeveloper(
            w3=web3,
            private_key=ACCOUNTS["meca_task"]["private_key"],
            dao_contract_address=DAO_CONTRACT_ADDRESS,
        )
        print("Started task dev with address:", meca_task_developer.account.address)
        super().__init__(meca_task_developer)

    async def run_func(self, func, args):
        print(func.__name__, ":")
        print(await super().run_func(func, args))


async def main():
    cli = TaskDeveloperCLI()
    cli.add_method(pymeca.utils.get_sha256_from_cid)
    cli.add_method(add_folder_to_ipfs)
    await cli.start()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
