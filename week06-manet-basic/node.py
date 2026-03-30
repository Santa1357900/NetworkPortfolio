import socket
import threading
import random
import sys
from config import HOST, BUFFER_SIZE, FORWARD_PROBABILITY, TTL

PORT = int(sys.argv[1])
NEIGHBORS = list(map(int, sys.argv[2:]))

neighbor_table = set(NEIGHBORS)
seen_messages = set()

def handle_incoming(conn, addr):
    data = conn.recv(BUFFER_SIZE).decode()
    conn.close()

    try:
        msg_id, msg, ttl = data.split('|')
        ttl = int(ttl)
    except:
        return

    if msg_id in seen_messages:
        return

    seen_messages.add(msg_id)

    print(f"[NODE {PORT}] From {addr}: {msg} (TTL={ttl})")

    if ttl > 0 and random.random() < FORWARD_PROBABILITY:
        forward_message(msg_id, msg, ttl - 1)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except:
        pass

    server.bind((HOST, PORT))
    server.listen()

    print(f"[NODE {PORT}] Listening...")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_incoming, args=(conn, addr), daemon=True).start()

def forward_message(msg_id, message, ttl):
    for peer_port in neighbor_table:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, peer_port))
            s.sendall(f"{msg_id}|{message}|{ttl}".encode())
            s.close()
        except:
            pass

if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()

    msg_id = str(random.randint(100000, 999999))
    message = f"Hello from node {PORT}"
    forward_message(msg_id, message, TTL)

    while True:
        pass