with open("server.py", "r", encoding="utf-8") as f:
    code = f.read()

target = "def get_db():\n    conn = sqlite3.connect(DB_PATH)\n    conn.row_factory = sqlite3.Row\n    return conn"
replacement = "def get_db():\n    conn = sqlite3.connect(DB_PATH, timeout=30.0)\n    conn.row_factory = sqlite3.Row\n    try:\n        conn.execute('PRAGMA journal_mode=WAL;')\n        conn.execute('PRAGMA busy_timeout=30000;')\n    except Exception:\n        pass\n    return conn"

if target in code:
    code = code.replace(target, replacement, 1)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("Successfully patched get_db() with WAL and busy_timeout=30000.")
else:
    print("Target not found. Looking with normalized line endings...")
    # Try normalizing \r\n
    code_norm = code.replace("\r\n", "\n")
    if target in code_norm:
        code_norm = code_norm.replace(target, replacement, 1)
        with open("server.py", "w", encoding="utf-8") as f:
            f.write(code_norm)
        print("Successfully patched get_db() after normalization.")
    else:
        print("Could not find target get_db block.")
