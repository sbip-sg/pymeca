#!/usr/bin/env python

import asyncio
import websockets
from ecies.utils import generate_eth_key
from ecies import decrypt
from ecies import encrypt
import pymeca


async def hello():
    uri = "ws://localhost:7777/client"
    async with websockets.connect(uri) as websocket:
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
        # to_send = encrypted_input_bytes
        await websocket.send(to_send)
        print(f">>> {name}")

        greeting = await websocket.recv()
        message_decrypted = decrypt(secret_key, greeting)
        print(f"<<< {message_decrypted.decode()}")

if __name__ == "__main__":
    asyncio.run(hello())
