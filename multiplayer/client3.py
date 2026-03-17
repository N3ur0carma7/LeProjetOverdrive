import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("[INFO] Socket created\n")
print("[RESEARCH] server researching")
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.sendto("searching...".encode(),   ("255.255.255.255", 5000))
s_data, s_addr = s.recvfrom(1024)
print(f"[SERVER] {s_addr} found...")
print(f"[SERVER] {s_data.decode()} recieved\n")

HEADER = 64
PORT = 5050
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "[DISCONNECT]"
SERVER = s_addr[0]
ADDR = (SERVER, PORT)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
print(f"[SERVER] {SERVER} connected")


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

send("hello world !")
input()
send(DISCONNECT_MESSAGE)
