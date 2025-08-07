import socket, threading

channels = {}
clients = {}

def handle(client):
    channel = None
    while True:
        try:
            data = client.recv(1024).decode()
            if data.startswith("/join"):
                _, ch, name = data.split()
                channel = ch
                clients[client] = name
                channels.setdefault(ch, []).append(client)
                broadcast(ch, f"{name} joined the chat.")
            elif data.startswith("/msg"):
                msg = data[5:]
                broadcast(channel, f"{clients[client]}: {msg}")
        except:
            break

def broadcast(channel, msg):
    for c in channels.get(channel, []):
        try:
            c.send(msg.encode())
        except:
            pass

def start():
    s = socket.socket()
    s.bind(("0.0.0.0", 5000))
    s.listen()
    print("Server running on port 5000...")
    while True:
        c, _ = s.accept()
        threading.Thread(target=handle, args=(c,), daemon=True).start()

if __name__ == "__main__":
    start()