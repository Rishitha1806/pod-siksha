with open('tests/test_v2_features.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("from db_adapter import get_db\n", "")
sys_code = """import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_adapter import get_db
"""
content = sys_code + content

with open('tests/test_v2_features.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed sys.path in test_v2_features.py!")
