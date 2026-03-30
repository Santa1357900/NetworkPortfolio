import socket
import threading
import time
import random
import sys

from message_queue import Message, MessageQueue
import config

PORT = int(sys.argv[1])
NEIGHBORS = [int(p) for p in sys.argv[2:]]

queue = MessageQueue()

def log(msg):
    print(f"[Node {PORT}] {msg}")

def handle_client(conn):
    data = conn.recv(config.BUFFER_SIZE).decode()
    if not data:
        return

    msg = Message.decode(data)

    if queue.add(msg):
        log(f"Received '{msg.content}' (TTL={msg.ttl}) from Node {msg.source}")

    conn.close()

def server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((config.HOST, PORT))
    s.listen(5)

    log("Server started...")

    while True:
        conn, _ = s.accept()
        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()

def send_loop():
    while True:
        time.sleep(config.RETRY_INTERVAL)

        for neighbor in NEIGHBORS:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((config.HOST, neighbor))

                for msg in queue.get_all():
                    if msg.ttl <= 0:
                        continue

                    if random.random() < config.FORWARD_PROBABILITY:
                        new_msg = Message(msg.content, msg.source, msg.ttl - 1)
                        new_msg.id = msg.id

                        s.send(new_msg.encode().encode())
                        log(f"Forward '{msg.content}' -> Node {neighbor} (TTL={new_msg.ttl})")

                s.close()

            except:
                log(f"Node {neighbor} unreachable")

def main():
    if PORT == 8001:
        msg = Message("Hello Opportunistic Network!", PORT, config.TTL)
        queue.add(msg)

    threading.Thread(target=server, daemon=True).start()
    threading.Thread(target=send_loop, daemon=True).start()

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()