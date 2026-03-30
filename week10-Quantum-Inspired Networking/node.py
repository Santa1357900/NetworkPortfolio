import sys
import threading
import uuid
import time
import hashlib
from network import send_packet, start_server

PORT = int(sys.argv[1])
NEIGHBORS = list(map(int, sys.argv[2:]))

class QuantumSecurity:
    def __init__(self):
        self.valid_tokens = {}
        self.used_tokens = set()
        self.lifetime = 60

    def generate(self):
        t = str(uuid.uuid4())[:8]
        self.valid_tokens[t] = time.time() + self.lifetime
        return t

    def verify(self, t):
        if t in self.used_tokens or t not in self.valid_tokens:
            return False
        if time.time() > self.valid_tokens[t]:
            return False
        return True

    def consume(self, t):
        self.used_tokens.add(t)
        if t in self.valid_tokens:
            del self.valid_tokens[t]

security = QuantumSecurity()
seen_messages = set()

def compute_hash(msg, token):
    return hashlib.sha256((msg + token).encode()).hexdigest()

def handle_client(conn):
    try:
        data = conn.recv(1024).decode()
        conn.close()
        msg, msg_id, token, h = data.split("|")
        
        if msg_id in seen_messages:
            return
        
        if compute_hash(msg, token) != h:
            print(f"\n[NODE {PORT}] Tampered Data!")
            return

        print(f"\n[NODE {PORT}] Consumed token: {msg}")
        seen_messages.add(msg_id)
        print(f"[NODE {PORT}] Enter message (or blank to exit): ", end="", flush=True)
    except:
        pass

def user_input_loop():
    while True:
        msg = input(f"[NODE {PORT}] Enter message (or blank to exit): ")
        if not msg:
            continue
        
        for n in NEIGHBORS:
            token = security.generate()
            msg_id = str(uuid.uuid4())
            h = compute_hash(msg, token)
            packet = f"{msg}|{msg_id}|{token}|{h}"
            
            if send_packet(n, packet):
                print(f"[NODE {PORT}] Sent token to {n}")
            else:
                print(f"[NODE {PORT}] FAIL to send to {n}")

if __name__ == "__main__":
    threading.Thread(target=user_input_loop, daemon=True).start()
    start_server(PORT, handle_client)