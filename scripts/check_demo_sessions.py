import sqlite3

conn = sqlite3.connect("pod_siksha.db")
conn.execute("""
    INSERT OR REPLACE INTO user_sessions (token, user_id, expires_at)
    VALUES ('session_demo_learner_001', 'user_demo_001', datetime('now', '+30 days'))
""")
conn.execute("""
    INSERT OR REPLACE INTO user_sessions (token, user_id, expires_at)
    VALUES ('session_demo_teacher_001', 'user_teacher_001', datetime('now', '+30 days'))
""")
conn.commit()

print("User sessions:")
for row in conn.execute("SELECT token, user_id, expires_at FROM user_sessions WHERE token LIKE 'session_demo_%'").fetchall():
    print(row)
conn.close()
