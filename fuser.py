#!/usr/bin/env python

import asyncio
import websockets
from ecies.utils import generate_eth_key
from ecies import decrypt
from ecies import encrypt
import json
import pathlib
import web3
import eth_keys
import pymeca

BLOCKCHAIN_URL = "http://localhost:9000"
DAO_CONTRACT_ADDRESS = pymeca.dao.get_DAO_ADDRESS()
ACCOUNTS = json.load(open("./src/config/accounts.json", "r"))
OUTPUT_FOLDER = pathlib.Path("./build")
# signature 65 bytes


async def hello():
    uri = "ws://localhost:7777/client"
    async with websockets.connect(uri) as websocket:
        w3 = web3.Web3(web3.Web3.HTTPProvider(BLOCKCHAIN_URL))
        meca_user = pymeca.user.MecaUser(
            w3=w3,
            private_key=ACCOUNTS["meca_user"]["private_key"],
            dao_contract_address=DAO_CONTRACT_ADDRESS,
        )

        name = input("What's your name? ")
        input_bytes = name.encode()
        # Generate asymmetric keys for host decryption and user encryption
        eth_k = generate_eth_key()
        secret_key = eth_k.to_hex()
        public_key = eth_k.public_key.to_hex()
        encrypted_input_bytes = encrypt(public_key, input_bytes)
        task_id = "0x" + "0"*64
        task_id_bytes = pymeca.utils.bytes_from_hex(task_id)
        print(encrypted_input_bytes)
        to_send = task_id_bytes + encrypted_input_bytes
        print(to_send)
        signature = meca_user.sign_bytes(to_send)
        print(signature)
        to_send = to_send + signature
        print(to_send)
        # to_send = encrypted_input_bytes
        await websocket.send(to_send)
        print(f">>> {name}")

        greeting = await websocket.recv()
        message_decrypted = decrypt(secret_key, greeting)
        print(f"<<< {message_decrypted.decode()}")

if __name__ == "__main__":
    asyncio.run(hello())
