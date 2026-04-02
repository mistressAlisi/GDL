import asyncio, json, websockets
from .handlers import CommandHandler

async def handle_client(websocket):
    handler = CommandHandler(websocket)
    async for raw in websocket:
        try:
            message = json.loads(raw)
            await handler.handle(message)
        except Exception as e:
            await websocket.send(json.dumps({"type": "error", "error": str(e)}))

async def start_server(host='0.0.0.0', port=8765):
    async with websockets.serve(handle_client, host, port):
        print(f"Athena GDL Daemon running on ws://{host}:{port}")
        await asyncio.Future()  # run forever
