from flask import Flask, request, jsonify, render_template, send_from_directory
import ssl, json, threading
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

MAP_FILE = "map.json"
USER_FILE = "users.json"
map_lock = threading.Lock()
user_lock = threading.Lock()

def load_json(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/specs/<path:filename>")
def specs_static(filename):
    return send_from_directory("static/specs", filename)


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username, password = data.get("username"), data.get("password")
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    with user_lock:
        users = load_json(USER_FILE, {})
        if username in users:
            return jsonify({"error": "Username exists"}), 400
        users[username] = generate_password_hash(password)
        save_json(USER_FILE, users)

    return jsonify({"message": "User created"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username, password = data.get("username"), data.get("password")
    with user_lock:
        users = load_json(USER_FILE, {})
        if username not in users or not check_password_hash(users[username], password):
            return jsonify({"error": "Invalid credentials"}), 403
    return jsonify({"message": "Login successful", "user": username})  # Tokenizing optional

@app.route("/domains", methods=["GET", "POST"])
def domains():
    username = request.args.get("user")
    if not username:
        return jsonify({"error": "Unauthorized"}), 401

    with map_lock:
        data_map = load_json(MAP_FILE, {"domains": {}})
        domains = data_map["domains"]

        if request.method == "GET":
            user_domains = {
                name: info for name, info in domains.items()
                if info.get("owner") == username
            }
            return jsonify(user_domains)

        elif request.method == "POST":
            req = request.json
            domain_name = req.get("domain")
            ip = req.get("ip")

            if not domain_name or not ip:
                return jsonify({"error": "Domain and IP required"}), 400
            if domain_name in domains:
                return jsonify({"error": "Domain already exists"}), 409

            secret = generate_password_hash(domain_name + username)
            domains[domain_name] = {
                "owner": username,
                "secret": secret,
                "ip": ip,
                "@": [ { "type": "A", "content": ip } ]
            }
            save_json(MAP_FILE, data_map)
            return jsonify({"message": "Domain created", "secret": secret}), 201


@app.route("/domains/<domain>/records", methods=["POST"])
def edit_records(domain):
    username = request.args.get("user")
    if not username:
        return jsonify({"error": "Unauthorized"}), 401

    with map_lock:
        data_map = load_json(MAP_FILE, {"domains": {}})
        domain_data = data_map["domains"].get(domain)

        if not domain_data or domain_data.get("owner") != username:
            return jsonify({"error": "Not found or forbidden"}), 403

        data = request.json
        record_type = data.get("type")
        content = data.get("content")
        subdomain = data.get("subdomain", "@")

        if not record_type or not content or record_type not in ["A", "TXT"]:
            return jsonify({"error": "Invalid input"}), 400

        if subdomain not in domain_data:
            domain_data[subdomain] = []

        # Replace record of same type if it exists, else add
        domain_data[subdomain] = [
            r for r in domain_data[subdomain] if r["type"] != record_type
        ]
        domain_data[subdomain].append({
            "type": record_type,
            "content": content
        })

        save_json(MAP_FILE, data_map)
        return jsonify({"message": f"{record_type} record for {subdomain}.{domain} updated"})


@app.route("/domains/<domain>", methods=["PUT", "DELETE"])
def edit_domain(domain):
    username = request.args.get("user")
    if not username:
        return jsonify({"error": "Unauthorized"}), 401

    with map_lock:
        data_map = load_json(MAP_FILE, {"domains": {}})
        domains = data_map["domains"]

        if domain not in domains or domains[domain].get("owner") != username:
            return jsonify({"error": "Not found or forbidden"}), 403

        domain_data = domains[domain]

        if request.method == "PUT":
            record_type = request.json.get("type")
            sub = request.json.get("subdomain", "@")
            content = request.json.get("content")

            if record_type not in ["A", "TXT"] or not content:
                return jsonify({"error": "Invalid record"}), 400

            if sub not in domain_data:
                domain_data[sub] = []

            # Replace existing record of same type or append new
            existing = [r for r in domain_data[sub] if r["type"] != record_type]
            existing.append({ "type": record_type, "content": content })
            domain_data[sub] = existing

            save_json(MAP_FILE, data_map)
            return jsonify({"message": f"Record updated for {sub}.{domain}"})

        elif request.method == "DELETE":
            del domains[domain]
            save_json(MAP_FILE, data_map)
            return jsonify({"message": "Domain deleted"})


def runHttpsServer():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain("cert.pem", "key.pem")
    app.run(host="0.0.0.0", port=9003, ssl_context=context)
