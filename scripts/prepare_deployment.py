import os
import json
import base64

files = []

def add_file(rel_path, is_binary=False):
    full_path = os.path.join(r"C:\Users\jvris\Downloads\pod-siksha", rel_path)
    if not os.path.exists(full_path):
        print(f"File not found: {full_path}")
        return
    
    if is_binary:
        with open(full_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("ascii")
        files.append({
            "file": rel_path.replace("\\", "/"),
            "data": data,
            "encoding": "base64"
        })
    else:
        with open(full_path, "r", encoding="utf-8") as f:
            data = f.read()
        files.append({
            "file": rel_path.replace("\\", "/"),
            "data": data,
            "encoding": "utf-8"
        })
    print(f"Added {rel_path} ({os.path.getsize(full_path)} bytes)")

add_file("api/index.py")
add_file("server.py")
add_file("requirements.txt")
add_file("vercel.json")
add_file("static/index.html")
add_file("static/report.html")
add_file("static/teacher.html")

payload = {
    "teamId": "team_GG8T38nijMGiwwRk56XNzfuO",
    "requestBody": {
        "name": "pod-siksha-2",
        "project": "prj_qOPVf0xD3dK0VFxBwxuXQIKGWgAe",
        "target": "production",
        "files": files
    }
}

out_file = r"C:\Users\jvris\Downloads\pod-siksha\scratch_deploy_payload.json"
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(payload, f)

print(f"Generated deployment payload with {len(files)} files at {out_file} ({os.path.getsize(out_file)} bytes)")
