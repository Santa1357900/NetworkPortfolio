import socket
import threading
import random
import time
import uuid

# ================= CONFIG =================
HOST = "127.0.0.1"
PORT = int(__import__("sys").argv[1])
NEIGHBORS = list(map(int, __import__("sys").argv[2:]))

ALPHA = 1.2
EVAPORATION = 0.05
REWARD = 0.5
PENALTY = 0.4
EXPLORATION_RATE = 0.2
MAX_PHEROMONE = 5.0

# ================= STATE =================
pheromone = {n: 1.0 for n in NEIGHBORS}
seen_messages = set()
buffer = []

# ================= SELECT NEXT NODE =================
def select_neighbor():
    # Exploration
    if random.random() < EXPLORATION_RATE:
        return random.choice(NEIGHBORS)

    weights = [pheromone[n] ** ALPHA for n in NEIGHBORS]
    total = sum(weights)

    r = random.random() * total
    cum = 0

    for i, n in enumerate(NEIGHBORS):
        cum += weights[i]
        if r <= cum:
            return n

    return random.choice(NEIGHBORS)

# ================= UPDATE PHEROMONE =================
def update_pheromone(node, success):
    if success:
        pheromone[node] = min(MAX_PHEROMONE, pheromone[node] + REWARD)
    else:
        pheromone[node] = max(0.1, pheromone[node] - PENALTY)

# ================= EVAPORATION =================
def evaporate():
    while True:
        time.sleep(3)
        for n in pheromone:
            pheromone[n] *= (1 - EVAPORATION)

# ================= SEND MESSAGE =================
def send_message(target, message):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((HOST, target))
        s.sendall(message.encode())
        s.close()
        return True
    except:
        return False

# ================= FORWARD =================
def forward(msg, ttl, msg_id):
    if ttl <= 0:
        return

    next_node = select_neighbor()

    success = send_message(next_node, f"{msg}|{ttl-1}|{msg_id}")

    if success:
        update_pheromone(next_node, True)
        print(f"[Node {PORT}] → {next_node} TTL={ttl} Pheromone={round(pheromone[next_node],2)}")
    else:
        update_pheromone(next_node, False)
        buffer.append((msg, ttl, msg_id))
        print(f"[Node {PORT}] ✗ {next_node} FAIL Pheromone={round(pheromone[next_node],2)}")

# ================= HANDLE CLIENT =================
def handle_client(conn):
    data = conn.recv(1024).decode()
    conn.close()

    try:
        msg, ttl, msg_id = data.split("|")
        ttl = int(ttl)
    except:
        return

    if msg_id in seen_messages:
        return

    seen_messages.add(msg_id)

    print(f"[Node {PORT}] Received '{msg}' TTL={ttl}")

    forward(msg, ttl, msg_id)

# ================= SERVER =================
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[Node {PORT}] Running...")

    while True:
        conn, _ = server.accept()
        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()

# ================= RETRY BUFFER =================
def retry_buffer():
    while True:
        time.sleep(5)
        if buffer:
            msg, ttl, msg_id = buffer.pop(0)
            print(f"[Node {PORT}] 🔁 Retrying...")
            forward(msg, ttl, msg_id)

# ================= GENERATE TRAFFIC =================
def generate_traffic():
    while True:
        time.sleep(4)
        msg_id = str(uuid.uuid4())
        forward("Bio Inspired Data", 4, msg_id)

# ================= MAIN =================
if __name__ == "__main__":
    threading.Thread(target=evaporate, daemon=True).start()
    threading.Thread(target=retry_buffer, daemon=True).start()
    threading.Thread(target=generate_traffic, daemon=True).start()
    start_server()