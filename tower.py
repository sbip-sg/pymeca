#!/usr/bin/env python

import asyncio
import signal
import websockets


# host_adrress -> true
HOSTS = {}
# clients : task_id -> websocket
CLIENTS = {}


async def task_handler(websocket):
    async for message in websocket:
        print(message)
        await websocket.send(message)


async def router(websocket, path):
    if path == "/":
        await websocket.send("ghinion")
    elif path == "/start_task":
        await task_handler(websocket)
    else:
        await websocket.send("ghinion")


async def main():
    # Set the stop condition when receiving SIGTERM.
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    async with websockets.serve(router, "localhost", 7777):
        await stop

if __name__ == "__main__":
    asyncio.run(main())
