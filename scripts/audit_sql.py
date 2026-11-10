import re

with open('server.py', 'r', encoding='utf-8') as f:
    text = f.read()

sqls = re.findall(r'execute\(\s*"""(.*?)"""', text, re.DOTALL)
sqls += re.findall(r'execute\(\s*"([^"]+)"', text)
sqls += re.findall(r"execute\(\s*'([^']+)'", text)

print(f"Total SQL statements detected: {len(sqls)}")
special_words = ['strftime', 'julianday', 'glob', 'instr', 'random', 'json_extract', 'autoincrement', 'pragma', 'datetime(']
for s in sqls:
    for word in special_words:
        if word in s.lower():
            print(f"[{word}] in: {s.strip()[:100]}")
