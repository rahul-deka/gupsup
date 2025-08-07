# TerminalChat (WebSocket Edition)

A terminal-based real-time chat system using WebSockets + FastAPI.

## How to Use

### 1. Start the server
```bash
cd websocket_server
pip install -r requirements.txt
python main.py
```

### 2. Install the client
```bash
pip install .
terminalchat
```

## Deploying Server to Render
- Deploy the `websocket_server` folder as a Web Service
- Use `python main.py` as start command
- Expose port 8000