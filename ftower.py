#!/usr/bin/env python
from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
import asyncio

app = FastAPI()

# A dictionary to store connected clients with their IDs
connected_tasks = {}
connected_hosts = {}

class ClientConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, tuple[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, task_id: str, host_address: str):
        await websocket.accept()
        if task_id in self.active_connections:
            websocket.disconnect()
        else:
            self.active_connections[task_id] = (host_address, websocket)

    def disconnect(self, task_id):
        del self.active_connections[task_id]

    async def send_output(seld, task_id: str, host_address: str, output_bytes: bytes):
        if task_id in self.active_connections:
            if self.active_connections[task_id][0] == host_address:
                await self.active_connections[task_id][1].send_bytes(output_bytes)
                self.active_connections[task_id][1].disconnect()
                self.disconnect()


manager = ClientConnectionManager()


@app.websocket("/client")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    input_bytes = await websocket.receive_bytes()
    # get the task out of the binary message
    task_id = "0x" + input_bytes[0:32].hex()
    # task_id = "0x" + "0" * 64
    print(task_id)
    connected_tasks[task_id] = websocket
    output_bytes = input_bytes[32:]
    print(output_bytes)
    # output_bytes = input_bytes
    await websocket.send_bytes(output_bytes)

    try:
        while True:
            await asyncio.sleep(1)  # Keeps the coroutine running
    except asyncio.CancelledError:
        pass
    except WebSocketDisconnect as e:
        print(f"WebSocketDisconnect {e.code}: {e.reason}")
    finally:
        del connected_tasks[task_id]

@app.websocket("/host")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients[client_id] = websocket
    print(f"Client {client_id} just connected")

    try:
        while True:
            await asyncio.sleep(1)  # Keeps the coroutine running
    except asyncio.CancelledError:
        pass
    except WebSocketDisconnect as e:
        print(f"WebSocketDisconnect {e.code}: {e.reason}")
    finally:
        del connected_clients[client_id]
