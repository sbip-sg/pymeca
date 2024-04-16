import asyncio
import base64
import websockets
import pathlib
import os
from ecies import encrypt
from ecies import decrypt
from web3 import Web3
from eth_hash.auto import keccak

import pymeca

from cli import MecaCLI

BLOCKCHAIN_URL = os.getenv(
    "MECA_BLOCKCHAIN_RPC_URL",
    "http://localhost:9000"
)
MECA_DAO_CONTRACT_ADDRESS = pymeca.dao.get_DAO_ADDRESS()
MECA_USER_PRIVATE_KEY = os.getenv(
    "MECA_USER_PRIVATE_KEY", "0x738626482f61c62379627cc124d446183c6e4d9ea1a5a5ccf72e2140c304bdfc"
)
OUTPUT_FOLDER = pathlib.Path("./build")


class MecaUserCLI(MecaCLI):
    def __init__(self):
        web3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_URL))
        meca_user = pymeca.user.MecaUser(
            w3=web3,
            private_key=MECA_USER_PRIVATE_KEY,
            dao_contract_address=MECA_DAO_CONTRACT_ADDRESS,
        )
        print("Started user with address:", meca_user.account.address)
        super().__init__(meca_user)

    async def wait_for_task(self, websocket, task_id):
        task_output = await websocket.recv()
        task_id = "0x" + task_output[0:32].hex()
        signature = task_output[-65:]
        verify = pymeca.utils.verify_signature(
            signature_bytes=signature,
            message_bytes=task_output[0:-65]
        )
        if not verify:
            print("Signature verification failed.")
            return
        host_ecc_pub_key = pymeca.utils.get_publick_key_from_signature(
            signature_bytes=signature,
            message_bytes=task_output[0:-65]
        )
        host_ecc_pub_key_hex = (
            "0x" +
            host_ecc_pub_key.to_compressed_bytes()[1:].hex()
        )

        runningTask = self.actor.get_running_task(task_id)
        host_address = runningTask["hostAddress"]
        blockcahin_host_pub_key = self.actor.get_host_public_key(
            host_address
        )

        if host_ecc_pub_key_hex != blockcahin_host_pub_key:
            print("Invalid host encryption public key")
            return

        encrypted_message = task_output[32:-65]
        message = decrypt(
            self.actor.private_key,
            encrypted_message
        )

        output_hash = runningTask["outputHash"]
        received_hash = "0x" + keccak(message).hex()
        if output_hash != received_hash:
            print("Output hash mismatch")
            return

        OUTPUT_FOLDER.mkdir(exist_ok=True)
        with open(f"{OUTPUT_FOLDER}/output.png", "wb") as f:
            f.write(base64.b64decode(message))

        print("Task output saved to output.png")

    async def finish_task(self, task_id):
        # wait for the task to be over on blockchain
        while not self.actor.is_task_done(task_id=task_id):
            await asyncio.sleep(1)

        self.actor.finish_task(task_id=task_id)
        print("sent finish task transaction.")

    async def run_func(self, func, args):
        if func.__name__ == "send_task_on_blockchain":
            ipfs_sha = args[0]
            host_address = args[1]
            tower_address = args[2]
            content = args[3]

            input_bytes = content.encode()
            # because I set the input in pymeca as a hex string
            input_hash = keccak(input_bytes).hex()
            success, task_id = self.actor.send_task_on_blockchain(
                ipfs_sha=ipfs_sha,
                host_address=host_address,
                tower_address=tower_address,
                input_hash=input_hash
            )
            tower_url = self.actor.get_tower_public_uri(tower_address)
            blockcahin_host_pub_key = self.actor.get_host_public_key(
                host_address
            )
            encrypted_input_bytes = encrypt(
                blockcahin_host_pub_key,
                input_bytes
            )
            task_id_bytes = pymeca.utils.bytes_from_hex(task_id)
            to_send = task_id_bytes + encrypted_input_bytes
            signature = self.actor.sign_bytes(to_send)
            to_send = to_send + signature
            uri = f"ws://{tower_url}/client"
            async with websockets.connect(uri) as websocket:
                await websocket.send(to_send)
                tasks = [
                    asyncio.ensure_future(
                        self.wait_for_task(websocket, task_id)
                    ),
                    asyncio.ensure_future(
                        self.finish_task(task_id)
                    )
                ]
                finished, unfinished = await asyncio.wait(
                    tasks,
                    return_when=asyncio.FIRST_COMPLETED
                )
                if tasks[0] in unfinished:
                    tasks[0].cancel()
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
