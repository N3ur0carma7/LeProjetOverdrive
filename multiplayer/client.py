import socket
import time
import json

HEADER = 64
PORT = 5050
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "[DISCONNECT]"
IP_server = ""
def search_serv():
    TIMOUT_RESEARCH = 100
    debut = time.time()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("[INFO] Socket created\n")
    print("[RESEARCH] server researching")
    s.settimeout(1.0)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s_addr = None
    while time.time() - debut < TIMOUT_RESEARCH and s_addr is None:
        try:
            s.sendto("searching...".encode(),   ("255.255.255.255", 5051))
            s_data, s_addr = s.recvfrom(1024)
            print(f"[SERVER] {s_addr} found...")
            print(f"[SERVER] {s_data.decode()} recieved\n")
        except socket.timeout:
            pass
        time.sleep(0.2)
    s.close()
    if s_addr is None :
        return -1
    else:
        return s_addr[0]

def handle_message_client(msg, client):
    try:
        data = json.loads(msg)
        msg_type = data.get("type")

        if msg_type == "list":
            liste = data["payload"]
            print(f"[LIST] server has send a list: {liste}")
            return liste

        elif msg_type == "dict":
            obj = data["payload"]
            print(f"[DICT] server has send a ditionary: {obj}")
            return obj

        elif msg_type == "tuple":
            tup =data["payload"]
            print(f"[TUPLE] server has send a tuple: {tup}")
            return tup

        elif msg_type == "str" :
            stri = data["payload"]
            print(f"[STR] server has send : {stri}")
            return stri

        elif msg_type == "int" :
            ints = data["payload"]
            print(f"[INT] server has send : {ints}")
            return ints

        elif msg_type == "bool" :
            bools = data["payload"]
            print(f"[BOOL] server has send : {bools}")
            return bools

        elif msg_type == "float":
            flot = data["payload"]
            print(f"[FLOAT] server has send : {flot}")
            return flot

        else:
            print(f"[UNKNOWN JSON] server: {data}")
            return None

    except json.JSONDecodeError:
        print(f"[TEXT] server: {msg}")

def recieved_client(client):
    try:
        msg_len_str = client.recv(HEADER).decode(FORMAT).strip()
        if not msg_len_str:
            return None
        msg_len = int(msg_len_str)
        msg = client.recv(msg_len).decode(FORMAT)

        if msg == DISCONNECT_MESSAGE:
            return None
        return handle_message_client(msg, client)

    except:
        return None

def send_server (msg, client):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

def send_list (lst, client):
    data = json.dumps({"type": "list", "payload": lst})
    send_server(data, client)

def send_tuple(tup, client):
    data = json.dumps({"type": "tuple", "payload": list(tup)})
    send_server(data, client)

def send_dict(dic, client):
    data = json.dumps({"type": "dict", "payload": dic})
    send_server(data, client)


def connection():
    global IP_server
    SERVER = search_serv()
    if SERVER == -1:
        print("[NOT FOUND] server not found")
        return -1
    IP_server = SERVER
    ADDR = (SERVER, PORT)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f"[SERVER] {SERVER} connected")
    send_dict({"test": "hello"}, client)
    while True:
        data = recieved_client(client)
        if data is not None:
            print(">>> Donnée reçue :", data)

connection()