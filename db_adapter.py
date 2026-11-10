"""
Database Adapter for Pod-Siksha 2.0.
Seamlessly routes queries to Neon PostgreSQL in production (when DATABASE_URL is set),
or SQLite for local development.

Features:
- Translates SQLite parameter placeholders (?) to PostgreSQL placeholders (%s).
- Converts SQLite datetime('now') expressions to standard PostgreSQL CURRENT_TIMESTAMP.
- Safely ignores SQLite-specific PRAGMAs.
- DictCursor provides identical field and index lookup to sqlite3.Row.
- Strictly raises an error if DATABASE_URL is missing in production environments.
"""

import os
import re
import logging
import sqlite3
from typing import Any, Optional, Tuple
from dotenv import load_dotenv

# Ensure .env is always loaded
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

log = logging.getLogger("pod_siksha.db")

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
IS_PRODUCTION = bool(os.getenv("VERCEL") or os.getenv("ENV") == "production" or os.getenv("NEON_BRANCH"))
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pod_siksha.db")

try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


def to_pg_sql(sql: str) -> str:
    s = sql.strip()
    if s.upper().startswith("PRAGMA"):
        return ""

    # Convert INSERT OR REPLACE INTO <table>
    m_replace = re.match(r"INSERT\s+OR\s+REPLACE\s+INTO\s+([a-zA-Z0-9_]+)\s*\(([^)]+)\)\s*VALUES\s*(.*)", s, re.IGNORECASE | re.DOTALL)
    if m_replace:
        tbl = m_replace.group(1)
        cols = [c.strip() for c in m_replace.group(2).split(",")]
        vals = m_replace.group(3)
        pk = "token" if tbl.lower() == "user_sessions" else "id"
        updates = ", ".join([f"{c} = EXCLUDED.{c}" for c in cols if c.lower() != pk])
        if updates:
            s = f"INSERT INTO {tbl} ({m_replace.group(2)}) VALUES {vals} ON CONFLICT ({pk}) DO UPDATE SET {updates}"
        else:
            s = f"INSERT INTO {tbl} ({m_replace.group(2)}) VALUES {vals} ON CONFLICT ({pk}) DO NOTHING"

    # Convert datetime('now', '+X days/hours/minutes/seconds')
    s = re.sub(
        r"datetime\('now',\s*'\+?(\d+)\s*(days?|hours?|minutes?|seconds?)'\)",
        r"CURRENT_TIMESTAMP + INTERVAL '\1 \2'",
        s,
        flags=re.IGNORECASE
    )
    # Convert datetime('now')
    s = re.sub(r"datetime\('now'\)", "CURRENT_TIMESTAMP", s, flags=re.IGNORECASE)

    # Convert ? placeholders to %s (outside quoted strings)
    pattern = r"('(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"|\?)"
    def repl(m):
        tok = m.group(1)
        return "%s" if tok == "?" else tok
    s = re.sub(pattern, repl, s)
    return s


class DummyCursor:
    """Mock cursor for ignored PRAGMA statements."""
    def fetchone(self):
        return None
    def fetchall(self):
        return []
    def __iter__(self):
        return iter([])


class PostgresCursorWrapper:
    def __init__(self, raw_cursor):
        self._raw = raw_cursor

    def execute(self, sql: str, params: Optional[Tuple[Any, ...]] = None):
        pg_sql = to_pg_sql(sql)
        if not pg_sql:
            return DummyCursor()
        if params is None:
            self._raw.execute(pg_sql)
        else:
            self._raw.execute(pg_sql, params)
        return self

    def fetchone(self):
        return self._raw.fetchone()

    def fetchall(self):
        return self._raw.fetchall()

    def fetchmany(self, size=None):
        return self._raw.fetchmany(size)

    @property
    def description(self):
        return self._raw.description

    @property
    def rowcount(self):
        return self._raw.rowcount

    def close(self):
        return self._raw.close()

    def __iter__(self):
        return iter(self._raw)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._raw.close()


class PostgresConnectionWrapper:
    def __init__(self, raw_conn):
        self._conn = raw_conn
        self._row_factory = None

    @property
    def row_factory(self):
        return self._row_factory

    @row_factory.setter
    def row_factory(self, val):
        self._row_factory = val

    def cursor(self):
        return PostgresCursorWrapper(self._conn.cursor())

    def execute(self, sql: str, params: Optional[Tuple[Any, ...]] = None):
        pg_sql = to_pg_sql(sql)
        if not pg_sql:
            return DummyCursor()
        cur = self._conn.cursor()
        if params is None:
            cur.execute(pg_sql)
        else:
            cur.execute(pg_sql, params)
        return PostgresCursorWrapper(cur)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.close()


def get_db():
    """
    Returns a database connection.
    If DATABASE_URL is set, connects to Neon PostgreSQL.
    Otherwise, if IS_PRODUCTION, raises an error rather than silently falling back.
    Otherwise (local development), uses SQLite.
    """
    db_url = os.getenv("DATABASE_URL", "").strip()

    if db_url:
        if not PSYCOPG2_AVAILABLE:
            raise RuntimeError("psycopg2 is required to connect to Neon PostgreSQL, but it is not installed.")
        try:
            # Neon requires SSL
            conn = psycopg2.connect(db_url, cursor_factory=psycopg2.extras.DictCursor)
            return PostgresConnectionWrapper(conn)
        except Exception as e:
            log.error("Failed to connect to Neon PostgreSQL: %s", e)
            raise RuntimeError(f"Database connection to Neon PostgreSQL failed: {e}") from e

    if IS_PRODUCTION:
        raise RuntimeError("DATABASE_URL must be configured in production. Fallback to SQLite is strictly forbidden.")

    # Local SQLite fallback
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute('PRAGMA journal_mode=WAL;')
        conn.execute('PRAGMA busy_timeout=30000;')
    except Exception:
        pass
    return conn
