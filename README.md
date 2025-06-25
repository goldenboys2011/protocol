# ORO Protocol

> A mini DNS-like protocol for decentralized IP lookups and peer connection

[![version](https://img.shields.io/badge/version-0.1-green.svg)](https://github.com/goldenboys2011/GoldenDNS/releases/tag/0.1)  
[![discord](https://img.shields.io/badge/Discord-join-7289DA.svg)](https://discord.gg/yPpfjwNzVy)  
[![license](https://img.shields.io/badge/License-GPL_3.0-blue.svg)](https://github.com/goldenboys2011/GoldenDNS/blob/main/LICENSE)

---

## Protocol Overview

GoldenDNS is a lightweight DNS-style protocol for looking up peer IPs using domain names.  
Instead of relying on traditional DNS, it uses a JSON-based map hosted on a custom TLS server.

Supports:
- `A` records (IPv4 address)
- `TXT` records (any text info)

---

## Structure

Your `map.json` looks like this:

```json
{
  "domains": {
    "gboogle.yab": {
      "secret": "superSecretHere",
      "@": [
        {"type": "A", "content": "127.0.0.1"},
        {"type": "TXT", "content": "Yo Internet"}
      ],
      "dev": [
        {"type": "A", "content": "127.0.0.2"}
      ]
    }
  }
}
```

---

## Server Querying

A client can query the main DNS server via a simple `GET` request:

```json
{
  "sender": "yourPublicIpHere",
  "request": "get",
  "type": "dns",
  "server": "gboogle.yab"
}
```

### Response:

```json
{
        {"type": "A", "content": "127.0.0.1"},
        {"type": "TXT", "content": "Yo Internet"}
}
```

Or if you ask for a subdomain:

- `dev.gboogle.yab` returns all records under `"dev"` in the domain entry

---

## Supported Record Types

| Type | Description         |
|------|---------------------|
| `A`  | IPv4 Address (string) |
| `TXT` | Any metadata/text |

Only these are supported for now, but extensible later (e.g. `MX`, `AAAA`, etc.)

---

## Authentication

Each domain entry contains a `secret` key.  
This is required for modifying or updating records (not for lookups).

Use this to protect your zone data from unauthorized changes.

---

## Example Usage

```python
Serverip = askServerForIp("gboogle.yab", "dns")
connectToPeer(Serverip, 9001)
```

---

## Installation

1. Clone the repo
2. Run the main server:
   ```bash
   python3 bigServer.py
   ```
3. Add domains to `map.json`
4. Connect using a compatible client

---

## To-Do

- [x] A & TXT support
- [ ] DNS record editing via API
- [ ] TTL support
- [ ] Web UI to manage domains

---

Built by Odysseas Chryssos (golden)
