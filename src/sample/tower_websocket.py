#!/usr/bin/env python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
from web3 import Web3
import os
import secrets
import pymeca

app = FastAPI()

BLOCKCHAIN_URL = os.getenv(
    "MECA_BLOCKCHAIN_RPC_URL",
    "http://localhost:9000"
)
MECA_DAO_CONTRACT_ADDRESS = pymeca.dao.get_DAO_ADDRESS()
MECA_TOWER_PRIVATE_KEY = os.getenv(
    "MECA_TOWER_PRIVATE_KEY", "0x62e6e282e5c1657c78c3a967b36711eb3906a7c8603d71d409e7a54d87bdc1f7"
)

web3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_URL))

meca_tower = pymeca.tower.MecaTower(
    w3=web3,
    private_key=MECA_TOWER_PRIVATE_KEY,
    dao_contract_address=MECA_DAO_CONTRACT_ADDRESS,
)


class ClientConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, tuple[str, WebSocket]] = {}

    async def connect(
        self,
        websocket: WebSocket,
        task_id: str,
        host_address: str
    ) -> bool:
        await websocket.accept()
        if task_id in self.active_connections:
            websocket.disconnect()
            return False
        else:
            self.active_connections[task_id] = (host_address, websocket)
            return True

    def disconnect(self, task_id: str):
        del self.active_connections[task_id]

    async def send_output(
        self,
        task_id: str,
        host_address: str,
        output_bytes: bytes
    ) -> bool:
        if task_id in self.active_connections:
            if self.active_connections[task_id][0] == host_address:
                await self.active_connections[
                    task_id][1].send_bytes(output_bytes)
                self.active_connections[task_id][1].disconnect()
                self.disconnect()
                return True
        return False


client_manager = ClientConnectionManager()


class HostConnectionManager:
    def __init__(self):
        # host_address: WebSocket
        self.active_connections: dict[str,  WebSocket] = {}

    async def connect(
        self,
        websocket: WebSocket,
        host_address: str
    ) -> bool:
        await websocket.accept()
        if host_address in self.active_connections:
            websocket.disconnect()
            return False
        else:
            self.active_connections[host_address] = websocket
            return True

    def disconnect(self, host_address: str):
        del self.active_connections[host_address]

    async def send_input(
        self,
        host_address: str,
        input_bytes: bytes
    ) -> bool:
        if host_address in self.active_connections:
            await self.active_connections[
                host_address].send_bytes(input_bytes)
            return True
        return False


host_manager = ClientConnectionManager()


@app.websocket("/client")
async def websocket_endpoint_client(websocket: WebSocket):
    await websocket.accept()

    input_bytes = await websocket.receive_bytes()
    # get the task out of the binary message
    task_id = "0x" + input_bytes[0:32].hex()
    # task_id = "0x" + "0" * 64
    # print(task_id)
    signature = input_bytes[-65:]
    # print(signature)
    verify = pymeca.utils.verify_signature(
        signature_bytes=signature,
        message_bytes=input_bytes[0:-65]
    )

    if not verify:
        await websocket.send_text("Invalid signature")
        return

    user_eth_address = pymeca.utils.get_eth_address_hex_from_signature(
        signature_bytes=signature,
        message_bytes=input_bytes[0:-65]
    )
    blockchain_task = meca_tower.get_running_task(
        task_id=task_id
    )

    if blockchain_task is None:
        await websocket.send_text("Task not found")
        return

    if blockchain_task["owner"] != user_eth_address:
        await websocket.send_text("Unauthorized")
        return

    host_address = blockchain_task["hostAddress"]
    tower_address = blockchain_task["towerAddress"]

    if tower_address != meca_tower.account.address:
        await websocket.send_text("Wrong tower address")
        return

    tower_host = meca_tower.get_my_hosts()
    if host_address not in tower_host:
        await websocket.send_text("Host not found")
        return

    if not await client_manager.connect(websocket, task_id, host_address):
        await websocket.send_text("Task already connected")
        return

    # output_bytes = input_bytes[32:-65]

    # send the bytes to the host
    # await websocket.send_bytes(output_bytes)
    host_connected = await host_manager.send_input(host_address, input_bytes)
    if not host_connected:
        await websocket.send_text("Host not connected")
        client_manager.disconnect(task_id)
        return

    await websocket.send_text("Task connected")

    try:
        while True:
            await asyncio.sleep(1)  # Keeps the coroutine running
    except asyncio.CancelledError:
        pass
    except WebSocketDisconnect as e:
        print(f"WebSocketDisconnect {e.code}: {e.reason}")
    finally:
        client_manager.disconnect(task_id)


@app.websocket("/host")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    token = secrets.token_bytes(nbytes=32)
    await websocket.send_bytes(token)

    input_bytes = await websocket.receive_bytes()

    host_address = "0x" + input_bytes[0:20].hex()
    signature = input_bytes[-65:]

    verify = pymeca.utils.verify_signature(
        signature_bytes=signature,
        message_bytes=input_bytes[0:20] + token
    )

    if not verify:
        await websocket.send_text("Invalid signature")
        return

    host_ecc_pub_key = pymeca.utils.get_publick_key_from_signature(
        signature_bytes=signature,
        message_bytes=input_bytes[0:20] + token
    )
    host_ecc_pub_key_hex = "0x" + host_ecc_pub_key.to_compressed_bytes(
    )[1:].hex()

    blockcahin_host_pub_key = meca_tower.get_host_public_key(
        host_address=host_address
    )

    if host_ecc_pub_key_hex != blockcahin_host_pub_key:
        await websocket.send_text("Invalid host encryption public key")
        return

    my_hosts = meca_tower.get_my_hosts()
    if host_address not in my_hosts:
        await websocket.send_text("Host not register with this tower")
        return

    if not await host_manager.connect(websocket, host_address):
        await websocket.send_text("Host already connected")
        return

    await websocket.send_text("Host connected")

    try:
        while True:
            task_output = await websocket.receive_bytes()
            task_id = "0x" + task_output[0:32].hex()
            signature = task_output[-65:]
            verify = pymeca.utils.verify_signature_pub_key(
                signature_bytes=signature,
                message_bytes=task_output[0:-65],
                public_key_bytes=host_ecc_pub_key
            )
            if not verify:
                await websocket.send_text("Invalid signature")
                continue
            task_connected = await client_manager.send_output(
                task_id=task_id,
                host_address=host_address,
                output_bytes=task_output
            )
            if not task_connected:
                await websocket.send_text("Task not connected")
                continue
            await websocket.send_text("Task output sent")
    except asyncio.CancelledError:
        pass
    except WebSocketDisconnect as e:
        print(f"WebSocketDisconnect {e.code}: {e.reason}")
    finally:
        host_manager.disconnect(host_address)
