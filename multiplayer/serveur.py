import socket
import threading
import json
import time
FORMAT = "utf-8"
HEADER = 64
PORT = 5050
DISCONNECT = "[DISCONNECT]"
clients = {}

def search_client():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(1.0)
    s.bind(("", 5051))
    print("[WAITING] the server is waiting for client...")
    while True:
        try:
            s_data, s_addr = s.recvfrom(1024)
            print(f"[FOUND] {s_addr} as been found...")
            s.sendto("searching client...".encode(FORMAT), s_addr)
        except socket.timeout:
            pass
        time.sleep(0.5)


def connect_client ():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ADDR = ("0.0.0.0", PORT)
    server.bind(ADDR)
    return server

def handle_client(client, addr):
    print(f"[NEW CLIENT] {addr} connected\n")
    clients[addr] = client
    send_dict({"server": "hello client"}, client)
    connected = True
    while connected:
        try:
            msg_len_str = client.recv(HEADER).decode(FORMAT).strip()
            if not msg_len_str:
                break

            msg_len = int(msg_len_str)
            msg = client.recv(msg_len).decode(FORMAT)
            if msg == DISCONNECT:
                connected = False
            else :
                handle_message_recieved(msg, addr)
        except Exception as e:
            pass
    if addr in clients:
        del clients[addr]
    disconnect(client)

def handle_message_recieved (msg, addr):
    try:
        data = json.loads(msg)
        msg_type = data.get("type")
        if msg_type == "list":
            liste = data["payload"]
            print(f"[LIST] {addr} : {liste}")

        elif msg_type == "dict":
            dic = data["payload"]
            print(f"[DICT] {addr} : {dic}")

        elif msg_type == "tuple":
            tup = data["payload"]
            print(f"[TUP] {addr} : {tup}")

        elif msg_type == "str" :
            stri = data["payload"]
            print(f"[STR] {addr} : {stri}")

        elif msg_type == "int" :
            ints = data["payload"]
            print(f"[INT] {addr} : {ints}")

        elif msg_type == "bool" :
            bools = data["payload"]
            print(f"[BOOL] {addr} : {bools}")

        elif msg_type == "float":
            flot = data["payload"]
            print(f"[FLOAT] {addr} : {flot}")

    except json.JSONDecodeError:
        print(f"[ERROR] {addr} : {msg}")



def disconnect (client):
    print(f"[STOP] client disconnected")
    client.close()

def send_client (msg, client):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

def send_list(lst, client):
    data = json.dumps({"type": "list", "payload": lst})
    send_client(data, client)

def send_dict(dic, client):
    data = json.dumps({"type": "dict", "payload": dic})
    send_client(data, client)


def start(server):
    end = False
    broadcast_thread = threading.Thread(target=search_client, daemon=True)
    broadcast_thread.start()
    server.listen()
    print("[READY] the server is ready")
    while not end:
        client, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client, addr))
        thread.daemon =True
        thread.start()
        number_connected = threading.active_count()- 2
        print(f"[ACTIVE CLIENTS] {number_connected}\n")
    disconnect(server)

def server_running():
    print("[STARTING] the server is starting...")
    start(connect_client())
    print("[ENDING] the server is ending...")

server_running()