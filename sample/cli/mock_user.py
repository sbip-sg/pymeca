import asyncio
import base64
import hashlib
import pathlib
from ecies import encrypt
import requests
from web3 import Web3
import json

import pymeca.utils
from pymeca.user import MecaUser
from pymeca.dao import get_DAO_ADDRESS
from sample.cli import MecaCLI

BLOCKCHAIN_URL = "http://localhost:9000"
DAO_CONTRACT_ADDRESS = get_DAO_ADDRESS()
ACCOUNTS = json.load(open("../../src/config/accounts.json", "r"))
OUTPUT_FOLDER = pathlib.Path("./build")


def send_message_to_tower(tower_uri, task_id, message):
    tower_url = f"{tower_uri}/send_task"
    res = requests.post(tower_url, json={"taskId": task_id, "message": message})
    if res.status_code != 200:
        print(f"Failed to send message to tower. Status code: {res.status_code}")
        return
    res_obj = res.json()
    # print(f"Response from tower: {res_obj}")
    if "message" in res_obj and res_obj["message"]:
        message = json.loads(res_obj["message"])
        if "success" in message and message["success"]:
            # save to png
            OUTPUT_FOLDER.mkdir(exist_ok=True)
            with open(f"{OUTPUT_FOLDER}/output.png", "wb") as f:
                f.write(base64.b64decode(message['msg']))
            print("Message result saved to output.png")
        elif "msg" in message and message["msg"]:
            print(f"Host failed to process the message. {message['msg']}")
        else:
            print("Unexpected message from host.", message)
        return message
    else:
        print("No message from host.")
        return


class MecaUserCLI(MecaCLI):
    def __init__(self):
        web3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_URL))
        meca_user = MecaUser(
            w3=web3,
            private_key=ACCOUNTS["meca_user"]["private_key"],
            dao_contract_address=DAO_CONTRACT_ADDRESS,
        )
        print("Started user with address:", meca_user.account.address)
        super().__init__(meca_user)

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
            input_bytes = content.encode()
            # because I set the input in pymeca as a hex string
            input_hash = hashlib.sha256(input_bytes).hexdigest()
            success, task_id = meca_user.send_task_on_blockchain(
                ipfs_sha=ipfs_sha,
                host_address=host_address,
                tower_address=tower_address,
                input_hash=input_hash
            )
            tower_url = meca_user.get_tower_public_uri(tower_address)
            host_public_key = meca_user.get_host_public_key(host_address)
            encrypted_input_bytes = encrypt(host_public_key, input_bytes)
            task_id_bytes = meca_user._bytes_from_hex(task_id)
            to_send = task_id_bytes + encrypted_input_bytes
            send_message_to_tower(
                tower_uri=tower_url,
                message=to_send
            )

            # Hash the input and submit it to the blockchain
            input_str = json.dumps(task_input)
            input_hash = hashlib.sha256(input_str.encode("utf-8")).hexdigest()

            success, task_id = meca_user.send_task_on_blockchain(ipfs_sha, host_address, tower_address, input_hash)
            print(f"Task sent to blockchain: task id: {task_id}\n")

            # Send the encrypted input to the tower
            tower_url = meca_user.get_tower_public_uri(tower_address)
            print(f"Sending encrypted input to the tower at {tower_url}")
            host_public_key = meca_user.get_host_public_key(host_address)
            input_enc = encrypt(host_public_key, input_str.encode("utf-8")).hex()
            send_message_to_tower(tower_url, task_id, input_enc)
        else:
            print(func.__name__, ":")
            print(await super().run_func(func, args))


async def main():
    cli = MecaUserCLI()
    meca_user = cli.actor
    cli.add_method(meca_user.get_tasks)
    cli.add_method(meca_user.get_towers_hosts_for_task)
    await cli.start()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
