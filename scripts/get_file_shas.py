import hashlib
import os

def get_file_info(rel_path):
    full_path = os.path.join(r"C:\Users\jvris\Downloads\pod-siksha", rel_path)
    with open(full_path, "rb") as f:
        data = f.read()
    sha1 = hashlib.sha1(data).hexdigest()
    size = len(data)
    print(f"{rel_path}: sha1={sha1}, size={size}")
    return sha1, size

get_file_info("server.py")
get_file_info("static/index.html")
get_file_info("static/report.html")
get_file_info("static/teacher.html")
get_file_info("requirements.txt")
get_file_info("vercel.json")
get_file_info("api/index.py")
