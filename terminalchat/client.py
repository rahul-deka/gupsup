import socket, threading
import random, string

def random_code(length=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def create_channel():
    code = random_code()
    print(f"Your channel code: {code}")
    join_channel(code)

def join_channel(code):
    name = input("Choose a username: ")
    s = socket.socket()
    s.connect(("localhost", 5000))
    s.send(f"/join {code} {name}".encode())

    def listen():
        while True:
            try:
                msg = s.recv(1024).decode()
                print("\n" + msg)
            except:
                break

    threading.Thread(target=listen, daemon=True).start()

    while True:
        try:
            msg = input()
            s.send(f"/msg {msg}".encode())
        except:
            break