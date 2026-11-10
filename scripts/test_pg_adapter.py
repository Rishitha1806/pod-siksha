import os
import re
import dotenv
import psycopg2
import psycopg2.extras

dotenv.load_dotenv(".env")
pg_url = os.getenv("DATABASE_URL")

def to_pg_sql(sql: str) -> str:
    s = sql.strip()
    # 1. Ignore PRAGMAs
    if s.upper().startswith("PRAGMA"):
        return ""
    
    # 2. Convert INSERT OR REPLACE INTO user_sessions
    if "INSERT OR REPLACE INTO user_sessions" in s:
        s = s.replace("INSERT OR REPLACE INTO user_sessions", "INSERT INTO user_sessions")
        if "ON CONFLICT" not in s:
            s += " ON CONFLICT (token) DO UPDATE SET user_id = EXCLUDED.user_id, expires_at = EXCLUDED.expires_at"

    # 3. Convert datetime('now', '+30 days')
    s = re.sub(r"datetime\('now',\s*'\+30 days'\)", "CURRENT_TIMESTAMP + INTERVAL '30 days'", s, flags=re.IGNORECASE)
    # 4. Convert datetime('now')
    s = re.sub(r"datetime\('now'\)", "CURRENT_TIMESTAMP", s, flags=re.IGNORECASE)

    # 5. Convert ? placeholders to %s (outside quotes)
    pattern = r"('(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"|\?)"
    def repl(m):
        tok = m.group(1)
        return "%s" if tok == "?" else tok
    s = re.sub(pattern, repl, s)
    return s

conn = psycopg2.connect(pg_url, cursor_factory=psycopg2.extras.DictCursor)
cur = conn.cursor()

test_queries = [
    ("PRAGMA journal_mode=WAL;", ()),
    ("SELECT * FROM users WHERE email = ? AND role = ?", ("learner@demo.in", "student")),
    ("SELECT u.id, u.email, u.full_name, u.preferred_language, u.is_verified, u.role FROM user_sessions s JOIN users u ON s.user_id = u.id WHERE s.token = ? AND s.expires_at > datetime('now')", ("session_demo_learner_001",)),
    ("SELECT * FROM sessions WHERE user_id = ? ORDER BY created_at DESC LIMIT 5", ("user_demo_001",)),
    ("SELECT * FROM doubts WHERE session_id = ? ORDER BY turn_index ASC", ("sess_quadratic_001",)),
    ("SELECT * FROM quiz_sessions WHERE session_id = ? ORDER BY created_at DESC LIMIT 1", ("sess_quadratic_001",))
]

for sql, params in test_queries:
    pg_sql = to_pg_sql(sql)
    if not pg_sql:
        print(f"Skipped PRAGMA: {sql}")
        continue
    cur.execute(pg_sql, params)
    rows = cur.fetchall()
    print(f"Query: {sql[:50]}... -> Rows: {len(rows)}")
    if rows:
        first = rows[0]
        print(f"  First row by key: {list(first.keys())[:3]} -> {first[0]}")

conn.close()
print("All prototype queries succeeded against Neon!")
