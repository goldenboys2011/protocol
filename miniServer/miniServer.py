import os
import socket
import threading
import json
import ssl
import public_ip

CERT_FILE = "cert.pem"
KEY_FILE = "key.pem"

def handle_client(conn, addr):
    print(f"[+] Connection from {addr}")

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

            if request.get("request") == "handshake":
                conn.sendall(json.dumps({"message": "accept"}).encode() + b'\n')

            elif request.get("request") == "get":
                requested_file = request.get("message", "")
                base_path = "fileSystem"

                safe_path = os.path.normpath(os.path.join(base_path, requested_file))

                if not safe_path.startswith(base_path):
                    response = {
                        "code": 403,
                        "message": "forbidden"
                    }
                else:
                    try:
                        with open(safe_path, "r") as f:
                            response = {
                                "code": 200,
                                "message": f.read()
                            }
                    except FileNotFoundError:
                        response = {
                            "code": 404,
                            "message": "not found"
                        }
                    except Exception as e:
                        response = {
                            "code": 500,
                            "message": f"internal error: {str(e)}"
                        }
                conn.sendall(json.dumps(response).encode() + b'\n')

            else:
                conn.sendall(json.dumps({"message": "unknown request"}).encode() + b'\n')

        except ConnectionResetError:
            break

    print(f"[-] Disconnected {addr}")
    conn.close()




def start_server():
    global context
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('0.0.0.0', 9001))
        sock.listen()

        with context.wrap_socket(sock, server_side=True) as ssock:
            print("Server listening on port 9001")
            while True:
                conn, addr = ssock.accept()
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    bigserver_sock = None
    publicIp = public_ip.get()

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    start_server()