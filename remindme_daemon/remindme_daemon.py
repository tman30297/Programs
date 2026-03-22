#!/usr/bin/env python3
"""Background daemon for remindme - checks for due reminders."""

import os
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

DB_PATH = Path.home() / ".remindme.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS reminders
                 (id INTEGER PRIMARY KEY, message TEXT, remind_at REAL, created_at REAL, notified INTEGER)''')
    conn.commit()
    return conn

def notify(message):
    """Show notification using notify-send."""
    try:
        subprocess.run([
            'notify-send', '-u', 'normal', '-t', '0',
            '⏰ Reminder', message
        ], capture_output=True, timeout=5)
    except Exception as e:
        # Fallback to stdout
        print(f"\n🔔 [{time.strftime('%H:%M')}] REMINDER: {message}", flush=True)

def main():
    # Ensure single instance
    lock_file = Path.home() / ".remindme_daemon.lock"
    if lock_file.exists():
        # Check if process is actually running
        try:
            with open(lock_file) as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)  # Check if process exists
            sys.exit(0)  # Already running
        except:
            pass  # Stale lock
    
    # Write lock file
    with open(lock_file, 'w') as f:
        f.write(str(os.getpid()))
    
    conn = init_db()
    
    while True:
        try:
            now = time.time()
            c = conn.cursor()
            c.execute("SELECT id, message FROM reminders WHERE notified=0 AND remind_at <= ?", (now,))
            due = c.fetchall()
            
            for rid, message in due:
                notify(message)
                c.execute("UPDATE reminders SET notified=1 WHERE id=?", (rid,))
            
            conn.commit()
        except Exception as e:
            pass
        
        time.sleep(10)

if __name__ == '__main__':
    main()
