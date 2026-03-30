import socket
import threading
import time
import sys
from config import HOST, BUFFER_SIZE, RETRY_INTERVAL
from message_queue import MessageQueue

PORT = int(sys.argv[1])
PEERS = list(map(int, sys.argv[2:]))

queue = MessageQueue()

def send_message(peer_port, message):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((HOST, peer_port))
        s.sendall(message.encode())
        s.close()
        return True
    except:
        return False

def forward_loop():
    while True:
        for msg in queue.get_messages():
            success = send_message(msg["peer"], msg["message"])
            if success:
                print(f"[NODE {PORT}] Sent stored message to {msg['peer']}")
                queue.remove_message(msg)
        time.sleep(RETRY_INTERVAL)

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
        data = conn.recv(BUFFER_SIZE).decode()
        print(f"\n[NODE {PORT}] Received: {data} from {addr}")
        conn.close()

def input_loop():
    while True:
        try:
            target = int(input("Send to port: ").strip())
            msg = input("Message: ").strip()

            if not send_message(target, msg):
                print(f"[NODE {PORT}] Peer {target} unavailable, storing message")
                queue.add_message(msg, target)

        except ValueError:
            print("Invalid input")

if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=forward_loop, daemon=True).start()
    input_loop()