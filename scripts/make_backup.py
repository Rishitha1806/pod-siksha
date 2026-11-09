import shutil
import sqlite3
import datetime
import os

src = "pod_siksha.db"
os.makedirs("backups", exist_ok=True)
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
dst = f"backups/pod_siksha_backup_{ts}.db"

shutil.copy2(src, dst)

# Verify backup integrity
conn = sqlite3.connect(dst)
cur = conn.cursor()
check = cur.execute("PRAGMA integrity_check;").fetchone()
row_count = cur.execute("SELECT COUNT(*) FROM sessions;").fetchone()[0]
conn.close()

size = os.path.getsize(dst)
print(f"Verified SQLite backup created at {dst}")
print(f"Size: {size} bytes, Sessions: {row_count}, Integrity: {check[0]}")
