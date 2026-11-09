import urllib.request
import json

try:
    with urllib.request.urlopen("http://127.0.0.1:8008/api/health") as resp:
        data = json.loads(resp.read().decode())
        print("Health status:", resp.status, data)
except Exception as e:
    print("Health check failed:", e)

try:
    with urllib.request.urlopen("http://127.0.0.1:8008/") as resp:
        body = resp.read().decode()
        print("Root / status:", resp.status, f"Length: {len(body)}", "Title in body:", "Pod-Siksha 2.0 — Aura Atelier" in body)
except Exception as e:
    print("Root / check failed:", e)
