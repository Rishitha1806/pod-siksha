import json

with open(r'C:\Users\jvris\.gemini\antigravity\brain\23d34354-39ca-40f8-aad7-0b7b2c82bbc3\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        idx = obj.get("step_index", 0)
        if 3787 <= idx <= 3795:
            print(f"=== Step {idx} ===")
            if "tool_calls" in obj:
                for tc in obj["tool_calls"]:
                    print("Tool call:", tc.get("name"), tc.get("args"))
            if "content" in obj:
                print("Content:", str(obj.get("content"))[:300])
