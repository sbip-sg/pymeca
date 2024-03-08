from fastapi import FastAPI, WebSocket, Request
import asyncio
from web3 import Web3
import json

from pymeca.tower import MecaTower
from pymeca.dao import get_DAO_ADDRESS

app = FastAPI()

BLOCKCHAIN_URL = "http://localhost:9000"
DAO_CONTRACT_ADDRESS = get_DAO_ADDRESS()
ACCOUNTS = json.load(open("../../src/config/accounts.json", "r"))

web3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_URL))

meca_tower = MecaTower(
    w3=web3,
    private_key=ACCOUNTS["meca_tower"]["private_key"],
    dao_contract_address=DAO_CONTRACT_ADDRESS,
)

# A dictionary to store connected clients with their IDs
connected_clients = {}


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    connected_clients[client_id] = websocket
    print(f"Client {client_id} just connected")

    try:
        while True:
            await asyncio.sleep(1)  # Keeps the coroutine running
    except asyncio.CancelledError:
        pass
    finally:
        del connected_clients[client_id]


@app.post("/send_message")
async def send_message(request: Request):
    data = await request.json()
    target_client_id = data["target_client_id"]
    message = data["message"]
    task_id = data["task_id"]
    if target_client_id in connected_clients:

        # Check if the task is submitted on the blockchain
        running_task = meca_tower.get_running_task(task_id)
        if running_task is None:
            return {"error": f"Task {task_id} not found."}
        print("Running task found.")

        # Check if the message matches with the running task input
        if running_task["inputHash"] != "0x"+message[:64]:
            return {"error": f"Message does not match with the running task input."}
        print("Message matches with the running task input.")

        # Send the message to the target client and wait for the response
        target_conn = connected_clients[target_client_id]
        await target_conn.send_text(message)
        print(f"Message sent to client {target_client_id}")
        res = await target_conn.receive_text()
        print(f"Response received from client {target_client_id}")

        return {"message": res}
    else:
        return {"error": f"Client {target_client_id} not found."}


@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI WebSocket server."}
