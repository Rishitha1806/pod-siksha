import sqlite3

conn = sqlite3.connect("pod_siksha.db")
print("users columns:", [c[1] for c in conn.execute("PRAGMA table_info(users)").fetchall()])
print("user_sessions columns:", [c[1] for c in conn.execute("PRAGMA table_info(user_sessions)").fetchall()])
