import socket
import threading
import json
import time
import ast

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

SERVER = connect_client()

def tuple_from_str(key_str):
    if not(isinstance(key_str, str) and key_str.startswith('(') and key_str.endswith(')')):
        return key_str
    try:
        content = key_str[1:-1]
        return ast.literal_eval(f"({content})")
    except:
        return key_str


def str_to_tuple_key(dic):
    result = {}
    for k, v in dic.items():
        result[tuple_from_str(k)] = v
    return result

def handle_client(client, addr):
    print(f"[NEW CLIENT] {addr} connected\n")
    clients[addr] = client
    send_dict_server({"server": "hello client"}, client)
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
                message, type = handle_message_recieved(msg, addr)
                for i in clients.keys():
                    if i != addr:
                        if type == "list":
                            send_list_server(message, clients[i])
                        elif type == "dict":
                            data = json.dumps({"type": "str", "payload": "bien reÃ§u"})
                            send_client(data, clients[i])
                            send_dict_tuple_server(message, clients[i])
                            print(f"envoyer a {clients[i]}")
                        elif type == "str":
                            send_str_server(message, clients[i])
                        elif type == "int":
                            send_int_server(message, clients[i])
                        elif type == "bool":
                            send_bool_server(message, clients[i])
                        elif type == "float":
                            send_float_server(message, clients[i])
                        elif type == "tuple":
                            send_tuple_server(message, clients[i])


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
            return liste, msg_type

        elif msg_type == "dict":
            raw_dic = data["payload"]
            dic = str_to_tuple_key(raw_dic)
            print(f"[DICT] {addr} : {dic}")
            return dic, msg_type

        elif msg_type == "tuple":
            tup = data["payload"]
            print(f"[TUP] {addr} : {tup}")
            return tup

        elif msg_type == "str" :
            stri = data["payload"]
            print(f"[STR] {addr} : {stri}")
            return stri

        elif msg_type == "int" :
            ints = data["payload"]
            print(f"[INT] {addr} : {ints}")
            return ints

        elif msg_type == "bool" :
            bools = data["payload"]
            print(f"[BOOL] {addr} : {bools}")
            return bools

        elif msg_type == "float":
            flot = data["payload"]
            print(f"[FLOAT] {addr} : {flot}")
            return flot

    except json.JSONDecodeError:
        print(f"[ERROR] {addr} : {msg}")
        return ""



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

def send_list_server(lst, client):
    data = json.dumps({"type": "list", "payload": lst})
    send_client(data, client)

def send_dict_server(dic, client):
    data = json.dumps({"type": "dict", "payload": dic})
    send_client(data, client)

def dict_keys_to_str_server(dic):
    result = {}
    for k, v in dic.items():
        result[str(k)] = v
    return result

def send_dict_tuple_server(dict_tuple, client):
    dic = dict_keys_to_str_server(dict_tuple)
    data = json.dumps({"type": "dict", "payload": dic})
    send_client(data, client)

def send_str_server (str, client):
    data = json.dumps({"type": "str", "payload": str})
    send_client(data, client)

def send_int_server (int, client):
    data = json.dumps({"type": "int", "payload": int})
    send_client(data, client)

def send_bool_server (bool, client):
    data = json.dumps({"type": "bool", "payload": bool})
    send_client(data, client)

def send_float_server (float, client):
    data = json.dumps({"type": "float", "payload": float})
    send_client(data, client)


def send_tuple_server(tup, client):
    data = json.dumps({"type": "tuple", "payload": list(tup)})
    send_client(data, client)

def disconnect_server():
    global SERVER
    SERVER.close()


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
        number_connected = len(clients)
        print(f"[ACTIVE CLIENTS] {number_connected}\n")

        if number_connected == 0:
            break
    disconnect_server()

def server_running():
    print("[STARTING] the server is starting...")
    start(SERVER)
    print("[ENDING] the server is ending...")