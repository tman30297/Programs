#!/usr/bin/env python3
"""
Smart Reminder CLI - Natural language reminder tool
Usage: remindme <time> <message>
       remindme list
       remindme clear
       
Examples:
  remindme in 30 minutes "Call mom"
  remindme in 2 hours "Meeting with team"
  remindme at 5pm "Check email"
  remindme tomorrow 9am "Standup"
  remindme list
  remindme clear
"""

import argparse
import os
import re
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path.home() / ".remindme.db"

def init_db():
    """Initialize the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reminders
                 (id INTEGER PRIMARY KEY, message TEXT, remind_at REAL, created_at REAL, notified INTEGER)''')
    conn.commit()
    return conn

def parse_time(time_str):
    """Parse natural language time into datetime."""
    now = datetime.now()
    time_str = time_str.lower().strip()
    
    # Handle "at X" - specific time today or tomorrow
    at_match = re.match(r'at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', time_str)
    if at_match:
        hour = int(at_match.group(1))
        minute = int(at_match.group(2) or 0)
        ampm = at_match.group(3)
        
        if ampm:
            if ampm == 'pm' and hour != 12:
                hour += 12
            elif ampm == 'am' and hour == 12:
                hour = 0
        
        # If time has passed, assume tomorrow
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target < now:
            target += timedelta(days=1)
        return target
    
    # Handle "in X minutes/hours/days/weeks"
    in_match = re.match(r'in\s+(\d+)\s*(minutes?|mins?|hours?|hrs?|days?|weeks?|months?)', time_str)
    if in_match:
        amount = int(in_match.group(1))
        unit = in_match.group(2)
        
        if unit.startswith('min'):
            delta = timedelta(minutes=amount)
        elif unit.startswith('hour') or unit.startswith('hr'):
            delta = timedelta(hours=amount)
        elif unit.startswith('day'):
            delta = timedelta(days=amount)
        elif unit.startswith('week'):
            delta = timedelta(weeks=amount)
        elif unit.startswith('month'):
            delta = timedelta(days=amount * 30)
        
        return now + delta
    
    # Handle relative days: "tomorrow", "day after tomorrow"
    if time_str == 'tomorrow':
        return (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    if time_str == 'day after tomorrow':
        return (now + timedelta(days=2)).replace(hour=9, minute=0, second=0, microsecond=0)
    
    # Handle "tomorrow at X"
    tomorrow_match = re.match(r'tomorrow\s+at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', time_str)
    if tomorrow_match:
        hour = int(tomorrow_match.group(1))
        minute = int(tomorrow_match.group(2) or 0)
        ampm = tomorrow_match.group(3)
        
        if ampm:
            if ampm == 'pm' and hour != 12:
                hour += 12
            elif ampm == 'am' and hour == 12:
                hour = 0
        
        target = (now + timedelta(days=1)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        return target
    
    raise ValueError(f"Couldn't parse time: {time_str}")

def add_reminder(message, remind_at):
    """Add a reminder to the database."""
    conn = init_db()
    c = conn.cursor()
    # Convert datetime to timestamp if needed
    ts = remind_at.timestamp() if isinstance(remind_at, datetime) else remind_at
    c.execute("INSERT INTO reminders (message, remind_at, created_at, notified) VALUES (?, ?, ?, 0)",
              (message, ts, time.time()))
    conn.commit()
    conn.close()
    
    # Format nice display time
    dt = datetime.fromtimestamp(ts)
    if dt.date() == datetime.now().date():
        time_str = dt.strftime("%I:%M %p today")
    elif dt.date() == (datetime.now() + timedelta(days=1)).date():
        time_str = dt.strftime("%I:%M %p tomorrow")
    else:
        time_str = dt.strftime("%b %d at %I:%M %p")
    
    print(f"✅ Reminder set: \"{message}\" at {time_str}")

def list_reminders():
    """List all pending reminders."""
    conn = init_db()
    c = conn.cursor()
    c.execute("SELECT id, message, remind_at FROM reminders WHERE notified=0 ORDER BY remind_at")
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        print("📭 No pending reminders")
        return
    
    print("📋 Pending Reminders:")
    print("-" * 50)
    for idx, (rid, message, remind_at) in enumerate(rows, 1):
        dt = datetime.fromtimestamp(remind_at)
        now = datetime.now()
        
        if dt < now:
            status = "⏰ OVERDUE"
        else:
            status = ""
        
        if dt.date() == now.date():
            time_str = dt.strftime("%I:%M %p today")
        elif dt.date() == (now + timedelta(days=1)).date():
            time_str = dt.strftime("%I:%M %p tomorrow")
        else:
            time_str = dt.strftime("%b %d at %I:%M %p")
        
        print(f"  {rid}. {time_str} - {message} {status}")

def clear_reminders(reminder_id=None):
    """Clear all or specific reminder."""
    conn = init_db()
    c = conn.cursor()
    
    if reminder_id:
        c.execute("DELETE FROM reminders WHERE id=?", (reminder_id,))
        print(f"🗑️  Cleared reminder #{reminder_id}")
    else:
        c.execute("DELETE FROM reminders")
        print("🗑️  Cleared all reminders")
    
    conn.commit()
    conn.close()

def check_daemon():
    """Check if reminder daemon is running."""
    try:
        result = subprocess.run(['pgrep', '-f', 'remindme_daemon'], 
                              capture_output=True, text=True)
        return bool(result.stdout.strip())
    except:
        return False

def start_daemon():
    """Start the background daemon."""
    import threading
    
    def daemon_loop():
        while True:
            try:
                conn = init_db()
                c = conn.cursor()
                now = time.time()
                c.execute("SELECT id, message, remind_at FROM reminders WHERE notified=0 AND remind_at <= ?", (now,))
                due = c.fetchall()
                
                for rid, message, remind_at in due:
                    # Show notification
                    try:
                        subprocess.run([
                            'notify-send', '-u', 'normal', 
                            '⏰ Reminder', message
                        ], capture_output=True)
                    except:
                        print(f"\n🔔 REMINDER: {message}")
                    
                    # Mark as notified
                    c.execute("UPDATE reminders SET notified=1 WHERE id=?", (rid,))
                
                conn.commit()
                conn.close()
            except Exception as e:
                pass
            
            time.sleep(10)  # Check every 10 seconds
    
    # Check if already running
    if check_daemon():
        print("⚠️  Daemon already running")
        return
    
    # Start in background
    daemon_file = Path(__file__).parent / "remindme_daemon.py"
    subprocess.Popen([sys.executable, str(daemon_file)], 
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    start_new_session=True)
    print("✅ Daemon started in background")

def stop_daemon():
    """Stop the reminder daemon."""
    try:
        subprocess.run(['pkill', '-f', 'remindme_daemon'], capture_output=True)
        print("✅ Daemon stopped")
    except:
        print("❌ Failed to stop daemon")

def main():
    parser = argparse.ArgumentParser(description='Smart Reminder CLI')
    parser.add_argument('args', nargs='*', help='Time and message')
    parser.add_argument('-l', '--list', action='store_true', help='List reminders')
    parser.add_argument('-c', '--clear', nargs='?', const='all', help='Clear reminders')
    parser.add_argument('-d', '--daemon', choices=['start', 'stop', 'status'], help='Manage daemon')
    
    args = parser.parse_args()
    
    # Handle daemon commands
    if args.daemon:
        if args.daemon == 'start':
            start_daemon()
        elif args.daemon == 'stop':
            stop_daemon()
        elif args.daemon == 'status':
            if check_daemon():
                print("🟢 Daemon is running")
            else:
                print("🔴 Daemon is not running")
        return
    
    # List reminders
    if args.list:
        list_reminders()
        return
    
    # Clear reminders: -c with no arg clears all, -c <id> clears specific
    if args.clear is not None:
        clear_id = None if args.clear == 'all' else int(args.clear)
        clear_reminders(clear_id)
        return
    
    # Add reminder
    if not args.args:
        parser.print_help()
        print("\n💡 Examples:")
        print("  remindme in 30 minutes \"Call mom\"")
        print("  remindme at 5pm \"Check email\"")
        print("  remindme tomorrow 9am \"Standup\"")
        print("  remindme -l  # list reminders")
        print("  remindme -d start  # start daemon")
        return
    
    # Parse: need to reconstruct time string from first few args
    args_list = list(args.args)
    
    # Handle "in X minutes/hours/etc" - need to reconstruct
    if args_list and args_list[0] in ['in', 'at']:
        # Need at least 3 parts: "in 30 minutes" or "at 5pm"
        if len(args_list) >= 3:
            time_part = ' '.join(args_list[:3])
            message = ' '.join(args_list[3:])
        elif len(args_list) == 2:
            # "in 30" -> assume minutes
            time_part = f"in {args_list[1]} minutes"
            message = ''
        else:
            print("❌ Invalid time format")
            return
    else:
        # First arg might be the full time or message
        time_part = args_list[0]
        message = ' '.join(args_list[1:])
        
        # Check if first arg is time keyword or number
        if time_part not in ['in', 'at', 'tomorrow'] and not re.match(r'\d', time_part):
            # All args might be message, default to 1 hour
            time_part = 'in 1 hour'
            message = ' '.join(args_list)
    
    try:
        remind_at = parse_time(time_part)
        if not message:
            print("❌ Please provide a message")
            return
        add_reminder(message, remind_at)
    except ValueError as e:
        print(f"❌ {e}")
        print("💡 Try: remindme in 30 minutes \"do something\"")
        print("   Or: remindme at 5pm \"do something\"")

if __name__ == '__main__':
    main()
