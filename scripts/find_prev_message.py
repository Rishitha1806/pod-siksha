import json

with open(r'C:\Users\jvris\.gemini\antigravity\brain\23d34354-39ca-40f8-aad7-0b7b2c82bbc3\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    data = json.loads(line)
    if data.get('content') and 'Yes done' in str(data.get('content')):
        print(f"Found 'Yes done' at line {i}")
        # print the previous planner response
        for j in range(i-1, max(0, i-10), -1):
            prev = json.loads(lines[j])
            if prev.get('source') == 'MODEL' and prev.get('type') == 'PLANNER_RESPONSE':
                print("PREVIOUS MODEL MESSAGE:")
                print(prev.get('content').encode('ascii', 'replace').decode('ascii'))
                break
        break
