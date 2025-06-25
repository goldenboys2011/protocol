import socket

HOST = '127.0.0.1'  # Server IP or hostname
PORT = 12345        # Server port

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print(f"Connected to server at {HOST}:{PORT}")

        while True:
            msg = input("Enter message (or 'quit'): ")
            if msg.lower() == 'quit':
                break

            s.sendall(msg.encode('utf-8'))
            data = s.recv(1024)
            print('Received:', data.decode('utf-8').strip())

if __name__ == "__main__":
    main()
