import json
import base64

with open('C:/Users/jvris/Downloads/pod-siksha/scripts/upload_cache.json', 'r') as f:
    d = json.load(f)
for k, v in d.items():
    try:
        raw = base64.b64decode(v['b64'])
        print(f"{k}: valid b64, len={len(v['b64'])}, decoded_size={len(raw)}, size={v['size']}, match={len(raw) == v['size']}")
    except Exception as e:
        print(f"{k}: ERROR {e}")
