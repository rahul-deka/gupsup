#!/usr/bin/env python3
"""
Development startup script for TerminalChat
"""
import os
import sys
import subprocess
import time
import signal
from pathlib import Path

def find_project_root():
    """Find the project root directory"""
    current = Path(__file__).parent
    while current.parent != current:
        if (current / "terminalchat").exists() and (current.parent / "terminalchat-server").exists():
            return current.parent
        current = current.parent
    return Path(__file__).parent.parent

def start_server():
    """Start the TerminalChat server"""
    project_root = find_project_root()
    server_dir = project_root / "terminalchat-server"
    
    if not server_dir.exists():
        print("❌ Server directory not found!")
        return None
    
    print("🚀 Starting TerminalChat Server...")
    
    # Change to server directory and start
    env = os.environ.copy()
    env['PYTHONPATH'] = str(server_dir)
    
    try:
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=server_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give the server a moment to start
        time.sleep(2)
        
        if process.poll() is None:
            print("✅ Server started successfully on http://localhost:8000")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def install_client():
    """Install the client in development mode"""
    project_root = find_project_root()
    client_dir = project_root / "terminalchat"
    
    if not client_dir.exists():
        print("❌ Client directory not found!")
        return False
    
    print("📦 Installing TerminalChat client...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            cwd=client_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Client installed successfully")
            return True
        else:
            print(f"❌ Client installation failed:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to install client: {e}")
        return False

def run_tests():
    """Run the test suite"""
    project_root = find_project_root()
    test_file = project_root / "terminalchat" / "test_terminalchat.py"
    
    if not test_file.exists():
        print("❌ Test file not found!")
        return False
    
    print("🧪 Running tests...")
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def main():
    """Main development setup function"""
    print("🛠️  TerminalChat Development Setup\n")
    
    # Step 1: Install client
    if not install_client():
        print("\n❌ Setup failed at client installation")
        return 1
    
    print()
    
    # Step 2: Run tests
    if not run_tests():
        print("\n⚠️  Tests failed, but continuing with server startup")
    
    print()
    
    # Step 3: Start server
    server_process = start_server()
    
    if server_process:
        print("\n🎉 Development environment ready!")
        print("\nYou can now:")
        print("  1. Open a new terminal and run: terminalchat")
        print("  2. Visit http://localhost:8000 for server status")
        print("  3. Visit http://localhost:8000/docs for API documentation")
        print("\nPress Ctrl+C to stop the server")
        
        try:
            # Keep the script running and display server output
            while True:
                line = server_process.stdout.readline()
                if line:
                    print(f"[SERVER] {line.strip()}")
                elif server_process.poll() is not None:
                    break
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            server_process.terminate()
            server_process.wait()
            print("✅ Server stopped")
        
        return 0
    else:
        print("\n❌ Development setup failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
