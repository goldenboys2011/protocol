from websockets.sync.server import serve
import uuid
import json
import os

def echo(websocket):
    for message in websocket:
        message = message.strip()

        if message.startswith("connect:"):
            parts = message.split(":")
            client_ip = parts[1]
            client_uuid = str(uuid.uuid4())

            if os.path.exists("map.json"):
                with open("map.json", "r") as f:
                    data = json.load(f)
            else:
                data = { "nodes": [] }

            data["nodes"].append({
                "ip": client_ip,
                "uuid": client_uuid
            })

            with open("map.json", "w") as f:
                json.dump(data, f, indent=2)

            websocket.send(f"{client_ip}:{client_uuid}")

        elif message.startswith("discconect:"):
            websocket.send("disconnected")

        else:
            websocket.send(message)

def main():
    with serve(echo, "localhost", 8765) as server:
        server.serve_forever()

if __name__ == "__main__":
    main()
