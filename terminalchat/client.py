import asyncio
import websockets
import json
import sys
import os
from typing import Optional
import logging

try:
    from .config import Config
except ImportError:
    # Fallback for when running as script
    from config import Config

# Configure logging
logging.basicConfig(level=getattr(logging, Config.get_log_level()))
logger = logging.getLogger(__name__)

class TerminalChatClient:
    def __init__(self):
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.username: str = ""
        self.channel_code: str = ""
        self.server_uri: str = ""
        self.is_connected: bool = False
        self.reconnect_attempts: int = 0
        self.max_reconnect_attempts: int = Config.get_max_reconnect_attempts()
        self.websocket_config = Config.get_websocket_config()
    
    def get_server_config(self) -> str:
        """Get server configuration from environment or user input"""
        default_server = Config.get_server_address()
        
        print("Welcome to TerminalChat!")
        server = input(f"Enter server address (default: {default_server}): ").strip()
        if not server:
            server = default_server
        return server
    
    def get_channel_code(self) -> str:
        """Get or generate channel code"""
        choice = input("Enter code to join or type 'new' to create a channel: ").strip()
        if choice.lower() == "new":
            import random, string
            code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            print(f"Your channel code is: {code}")
            print("Share this code with others to join your channel!")
            return code
        else:
            return choice
    
    def get_username(self) -> str:
        """Get username from user"""
        while True:
            username = input("Enter your name: ").strip()
            if username:
                return username
            print("Username cannot be empty. Please try again.")
    
    def build_websocket_uri(self, server: str, code: str) -> str:
        """Build WebSocket URI based on server address"""
        if server.startswith("localhost") or server.startswith("127.0.0.1"):
            return f"ws://{server}/ws/{code}"
        else:
            return f"wss://{server}/ws/{code}"
    
    async def connect(self) -> bool:
        """Establish WebSocket connection with retry logic"""
        try:
            self.websocket = await websockets.connect(
                self.server_uri,
                **self.websocket_config
            )
            self.is_connected = True
            self.reconnect_attempts = 0
            print(f"✅ Connected to channel: {self.channel_code}")
            print("Type your messages and press Enter to send. Type 'quit' to exit.\n")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    async def reconnect(self) -> bool:
        """Attempt to reconnect to the server"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            print(f"❌ Max reconnection attempts ({self.max_reconnect_attempts}) reached. Giving up.")
            return False
        
        self.reconnect_attempts += 1
        print(f"🔄 Attempting to reconnect... (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
        
        await asyncio.sleep(2 ** self.reconnect_attempts)  # Exponential backoff
        return await self.connect()
    
    async def receive_messages(self):
        """Handle incoming messages"""
        while self.is_connected:
            try:
                if self.websocket:
                    message = await self.websocket.recv()
                    print(f"\r{message}")
                    print("", end="", flush=True)  # Restore input prompt
            except websockets.exceptions.ConnectionClosed:
                print("\n🔗 Connection lost. Attempting to reconnect...")
                self.is_connected = False
                if await self.reconnect():
                    continue
                else:
                    break
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
                break
    
    async def send_messages(self):
        """Handle outgoing messages"""
        while self.is_connected:
            try:
                # Use asyncio to make input non-blocking
                message = await asyncio.get_event_loop().run_in_executor(None, input)
                
                if message.lower() in ['quit', 'exit', '/quit', '/exit']:
                    print("👋 Goodbye!")
                    self.is_connected = False
                    break
                
                if message.strip():  # Don't send empty messages
                    if self.websocket:
                        formatted_message = f"{self.username}: {message}"
                        await self.websocket.send(formatted_message)
                        
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                self.is_connected = False
                break
            except Exception as e:
                print(f"❌ Error sending message: {e}")
                break
    
    async def chat(self):
        """Main chat loop"""
        if not await self.connect():
            return
        
        try:
            # Run receive and send coroutines concurrently
            await asyncio.gather(
                self.receive_messages(),
                self.send_messages()
            )
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Clean up resources"""
        self.is_connected = False
        if self.websocket:
            try:
                await self.websocket.close()
            except:
                pass

def run_client():
    """Main entry point for the terminal chat client"""
    client = TerminalChatClient()
    
    try:
        # Get configuration
        server = client.get_server_config()
        client.channel_code = client.get_channel_code()
        client.username = client.get_username()
        client.server_uri = client.build_websocket_uri(server, client.channel_code)
        
        # Start chat
        asyncio.run(client.chat())
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)