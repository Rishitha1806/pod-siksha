import json

env_dict = {}
with open(".env", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env_dict[k.strip()] = v.strip()

items = []
for k, v in env_dict.items():
    items.append({
        "key": k,
        "value": v,
        "type": "encrypted",
        "target": ["production", "preview", "development"]
    })

payload = {
    "idOrName": "prj_qOPVf0xD3dK0VFxBwxuXQIKGWgAe",
    "teamId": "team_GG8T38nijMGiwwRk56XNzfuO",
    "upsert": "true",
    "requestBody": items
}

with open("scratch_envs_payload.json", "w", encoding="utf-8") as f:
    json.dump(payload, f)

print(f"Prepared {len(items)} env variables in scratch_envs_payload.json")
