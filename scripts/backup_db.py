"""Pod-Siksha — Database Backup & Integrity Verification Utility
Creates timestamped hot backups of SQLite pod_siksha.db and verifies integrity.
"""
import os
import shutil
import sqlite3
import sys
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "pod_siksha.db")
BACKUP_DIR = os.path.join(ROOT_DIR, "backups")

def run_backup():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file does not exist at {DB_PATH}")
        sys.exit(1)

    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"pod_siksha_backup_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    print(f"Starting SQLite backup from {DB_PATH} to {backup_path}...")
    
    # Use SQLite Online Backup API for hot consistency
    src_conn = sqlite3.connect(DB_PATH)
    dst_conn = sqlite3.connect(backup_path)
    try:
        src_conn.backup(dst_conn)
        print("Hot backup completed successfully.")
    finally:
        dst_conn.close()
        src_conn.close()

    # Verify backup integrity
    verify_conn = sqlite3.connect(backup_path)
    try:
        res = verify_conn.execute("PRAGMA integrity_check").fetchone()[0]
        if res.lower() == "ok":
            print(f"Integrity check PASSED: {res}")
        else:
            print(f"Warning: Integrity check returned: {res}")
            sys.exit(2)
        
        # Display record counts
        sess_cnt = verify_conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        doubt_cnt = verify_conn.execute("SELECT COUNT(*) FROM doubts").fetchone()[0]
        quiz_cnt = verify_conn.execute("SELECT COUNT(*) FROM quiz_sessions WHERE completed = 1").fetchone()[0]
        ans_cnt = verify_conn.execute("SELECT COUNT(*) FROM quiz_answers").fetchone()[0]
        print(f"Backup verified. Statistics: {sess_cnt} sessions, {doubt_cnt} doubts, {quiz_cnt} completed quizzes, {ans_cnt} answers.")
    finally:
        verify_conn.close()

    print(f"Backup successfully generated: {backup_path}")
    return backup_path

if __name__ == "__main__":
    run_backup()
