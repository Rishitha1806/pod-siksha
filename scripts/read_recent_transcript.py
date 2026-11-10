import json

with open(r'C:\Users\jvris\.gemini\antigravity\brain\23d34354-39ca-40f8-aad7-0b7b2c82bbc3\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data.get('source') in ('USER_EXPLICIT', 'MODEL') and data.get('type') in ('USER_INPUT', 'PLANNER_RESPONSE'):
            c = str(data.get('content'))
            if c != 'None':
                print(f"{data.get('source')} ({data.get('type')}): {c[:300]}\n---")
