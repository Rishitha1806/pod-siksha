"""
Database Migration & Synchronizer: SQLite to Neon PostgreSQL for Pod-Siksha 2.0.
Transfers all existing sessions, doubts, quiz records, users, and telemetry
from local pod_siksha.db into a Neon PostgreSQL database without data loss.
"""

import os
import sqlite3
import json
import psycopg2
import psycopg2.extras

def get_pg_connection(pg_url: str):
    import psycopg2
    import psycopg2.extras
    conn = psycopg2.connect(pg_url, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn

def init_pg_schema(pg_conn):
    with pg_conn.cursor() as cur:
        # Users
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                role TEXT DEFAULT 'student'
            );
        """)

        # User Sessions
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                token TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            );
        """)

        # Sessions
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                title TEXT,
                chapter_text TEXT,
                language TEXT,
                script_json TEXT,
                quiz_json TEXT,
                status TEXT DEFAULT 'active',
                user_id TEXT REFERENCES users(id) ON DELETE SET NULL
            );
        """)

        # Doubts
        cur.execute("""
            CREATE TABLE IF NOT EXISTS doubts (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                turn_index INTEGER,
                playback_ms INTEGER,
                transcribed_text TEXT,
                detected_language TEXT,
                concept_tag TEXT,
                hint_level INTEGER DEFAULT 1,
                answer_text TEXT,
                spoken_answer TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT REFERENCES users(id) ON DELETE SET NULL
            );
        """)

        # Concept DNA
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
            );
        """)

        # Teach-Back
        cur.execute("""
            CREATE TABLE IF NOT EXISTS teachback_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id) ON DELETE SET NULL,
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
            );
        """)

        # Misconceptions
        cur.execute("""
            CREATE TABLE IF NOT EXISTS misconceptions (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id) ON DELETE SET NULL,
                session_id TEXT,
                concept_tag TEXT NOT NULL,
                misconception_text TEXT NOT NULL,
                grounded_truth TEXT,
                confidence REAL DEFAULT 0.85,
                evidence_source TEXT DEFAULT 'teachback',
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP
            );
        """)

        # Memory Loop
        cur.execute("""
            CREATE TABLE IF NOT EXISTS memory_loop (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id) ON DELETE SET NULL,
                concept_tag TEXT NOT NULL,
                session_id TEXT,
                interval_hours INTEGER DEFAULT 24,
                due_at TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'queued',
                last_recalled_at TIMESTAMP,
                recall_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Quiz Sessions
        cur.execute("""
            CREATE TABLE IF NOT EXISTS quiz_sessions (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                language TEXT,
                total_questions INTEGER DEFAULT 0,
                total_score REAL DEFAULT 0.0,
                percentage REAL DEFAULT 0.0,
                completed INTEGER DEFAULT 0,
                learning_summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                user_id TEXT REFERENCES users(id) ON DELETE SET NULL
            );
        """)

        # Quiz Questions
        cur.execute("""
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id TEXT PRIMARY KEY,
                quiz_session_id TEXT REFERENCES quiz_sessions(id) ON DELETE CASCADE,
                question_number INTEGER,
                question_type TEXT,
                question_text TEXT,
                spoken_text TEXT,
                expected_answer TEXT,
                concept_tag TEXT,
                difficulty TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Quiz Answers
        cur.execute("""
            CREATE TABLE IF NOT EXISTS quiz_answers (
                id TEXT PRIMARY KEY,
                quiz_question_id TEXT REFERENCES quiz_questions(id) ON DELETE CASCADE,
                quiz_session_id TEXT,
                transcript TEXT,
                evaluation_status TEXT,
                score REAL,
                feedback_display TEXT,
                feedback_spoken TEXT,
                correct_points TEXT,
                missing_points TEXT,
                concept_tag TEXT,
                ideal_answer TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        # Concept Events
        cur.execute("""
            CREATE TABLE IF NOT EXISTS concept_events (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                concept_tag TEXT,
                normalized_tag TEXT,
                event_type TEXT,
                hint_level INTEGER DEFAULT 1,
                quiz_status TEXT,
                score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT REFERENCES users(id) ON DELETE SET NULL
            );
        """)

        # Teacher Recommendations
        cur.execute("""
            CREATE TABLE IF NOT EXISTS teacher_recommendations (
                id TEXT PRIMARY KEY,
                chapter_filter TEXT,
                recommendations_json TEXT,
                evidence_summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        pg_conn.commit()

def migrate_data(sqlite_path: str, pg_url: str):
    print(f"Connecting to SQLite: {sqlite_path}...")
    s_conn = sqlite3.connect(sqlite_path)
    s_conn.row_factory = sqlite3.Row
    s_cur = s_conn.cursor()

    print(f"Connecting to Neon PostgreSQL...")
    p_conn = get_pg_connection(pg_url)
    init_pg_schema(p_conn)

    tables = [
        "users", "user_sessions", "sessions", "doubts", "concept_dna",
        "teachback_sessions", "misconceptions", "memory_loop",
        "quiz_sessions", "quiz_questions", "quiz_answers",
        "concept_events", "teacher_recommendations"
    ]

    total_rows = 0
    stats = {}
    with p_conn.cursor() as p_cur:
        for tbl in tables:
            query = f"SELECT * FROM {tbl}"
            if tbl == "user_sessions":
                query = "SELECT * FROM user_sessions WHERE user_id IN (SELECT id FROM users)"
            rows = s_cur.execute(query).fetchall()
            if not rows:
                print(f"Table '{tbl}': 0 rows to migrate.")
                stats[tbl] = {"sqlite": 0, "neon": 0}
                continue

            cols = [desc[0] for desc in s_cur.description]
            col_names = ", ".join(cols)
            conflict_col = "token" if tbl == "user_sessions" else "id"
            insert_query = f"""
                INSERT INTO {tbl} ({col_names})
                VALUES %s
                ON CONFLICT ({conflict_col}) DO NOTHING;
            """

            # Batch insert using psycopg2.extras.execute_values
            data = [tuple(r) for r in rows]
            psycopg2.extras.execute_values(p_cur, insert_query, data, page_size=100)
            p_conn.commit()

            # Check Neon count
            p_cur.execute(f"SELECT COUNT(*) FROM {tbl}")
            neon_count = p_cur.fetchone()["count"]
            print(f"Table '{tbl}': SQLite={len(rows)}, Neon Total={neon_count}", flush=True)
            stats[tbl] = {"sqlite": len(rows), "neon": neon_count}
            total_rows += len(rows)

    s_conn.close()
    p_conn.close()
    print(f"\nMigration complete! Total {total_rows} rows processed to Neon PostgreSQL.")
    return stats

if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    load_dotenv(".env")
    
    pg_url = os.getenv("DATABASE_URL")
    if len(sys.argv) > 1:
        pg_url = sys.argv[1]

    if not pg_url:
        print("Usage: python scripts/migrate_sqlite_to_neon.py <NEON_DATABASE_URL>")
        print("Or set DATABASE_URL in .env.")
    else:
        sqlite_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pod_siksha.db")
        migrate_data(sqlite_file, pg_url)
