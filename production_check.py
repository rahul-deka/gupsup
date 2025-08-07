"""
Production Readiness Check for TerminalChat
"""
import asyncio
import websockets
import requests
import subprocess
import sys
import os
from pathlib import Path

class ProductionReadinessChecker:
    def __init__(self):
        self.results = {}
        self.server_process = None
        
    def log_result(self, test_name, passed, details=""):
        """Log a test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.results[test_name] = passed
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
    
    def start_local_server(self):
        """Start local server for testing"""
        try:
            self.server_process = subprocess.Popen(
                [sys.executable, "../terminalchat-server/main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            import time
            time.sleep(3)  # Give server time to start
            return self.server_process.poll() is None
        except Exception as e:
            print(f"Failed to start server: {e}")
            return False
    
    def stop_local_server(self):
        """Stop local server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
    
    def check_server_files(self):
        """Check if all required server files exist"""
        required_files = [
            "../terminalchat-server/main.py",
            "../terminalchat-server/requirements.txt",
            "../terminalchat-server/README.md"
        ]
        
        all_exist = True
        missing_files = []
        
        for file_path in required_files:
            if not Path(file_path).exists():
                all_exist = False
                missing_files.append(file_path)
        
        details = f"Missing files: {missing_files}" if missing_files else "All required files present"
        self.log_result("Server Files Complete", all_exist, details)
        return all_exist
    
    def check_client_package(self):
        """Check if client package is properly structured"""
        required_files = [
            "pyproject.toml",
            "setup.py",
            "terminalchat/__init__.py",
            "terminalchat/client.py",
            "terminalchat/config.py",
            "README.md"
        ]
        
        all_exist = True
        missing_files = []
        
        for file_path in required_files:
            if not Path(file_path).exists():
                all_exist = False
                missing_files.append(file_path)
        
        details = f"Missing files: {missing_files}" if missing_files else "All required files present"
        self.log_result("Client Package Complete", all_exist, details)
        return all_exist
    
    def check_dependencies(self):
        """Check if dependencies are properly specified"""
        try:
            # Check server requirements
            with open("../terminalchat-server/requirements.txt", "r", encoding="utf-8") as f:
                server_deps = f.read().strip()
            
            server_ok = "fastapi" in server_deps and "uvicorn" in server_deps
            
            # Check client dependencies in pyproject.toml
            with open("pyproject.toml", "r", encoding="utf-8") as f:
                client_deps = f.read()
            
            client_ok = "websockets" in client_deps
            
            overall_ok = server_ok and client_ok
            details = f"Server deps OK: {server_ok}, Client deps OK: {client_ok}"
            self.log_result("Dependencies Specified", overall_ok, details)
            return overall_ok
            
        except Exception as e:
            self.log_result("Dependencies Specified", False, f"Error: {e}")
            return False
    
    async def check_websocket_functionality(self):
        """Test WebSocket functionality"""
        try:
            # Test connection to local server
            uri = "ws://localhost:8000/ws/prodtest"
            async with websockets.connect(uri) as websocket:
                # Test sending message
                await websocket.send("ProdTestUser: Testing production readiness")
                
                # Test that we can connect (no response expected for single client)
                self.log_result("WebSocket Connection", True, "Can connect and send messages")
                return True
                
        except Exception as e:
            self.log_result("WebSocket Connection", False, f"Error: {e}")
            return False
    
    def check_http_endpoints(self):
        """Test HTTP endpoints"""
        try:
            # Test root endpoint
            response = requests.get("http://localhost:8000", timeout=5)
            root_ok = response.status_code == 200 and "TerminalChat Server" in response.text
            
            # Test health endpoint
            health_response = requests.get("http://localhost:8000/health", timeout=5)
            health_ok = health_response.status_code == 200
            
            overall_ok = root_ok and health_ok
            details = f"Root: {response.status_code}, Health: {health_response.status_code}"
            self.log_result("HTTP Endpoints", overall_ok, details)
            return overall_ok
            
        except Exception as e:
            self.log_result("HTTP Endpoints", False, f"Error: {e}")
            return False
    
    def check_render_deployment_files(self):
        """Check if files are ready for Render deployment"""
        # Check if main.py can be run directly
        server_main_exists = Path("../terminalchat-server/main.py").exists()
        
        # Check if requirements.txt is in the right place
        requirements_exists = Path("../terminalchat-server/requirements.txt").exists()
        
        # Check if README has deployment instructions
        readme_path = Path("../terminalchat-server/README.md")
        readme_ok = False
        if readme_path.exists():
            try:
                with open(readme_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    readme_ok = "Render" in content and "python main.py" in content
            except UnicodeDecodeError:
                # Try with different encoding
                try:
                    with open(readme_path, "r", encoding="latin-1") as f:
                        content = f.read()
                        readme_ok = "Render" in content and "python main.py" in content
                except:
                    readme_ok = False
        
        overall_ok = server_main_exists and requirements_exists and readme_ok
        details = f"main.py: {server_main_exists}, requirements.txt: {requirements_exists}, README: {readme_ok}"
        self.log_result("Render Deployment Ready", overall_ok, details)
        return overall_ok
    
    def check_client_installation(self):
        """Check if client can be installed"""
        try:
            # Try to install in development mode
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-e", "."],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            install_ok = result.returncode == 0
            
            # Try to import the client
            if install_ok:
                try:
                    import terminalchat.client
                    import_ok = True
                except ImportError:
                    import_ok = False
            else:
                import_ok = False
            
            overall_ok = install_ok and import_ok
            details = f"Install: {install_ok}, Import: {import_ok}"
            self.log_result("Client Installation", overall_ok, details)
            return overall_ok
            
        except Exception as e:
            self.log_result("Client Installation", False, f"Error: {e}")
            return False
    
    async def run_all_checks(self):
        """Run all production readiness checks"""
        print("🔍 Production Readiness Check for TerminalChat\n")
        
        # Static file checks (don't need server)
        print("📁 File Structure Checks:")
        self.check_server_files()
        self.check_client_package()
        self.check_dependencies()
        self.check_render_deployment_files()
        print()
        
        # Client installation check
        print("📦 Client Installation Check:")
        self.check_client_installation()
        print()
        
        # Server functionality checks (need running server)
        print("🚀 Server Functionality Checks:")
        if self.start_local_server():
            self.log_result("Server Startup", True, "Server started successfully")
            
            # Wait a moment for server to be fully ready
            await asyncio.sleep(2)
            
            self.check_http_endpoints()
            await self.check_websocket_functionality()
            
            self.stop_local_server()
        else:
            self.log_result("Server Startup", False, "Could not start server")
            self.log_result("HTTP Endpoints", False, "Server not running")
            self.log_result("WebSocket Connection", False, "Server not running")
        
        print()
        
        # Summary
        print("📊 Production Readiness Summary:")
        passed = sum(1 for result in self.results.values() if result)
        total = len(self.results)
        
        for test_name, result in self.results.items():
            status = "✅" if result else "❌"
            print(f"  {status} {test_name}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 PRODUCTION READY! ✅")
            print("\nDeployment Instructions:")
            print("1. Deploy terminalchat-server folder to Render.com")
            print("2. Install client on devices: pip install ./terminalchat")
            print("3. Run client: terminalchat")
            return True
        else:
            print(f"\n⚠️  NOT PRODUCTION READY - {total - passed} issues to fix")
            return False

async def main():
    checker = ProductionReadinessChecker()
    return await checker.run_all_checks()

if __name__ == "__main__":
    try:
        is_ready = asyncio.run(main())
        sys.exit(0 if is_ready else 1)
    except KeyboardInterrupt:
        print("\nCheck interrupted by user")
        sys.exit(1)
