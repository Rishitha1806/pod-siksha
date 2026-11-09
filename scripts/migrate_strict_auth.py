import sqlite3
import os
import uuid
import hashlib
import secrets

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pod_siksha.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

# 1. Add role column to users if not present
cols = [c["name"] for c in conn.execute("PRAGMA table_info(users)").fetchall()]
if "role" not in cols:
    conn.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'student'")
    print("Added role column to users.")

# 2. Add verification_token to users if missing
if "verification_token" not in cols:
    conn.execute("ALTER TABLE users ADD COLUMN verification_token TEXT")
    print("Added verification_token column to users.")

def hash_pw(pw, salt=None):
    salt = salt or secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 100_000).hex()
    return pw_hash, salt

# 3. Ensure teacher user exists
teacher = conn.execute("SELECT id FROM users WHERE email = 'teacher@demo.in'").fetchone()
if not teacher:
    h, s = hash_pw("teacheraura2026")
    conn.execute("""
        INSERT INTO users (id, email, password_hash, salt, full_name, preferred_language, is_verified, role)
        VALUES ('user_teacher_001', 'teacher@demo.in', ?, ?, 'Prof. Yashwanth (Teacher)', 'te', 1, 'teacher')
    """, (h, s))
    print("Seeded teacher@demo.in.")

# Ensure demo student has role = student
conn.execute("UPDATE users SET role = 'student' WHERE email = 'learner@demo.in' AND role IS NULL")

# 4. Ensure teacher session exists for testing
t_sess = conn.execute("SELECT token FROM user_sessions WHERE user_id = 'user_teacher_001'").fetchone()
if not t_sess:
    conn.execute("""
        INSERT INTO user_sessions (token, user_id, expires_at)
        VALUES ('session_demo_teacher_001', 'user_teacher_001', datetime('now', '+30 days'))
    """)
    print("Created teacher session session_demo_teacher_001.")

# Ensure student session exists
s_sess = conn.execute("SELECT token FROM user_sessions WHERE user_id = 'user_demo_001'").fetchone()
if not s_sess:
    conn.execute("""
        INSERT INTO user_sessions (token, user_id, expires_at)
        VALUES ('session_demo_learner_001', 'user_demo_001', datetime('now', '+30 days'))
    """)
    print("Created learner session session_demo_learner_001.")

conn.commit()
conn.close()
print("Migration completed successfully.")
