import asyncio
import websockets

async def chat(uri, username):
    async with websockets.connect(uri) as websocket:
        async def receive():
            while True:
                try:
                    msg = await websocket.recv()
                    print("\n" + msg)
                except:
                    break

        asyncio.create_task(receive())

        while True:
            msg = input()
            # Send username as part of the message payload
            await websocket.send(f"{username}: {msg}")

def run_client():
    print("Welcome to TerminalChat!")
    server = input("Enter server address (default: terminalchat-server-1.onrender.com:443): ").strip()
    if not server:
        server = "terminalchat-server-1.onrender.com:443"
    choice = input("Enter code to join or type 'new' to create a channel: ").strip()
    if choice.lower() == "new":
        import random, string
        code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        print(f"Your channel code is: {code}")
    else:
        code = choice

    username = input("Enter your name: ").strip()
    if server.startswith("localhost") or server.startswith("127.0.0.1"):
        uri = f"ws://{server}/ws/{code}"
    else:
        uri = f"wss://{server}/ws/{code}"
    asyncio.run(chat(uri, username))