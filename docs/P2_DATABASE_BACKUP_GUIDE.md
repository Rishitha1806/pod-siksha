# Pod-Siksha: Database Backup & Recovery Guide

## 1. Overview
Pod-Siksha utilizes an embedded, persistent SQLite database (`pod_siksha.db`) to record classroom sessions, 14-turn podcast scripts, doubt interruptions, hint ladder levels, oral quiz questions, student transcripts, and concept events.

To guarantee zero data loss across application restarts, system maintenance, and host redeployments, Pod-Siksha includes an automated, hot-consistent database backup utility (`scripts/backup_db.py`).

---

## 2. Automated Backup Execution
The hot backup utility uses SQLite's native Online Backup API (`sqlite3.Connection.backup()`), which safely reads the database even while students and teachers are concurrently submitting doubts or viewing analytics.

### Manual Backup Command
```bash
python scripts/backup_db.py
```

### Script Workflow:
1. Locates `pod_siksha.db` in the application root directory.
2. Ensures the `backups/` directory exists.
3. Generates a timestamped replica: `backups/pod_siksha_backup_YYYYMMDD_HHMMSS.db`.
4. Executes SQLite Online Backup (`src_conn.backup(dst_conn)`).
5. Performs immediate integrity verification on the generated backup:
   ```sql
   PRAGMA integrity_check;
   ```
6. Validates key table record counts (`sessions`, `doubts`, `quiz_sessions`, `quiz_answers`).
7. Exits with code `0` on verified success.

---

## 3. Scheduled Automated Backups

### Linux / Production Server (Cron)
To run an automated backup every 6 hours and retain the last 30 days of snapshots:
```bash
# Add to crontab via crontab -e
0 */6 * * * cd /app && python scripts/backup_db.py >> /var/log/pod_siksha_backup.log 2>&1
0 2 * * * find /app/backups -name "pod_siksha_backup_*.db" -mtime +30 -delete
```

### Windows Host (Task Scheduler / PowerShell)
```powershell
$Action = New-ScheduledTaskAction -Execute "python.exe" -Argument "C:\Users\jvris\Downloads\pod-siksha\scripts\backup_db.py" -WorkingDirectory "C:\Users\jvris\Downloads\pod-siksha"
$Trigger = New-ScheduledTaskTrigger -Daily -At 2:00AM
Register-ScheduledTask -TaskName "PodSikshaDailyBackup" -Action $Action -Trigger $Trigger
```

---

## 4. Disaster Recovery & Restoration Procedure

In the event of database corruption or hardware failure, follow this restoration procedure:

### Step 1: Stop the Pod-Siksha Application
```bash
# Terminate Uvicorn process
killall uvicorn # or Taskkill on Windows
```

### Step 2: Select the Most Recent Healthy Backup
```bash
ls -lt backups/
# Example: backups/pod_siksha_backup_20261109_160311.db
```

### Step 3: Verify Backup Integrity Before Restoring
```bash
python -c "import sqlite3; conn = sqlite3.connect('backups/pod_siksha_backup_20261109_160311.db'); print(conn.execute('PRAGMA integrity_check').fetchall())"
# Expected output: [('ok',)]
```

### Step 4: Replace Corrupted Database File
```bash
cp backups/pod_siksha_backup_20261109_160311.db pod_siksha.db
```

### Step 5: Restart the Server
```bash
python server.py
```

### Step 6: Verify Endpoint Health
```bash
curl http://127.0.0.1:8008/api/health
# Confirm "database": "connected"
```
