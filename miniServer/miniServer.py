import os
import socket
import threading
import json

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

                # Prevent path traversal like "../../../etc/passwd"
                safe_path = os.path.normpath(os.path.join(base_path, requested_file))

                # Ensure the requested file stays within base_path
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

def start_server(host="0.0.0.0", port=9001):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()

    print(f"[SERVER] Listening on {host}:{port}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
