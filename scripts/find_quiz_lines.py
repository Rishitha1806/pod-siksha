import re

with open(r"C:\Users\jvris\Downloads\pod-siksha\server.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "/api/quiz" in line or "/api/audio" in line or "/api/student" in line or "/api/teacher" in line or "/api/dashboard" in line:
        print(f"Line {i+1}: {line.strip()}")
