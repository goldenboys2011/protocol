import socket
import json
from websockets.sync.client import connect
import public_ip
import ssl

def connectToPeer(ip, port):
    global context
    global publicIp
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
         with context.wrap_socket(s, server_hostname=ip) as sc:
            sc.connect((ip, port))

            handshake = {
                "sender": publicIp,
                "request": "handshake",
                "message": "connect"
            }
            sc.sendall(json.dumps(handshake).encode() + b'\n')
            handshake_response = sc.recv(1024).decode().strip()
            print("Handshake:", handshake_response)

            response = json.loads(handshake_response)
            if response.get("message") == "accept":

                request = {
                    "sender": publicIp,
                    "request": "get",
                    "message": "index.html"
                }
                sc.sendall(json.dumps(request).encode() + b'\n')
                print("Data:", sc.recv(2048).decode().strip())
            elif response.get("message") == "refuse":
                print("Connection Refused")
            else:
                print("Connection Closed")

def askServerForIp(server, type):
    global context
    global publicIp
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        with context.wrap_socket(s, server_hostname="192.0.0.1") as sc:
            sc.connect(("127.0.0.1", 9002))

            getServer = {
                "sender": publicIp,
                "request": "get",
                "type": type,
                "server": server
            }

            sc.sendall(json.dumps(getServer).encode() + b'\n')
            file_like = sc.makefile('r')
            get_response = json.loads(file_like.readline().strip())
            print(get_response)

            if isinstance(get_response, list):
                for record in get_response:
                    if record.get("type") == "A":
                        return record.get("content")
                    
                return None
            elif isinstance(get_response, dict):

                return get_response.get("ip")
            else:
                return None




if __name__ == "__main__":
    context = ssl._create_unverified_context()
    publicIp = public_ip.get()
    Serverip = askServerForIp("gboogle.yab", "dns")
    #connectToPeer("37.27.51.34", 9001)
    if Serverip != None:
        print(Serverip)
        connectToPeer(Serverip, 9001)
    else:    
        print("Ip Not Found")
