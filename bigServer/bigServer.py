"Big Server / DNS"

import socket
import threading
import json
import ssl

CERT_FILE = "cert.pem"
KEY_FILE = "key.pem"
MAP_FILE = "map.json"
map_lock = threading.Lock()

def load_map():
    try:
        with open(MAP_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"domains": {}}

def handle_client(conn, addr):
    print(f"[+] Connection from {addr}")
    
    # Load map at start of client session
    with map_lock:
        data_map = load_map()

    while True:
        try:
            data = conn.recv(2048).decode().strip()
            if not data:
                break

            print(f"[{addr}] Raw: {data}")
            try:
                request = json.loads(data)
            except json.JSONDecodeError:
                conn.sendall(json.dumps({"message": "invalid json"}).encode() + b'\n')
                continue

            req_type = request.get("request")

            if req_type == "get":
                with map_lock:
                    if request.get("type") == "dns":
                        full_domain = request.get("server", "")
                        parts = full_domain.split('.')

                        if len(parts) < 3:
                            # No Subdomain

                            subdomain = None
                            domain = full_domain
                        elif len(parts) > 3:
                            # Invalid

                            conn.sendall(json.dumps({"message": "invalid domain format"}).encode() + b'\n')
                        else:
                            # Subdomain | Extract that shit :D

                            subdomain, *domain_parts = parts
                            domain = '.'.join(domain_parts)

                        domain_info = data_map["domains"].get(domain)

                        if domain_info:
                            key = subdomain if subdomain else "@"
                            records = domain_info.get(key)
                            if records:
                                try:
                                    conn.sendall(json.dumps(records).encode() + b'\n')
                                except Exception as e:
                                    print(f"Failed to send records: {e}")
                                    conn.sendall(json.dumps({"message": "internal server error"}).encode() + b'\n')
                            else:
                                conn.sendall(json.dumps({
                                    "message": "Subdomain not found" if subdomain else "No records found",
                                    "ip": None
                                }).encode() + b'\n')
                        else:
                            conn.sendall(json.dumps({"message": "Domain not found", "ip": None}).encode() + b'\n')
                    else:
                        conn.sendall(json.dumps({"message": "Invalid get type"}).encode() + b'\n')


            else:
                conn.sendall(json.dumps({"message": "unknown request"}).encode() + b'\n')

        except ConnectionResetError:
            break

    print(f"[-] Disconnected {addr}")
    conn.close()

def start_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('0.0.0.0', 9002))
        sock.listen()

        with context.wrap_socket(sock, server_side=True) as ssock:
            print("Big server listening on port 9002")
            while True:
                conn, addr = ssock.accept()
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    start_server()
