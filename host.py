#!/usr/bin/env python

import asyncio
import websockets
from ecies.utils import generate_eth_key
from ecies import decrypt
from ecies import encrypt


async def hello():
    uri = "ws://localhost:7777/host"
    async with websockets.connect(uri) as websocket:
        name = input("What's your name? ")
        input_bytes = name.encode()
        # Generate asymmetric keys for host decryption and user encryption
        eth_k = generate_eth_key()
        secret_key = eth_k.to_hex()
        public_key = eth_k.public_key.to_hex()
        encrypted_input_bytes = encrypt(public_key, input_bytes)
        await websocket.send(encrypted_input_bytes)
        print(f">>> {name}")

        greeting = await websocket.recv()
        message_decrypted = decrypt(secret_key, greeting)
        print(f"<<< {message_decrypted.decode()}")

        name = "Ion"
        input_bytes = name.encode()
        encrypted_input_bytes = encrypt(public_key, input_bytes)
        await websocket.send(encrypted_input_bytes)
        print(f">>> {name}")

        greeting = await websocket.recv()
        message_decrypted = decrypt(secret_key, greeting)
        print(f"<<< {message_decrypted.decode()}")

        async for message in websocket:
            print(message)

if __name__ == "__main__":
    asyncio.run(hello())
