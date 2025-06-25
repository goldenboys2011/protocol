import socket
import json
from websockets.sync.client import connect
import public_ip as ip

def connectToPeer(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))

        # Handshake
        handshake = {
            "sender": "192.168.1.200",
            "request": "handshake",
            "message": "connect"
        }
        s.sendall(json.dumps(handshake).encode() + b'\n')
        handshake_response = s.recv(1024).decode().strip()
        print("Handshake:", handshake_response)

        response = json.loads(handshake_response)
        if response.get("message") == "accept":

            request = {
                "sender": "192.168.1.200",
                "request": "get",
                "message": "index.html"
            }
            s.sendall(json.dumps(request).encode() + b'\n')
            print("Data:", s.recv(2048).decode().strip())
        elif response.get("message") == "refuse":
            print("Connection Refused")
        else:
            print("Connection Closed")

def askServerForIp(uuid):
    global ClientUUid

    with connect("ws://localhost:8765") as websocket:

        websocket.send(f"connect:{ip.get()}")

        message = websocket.recv()
        message = message.strip()
        mParts = message.split(":")

        ClientUUid = mParts[1]
        print(mParts[1])

if __name__ == "__main__":
    ClientUUid = ""
    ip = askServerForIp("irn")
    connectToPeer("37.27.51.34", 9001)
