import asyncio
from web3 import Web3
import json
import ipfsApi

import pymeca.utils
from pymeca.task import MecaTaskDeveloper
from pymeca.dao import get_DAO_ADDRESS
from cli import MecaCLI

IPFS_HOST = "host.docker.internal"
IPFS_PORT = 5001
BLOCKCHAIN_URL = "http://localhost:9000"
DAO_CONTRACT_ADDRESS = get_DAO_ADDRESS()
ACCOUNTS = json.load(open("../../src/config/accounts.json", "r"))


ipfs_client = ipfsApi.Client(IPFS_HOST, IPFS_PORT)


async def add_folder_to_ipfs(folder_path: str):
    return ipfs_client.add(folder_path, recursive=True)


class TaskDeveloperCLI(MecaCLI):
    async def run_func(self, func, args):
        print(func.__name__, ":")
        print(await super().run_func(func, args))


async def main():
    web3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_URL))

    meca_task_developer = MecaTaskDeveloper(
        w3=web3,
        private_key=ACCOUNTS["meca_task"]["private_key"],
        dao_contract_address=DAO_CONTRACT_ADDRESS,
    )

    print("Started task dev with address:", meca_task_developer.account.address)

    cli = TaskDeveloperCLI(meca_task_developer)
    cli.add_method(pymeca.utils.get_sha256_from_cid)
    cli.add_method(add_folder_to_ipfs)
    await cli.start()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
