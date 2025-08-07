from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Dict, List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

channels: Dict[str, List[WebSocket]] = {}
users: Dict[WebSocket, str] = {}

@app.websocket("/ws/{channel}/{username}")
async def websocket_endpoint(websocket: WebSocket, channel: str, username: str):
    await websocket.accept()
    users[websocket] = username
    if channel not in channels:
        channels[channel] = []
    channels[channel].append(websocket)

    await broadcast(channel, f"🟢 {username} joined the chat.")

    try:
        while True:
            data = await websocket.receive_text()
            await broadcast(channel, f"{username}: {data}")
    except WebSocketDisconnect:
        channels[channel].remove(websocket)
        await broadcast(channel, f"🔴 {username} left the chat.")
        del users[websocket]

async def broadcast(channel: str, message: str):
    for ws in channels.get(channel, []):
        await ws.send_text(message)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)