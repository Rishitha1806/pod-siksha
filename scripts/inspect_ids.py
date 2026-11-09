import re

with open(r"C:\Users\jvris\Downloads\pod-siksha\static\index.html", "r", encoding="utf-8") as f:
    text = f.read()

ids = re.findall(r'id=["\']([^"\']+)["\']', text)
print("Found IDs in static/index.html:")
for i in sorted(set(ids)):
    print(f" - {i}")
