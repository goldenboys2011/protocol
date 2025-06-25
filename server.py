import socket
import threading

HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 12345      # Port to listen on

clients = {}  # Map client socket to client ID (simple)

def handle_client(conn, addr):
    print(f"New connection from {addr}")
    client_id = addr[1]  # use port as a simple client ID

    clients[conn] = client_id
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode('utf-8').strip()
            print(f"Received from {client_id}: {message}")

            # Echo message back with some simple protocol wrapper
            response = f"Server got your message: {message}\n"
            conn.sendall(response.encode('utf-8'))

    except ConnectionResetError:
        print(f"Connection lost from {client_id}")
    finally:
        print(f"Closing connection from {client_id}")
        del clients[conn]
        conn.close()

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
