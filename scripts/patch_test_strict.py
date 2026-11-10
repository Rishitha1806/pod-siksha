with open('tests/test_strict_access_control.py', 'r', encoding='utf-8') as f:
    content = f.read()

sys_code = """import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_adapter import get_db
"""
content = sys_code + content
content = content.replace("sqlite3.connect(DB_PATH)", "get_db()")

with open('tests/test_strict_access_control.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated test_strict_access_control.py to use get_db()!")
