import json

env_dict = {}
with open(".env", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env_dict[k.strip()] = v.strip()

env_vars = []
for k, v in env_dict.items():
    env_vars.append({
        "key": k,
        "value": v,
        "target": ["production", "preview", "development"],
        "type": "encrypted"
    })

req = {
    "teamId": "team_GG8T38nijMGiwwRk56XNzfuO",
    "requestBody": {
        "name": "pod-siksha-2",
        "framework": None,
        "environmentVariables": env_vars
    }
}

with open("scratch_create_project.json", "w", encoding="utf-8") as f:
    json.dump(req, f, indent=2)

print("Saved scratch_create_project.json")
