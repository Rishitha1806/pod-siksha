import os
import json

env_dict = {}
with open(".env", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env_dict[k.strip()] = v.strip()

print(f"Loaded {len(env_dict)} environment variables from .env")
print("Keys:", list(env_dict.keys()))
