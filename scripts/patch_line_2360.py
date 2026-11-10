with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = 'cached_time = datetime.strptime(cached["created_at"], "%Y-%m-%d %H:%M:%S")'
replacement = '''if isinstance(cached["created_at"], str):
                    cached_time = datetime.strptime(cached["created_at"].split(".")[0], "%Y-%m-%d %H:%M:%S")
                else:
                    cached_time = cached["created_at"].replace(tzinfo=None) if hasattr(cached["created_at"], 'tzinfo') and cached["created_at"].tzinfo else cached["created_at"]'''

assert target in content, 'Target not found'
content = content.replace(target, replacement, 1)

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Patched datetime parsing on line 2360!')
