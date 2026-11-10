import re

with open(r'C:\Users\jvris\Downloads\pod-siksha\static\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

print(f'Total length of index.html: {len(text)} chars')

sections = re.findall(r'<section[^>]+id=["\']([^"\']+)["\']', text)
print('Section IDs:')
for s in sections:
    print(f'  - {s}')

all_ids = re.findall(r'id=["\']([^"\']+)["\']', text)
views = [i for i in all_ids if any(k in i.lower() for k in ['view', 'section', 'panel', 'screen', 'tab', 'modal', 'atelier', 'studio', 'desk', 'login', 'register'])]
print(f'\nRelevant View IDs ({len(views)}):')
for v in sorted(set(views)):
    print(f'  - {v}')
