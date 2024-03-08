import asyncio
import requests
from web3 import Web3
import json
from ecies import encrypt

import pymeca.utils
from pymeca.user import MecaUser
from pymeca.dao import get_DAO_ADDRESS
from cli import MecaCLI

BLOCKCHAIN_URL = "http://localhost:9000"
DAO_CONTRACT_ADDRESS = get_DAO_ADDRESS()
ACCOUNTS = json.load(open("../../src/config/accounts.json", "r"))


class MecaUserCLI(MecaCLI):
    async def run_func(self, func, args):
        if func.__name__ == "send_task_on_blockchain":
            meca_user = self.actor
            ipfs_sha = args[0]
            ipfs_cid = pymeca.utils.cid_from_sha256(ipfs_sha)
            host_address = args[1]
            tower_address = args[2]
            content = args[3]
            task_input = {
                "id": ipfs_cid,
                "input": content,
            }

            host_public_key = meca_user.get_host_public_key(host_address)

            # Encrypt the input with the host's public key and submit it to the blockchain
            input_hash = encrypt(host_public_key, json.dumps(task_input).encode("utf-8")).hex()
            truncated_input_hash = input_hash[:64]
            success, task_id = meca_user.send_task_on_blockchain(ipfs_sha, host_address, tower_address, truncated_input_hash)
            print("Task sent to blockchain.\n")

            tower_url = meca_user.get_tower_public_uri(tower_address) + f"/send_message"
            print(f"Sending encrypted input to the tower at {tower_url}")

            # Send the encrypted input to the tower
            res = requests.post(tower_url, json={"target_client_id": host_address, "task_id": task_id, "message": input_hash})
            if res.status_code != 200:
                print(f"Failed to send message to tower. Status code: {res.status_code}")
                return
            res_obj = res.json()
            print(f"Response from tower: {res_obj}")
            if "message" in res_obj and res_obj["message"]:
                message = json.loads(res_obj["message"])
                print(f"Response from host: {message}")
            else:
                print("No message from host.")
        else:
            print(func.__name__, ":")
            print(await super().run_func(func, args))


async def main():
    web3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_URL))

    meca_user = MecaUser(
        w3=web3,
        private_key=ACCOUNTS["meca_user"]["private_key"],
        dao_contract_address=DAO_CONTRACT_ADDRESS,
    )

    print("Started user with address:", meca_user.account.address)

    cli = MecaUserCLI(meca_user)
    cli.add_method(meca_user.get_tasks)
    cli.add_method(meca_user.get_towers_hosts_for_task)
    await cli.start()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
