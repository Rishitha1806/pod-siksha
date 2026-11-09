import re

with open(r"C:\Users\jvris\Downloads\pod-siksha\server.py", "r", encoding="utf-8") as f:
    text = f.read()

endpoints = re.findall(r'@app\.(get|post|delete|patch|put)\(["\']([^"\']+)["\']', text)
print(f"Total endpoints found: {len(endpoints)}")
for method, path in endpoints:
    print(f"{method.upper():6} {path}")
