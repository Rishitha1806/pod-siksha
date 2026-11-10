import sqlite3
conn = sqlite3.connect('pod_siksha.db')
cur = conn.cursor()
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()]
print("All SQLite tables:")
for t in tables:
    count = cur.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
    print(f"  {t}: {count} rows")
