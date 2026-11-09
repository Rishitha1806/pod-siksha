with open("server.py", "r", encoding="utf-8") as f:
    code = f.read()

target = """        conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_loop_due ON memory_loop(due_at)")
        conn.commit()"""

replacement = """        conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_loop_due ON memory_loop(due_at)")
        # Guarantee demo user sessions exist with 30-day validity
        conn.execute(\"\"\"
            INSERT OR REPLACE INTO user_sessions (token, user_id, expires_at)
            VALUES ('session_demo_learner_001', 'user_demo_001', datetime('now', '+30 days'))
        \"\"\")
        conn.execute(\"\"\"
            INSERT OR REPLACE INTO user_sessions (token, user_id, expires_at)
            VALUES ('session_demo_teacher_001', 'user_teacher_001', datetime('now', '+30 days'))
        \"\"\")
        conn.commit()"""

if target in code:
    code = code.replace(target, replacement, 1)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("Successfully patched init_db() to seed demo sessions.")
else:
    print("Target not found. Normalizing line endings...")
    code_norm = code.replace("\r\n", "\n")
    target_norm = target.replace("\r\n", "\n")
    if target_norm in code_norm:
        code_norm = code_norm.replace(target_norm, replacement, 1)
        with open("server.py", "w", encoding="utf-8") as f:
            f.write(code_norm)
        print("Successfully patched init_db() after normalization.")
    else:
        print("Failed to find target in init_db.")
