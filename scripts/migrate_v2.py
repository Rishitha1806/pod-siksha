import sqlite3
import os
import secrets
import hashlib
from datetime import datetime, timedelta

DB_PATH = r"C:\Users\jvris\Downloads\pod-siksha\pod_siksha.db"

def hash_password(password: str, salt: str = None) -> tuple:
    if not salt:
        salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
    return pw_hash, salt

def run_migration():
    print(f"Applying additive v2 migration to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            full_name TEXT NOT NULL,
            preferred_language TEXT DEFAULT 'te',
            is_verified INTEGER DEFAULT 1,
            verification_token TEXT,
            reset_token TEXT,
            reset_token_expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. User sessions table (for active tokens)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            token TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # 3. Add user_id column to existing tables if missing
    for table in ["sessions", "doubts", "quiz_sessions", "concept_events"]:
        cur.execute(f"PRAGMA table_info({table})")
        columns = [c[1] for c in cur.fetchall()]
        if "user_id" not in columns:
            print(f"Adding user_id column to {table}...")
            cur.execute(f"ALTER TABLE {table} ADD COLUMN user_id TEXT")

    # 4. Concept DNA table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS concept_dna (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            concept_tag TEXT NOT NULL,
            definition TEXT,
            prerequisites_json TEXT,
            related_json TEXT,
            mastery_score REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 5. Teach-Back Sessions
    cur.execute("""
        CREATE TABLE IF NOT EXISTS teachback_sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            session_id TEXT NOT NULL,
            concept_tag TEXT NOT NULL,
            ai_prompt TEXT NOT NULL,
            user_transcript TEXT NOT NULL,
            understood_points_json TEXT,
            misconceptions_json TEXT,
            missing_points_json TEXT,
            next_step TEXT,
            mastery_delta REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 6. Misconceptions table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS misconceptions (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            session_id TEXT NOT NULL,
            concept_tag TEXT NOT NULL,
            misconception_text TEXT NOT NULL,
            grounded_truth TEXT NOT NULL,
            confidence REAL DEFAULT 0.85,
            evidence_source TEXT DEFAULT 'teachback',
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP
        )
    """)

    # 7. Memory Loop Spaced Revision table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS memory_loop (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            concept_tag TEXT NOT NULL,
            session_id TEXT,
            interval_hours INTEGER DEFAULT 24,
            due_at TIMESTAMP NOT NULL,
            status TEXT DEFAULT 'queued',
            last_recalled_at TIMESTAMP,
            recall_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Seed demo user if not existing
    cur.execute("SELECT id FROM users WHERE email = 'learner@demo.in'")
    row = cur.fetchone()
    if not row:
        demo_id = "user_demo_001"
        pw_hash, salt = hash_password("podsiksha2026")
        cur.execute("""
            INSERT INTO users (id, email, password_hash, salt, full_name, preferred_language, is_verified)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (demo_id, "learner@demo.in", pw_hash, salt, "Rishitha J.V.", "te"))
        print("Created default demo user: learner@demo.in / podsiksha2026")

        # Associate existing sessions with demo user
        cur.execute("UPDATE sessions SET user_id = ? WHERE user_id IS NULL", (demo_id,))
        cur.execute("UPDATE doubts SET user_id = ? WHERE user_id IS NULL", (demo_id,))
        cur.execute("UPDATE quiz_sessions SET user_id = ? WHERE user_id IS NULL", (demo_id,))
        cur.execute("UPDATE concept_events SET user_id = ? WHERE user_id IS NULL", (demo_id,))
        print("Associated existing database history with demo user.")

    # Seed sample misconception from real data if none
    cur.execute("SELECT COUNT(*) FROM misconceptions")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO misconceptions (id, user_id, session_id, concept_tag, misconception_text, grounded_truth, confidence, evidence_source, status)
            VALUES (
                'misc_001',
                'user_demo_001',
                (SELECT id FROM sessions ORDER BY created_at DESC LIMIT 1),
                'Water Photolysis',
                'Water is split directly to synthesize glucose sugar.',
                'Water photolysis replenishes chlorophyll electrons in Photosystem II; oxygen is released as a byproduct while electrons power ATP synthase.',
                0.88,
                'teachback',
                'active'
            )
        """)
        print("Seeded diagnosed misconception for Water Photolysis.")

    # Seed memory loop touchpoints if none
    cur.execute("SELECT COUNT(*) FROM memory_loop")
    if cur.fetchone()[0] == 0:
        now = datetime.now()
        cur.execute("""
            INSERT INTO memory_loop (id, user_id, concept_tag, session_id, interval_hours, due_at, status)
            VALUES 
            ('mem_001', 'user_demo_001', 'Water Photolysis Mechanism', (SELECT id FROM sessions ORDER BY created_at DESC LIMIT 1), 24, ?, 'queued'),
            ('mem_002', 'user_demo_001', 'RuBisCO Enzyme Function', (SELECT id FROM sessions ORDER BY created_at DESC LIMIT 1), 72, ?, 'queued')
        """, (now.strftime("%Y-%m-%d %H:%M:%S"), (now + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")))
        print("Seeded memory loop touchpoints.")

    conn.commit()
    conn.close()
    print("Migration v2 completed successfully!")

if __name__ == "__main__":
    run_migration()
