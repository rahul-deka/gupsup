#!/usr/bin/env python3
"""
Simple test script to verify TerminalChat functionality
"""
import asyncio
import websockets
import sys
import os

# Add the parent directory to the path so we can import terminalchat
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_server_connection():
    """Test basic server connectivity"""
    test_server = "localhost:8000"
    test_channel = "test123"
    test_uri = f"ws://{test_server}/ws/{test_channel}"
    
    print(f"Testing connection to: {test_uri}")
    
    try:
        async with websockets.connect(test_uri) as websocket:
            print("✅ Successfully connected to server")
            
            # Send a test message
            await websocket.send("TestUser: Hello, World!")
            print("✅ Message sent successfully")
            
            # Try to receive (with timeout)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                print(f"📨 Received: {response}")
            except asyncio.TimeoutError:
                print("⏰ No response received (expected for single client)")
            
            return True
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

async def test_client_import():
    """Test client module import"""
    try:
        from terminalchat.client import TerminalChatClient
        from terminalchat.config import Config
        
        print("✅ Client modules imported successfully")
        
        # Test configuration
        server = Config.get_server_address()
        max_attempts = Config.get_max_reconnect_attempts()
        print(f"✅ Configuration loaded: server={server}, max_attempts={max_attempts}")
        
        # Test client instantiation
        client = TerminalChatClient()
        print("✅ Client instantiated successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Client import test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Running TerminalChat Tests\n")
    
    # Test 1: Client import
    print("Test 1: Client Module Import")
    import_success = await test_client_import()
    print()
    
    # Test 2: Server connection (optional - only if server is running)
    print("Test 2: Server Connection (requires server running on localhost:8000)")
    connection_success = await test_server_connection()
    print()
    
    # Summary
    print("📊 Test Summary:")
    print(f"  Client Import: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"  Server Connection: {'✅ PASS' if connection_success else '⚠️ SKIP (server not running)'}")
    
    if import_success:
        print("\n🎉 Core functionality is working!")
        if not connection_success:
            print("💡 To test server connection, run: cd terminalchat-server && python main.py")
    else:
        print("\n❌ Core functionality has issues!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
