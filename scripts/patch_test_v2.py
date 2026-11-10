with open('tests/test_v2_features.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add get_db import
if 'from db_adapter import get_db' not in content:
    content = "from db_adapter import get_db\n" + content

# Replace sqlite3.connect(DB_PATH) with get_db()
content = content.replace("sqlite3.connect(DB_PATH)", "get_db()")

with open('tests/test_v2_features.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated test_v2_features.py to use get_db()!")
