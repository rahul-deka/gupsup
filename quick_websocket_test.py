import asyncio
import websockets
import json

async def quick_test():
    """Quick WebSocket test"""
    uri = "ws://localhost:8000/ws/quicktest"
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            await websocket.send("TestUser: Hello from quick test!")
            print("✅ Message sent successfully!")
            print("✅ WebSocket connection working!")
            return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(quick_test())
    print(f"Test result: {'PASS' if result else 'FAIL'}")
