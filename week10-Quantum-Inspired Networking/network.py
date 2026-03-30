import socket

HOST = "127.0.0.1"

def send_packet(target_port, packet):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((HOST, target_port))
        s.sendall(packet.encode())
        s.close()
        return True
    except:
        return False

def start_server(port, handler):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, port))
    server.listen()
    print(f"[NODE {port}] Listening...")
    while True:
        conn, _ = server.accept()
        handler(conn)