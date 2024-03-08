import asyncio
from web3 import Web3
import json

from pymeca.task import MecaTaskDeveloper
from pymeca.dao import get_DAO_ADDRESS
import pymeca.utils
from cli import MecaCLI

BLOCKCHAIN_URL = "http://localhost:9000"
DAO_CONTRACT_ADDRESS = get_DAO_ADDRESS()
ACCOUNTS = json.load(open("../../src/config/accounts.json", "r"))


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
    await cli.start()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
