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
            await websocket.send(msg)

def run_client():
    print("Welcome to TerminalChat!")
    choice = input("Enter code to join or type 'new' to create a channel: ").strip()
    if choice.lower() == "new":
        import random, string
        code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        print(f"Your channel code is: {code}")
    else:
        code = choice

    username = input("Enter your name: ").strip()
    uri = f"wss://terminalchat-server-1.onrender.com/ws/{code}"  # Use wss:// for HTTPS-secured WebSocket
    asyncio.run(chat(uri, username))