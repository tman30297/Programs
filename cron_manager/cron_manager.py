#!/usr/bin/env python3
"""
Cron Job Manager - Manage system and user cron jobs
Usage: cron_manager.py <command> [options]
Commands:
  list                 List all user crontab entries
  list-system          List system cron jobs (/etc/cron.d, /etc/crontab)
  add <schedule> <cmd> Add a new cron job
  remove <pattern>     Remove cron jobs matching pattern
  backup               Backup current crontab
  restore              Restore from backup
  next                 Show next run times
  edit                 Edit crontab in $EDITOR
"""

import os
import sys
import subprocess
import argparse
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import re

CRON_BACKUP_DIR = Path("/media/tony/Drive2/Programs/cron_backups")

def run_cmd(cmd, capture=True):
    """Run shell command"""
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    return result.returncode, result.stdout, result.stderr

def parse_crontab():
    """Parse current crontab"""
    code, out, _ = run_cmd("crontab -l 2>/dev/null")
    if code == 0 and out:
        return out.strip().split('\n')
    return []

def list_crons():
    """List all user cron jobs"""
    jobs = parse_crontab()
    
    if not jobs or (len(jobs) == 1 and not jobs[0].strip()):
        print("📋 No crontab entries found")
        return
    
    print("📋 User Crontab:\n")
    print(f"{'Schedule':<20} {'Command':<50}")
    print("-" * 70)
    
    for job in jobs:
        job = job.strip()
        if not job or job.startswith('#'):
            continue
        
        parts = job.split(None, 5)
        if len(parts) >= 6:
            schedule = ' '.join(parts[:5])
            command = parts[5][:47] + '...' if len(parts[5]) > 50 else parts[5]
            print(f"{schedule:<20} {command:<50}")
        else:
            print(f"{job[:70]}")

def list_system_crons():
    """List system cron jobs"""
    print("📋 System Cron Jobs:\n")
    
    system_crons = [
        Path("/etc/crontab"),
        Path("/etc/cron.d"),
    ]
    
    for sc in system_crons:
        if sc.is_file():
            print(f"--- {sc} ---")
            print(sc.read_text())
        elif sc.is_dir():
            print(f"--- {sc}/ ---")
            for f in sorted(sc.iterdir()):
                if f.is_file() and not f.name.startswith('.'):
                    print(f"\n### {f.name} ###")
                    print(f.read_text())

def add_cron(schedule, command, comment=None):
    """Add a new cron job"""
    jobs = parse_crontab()
    
    entry = f"{schedule} {command}"
    if comment:
        entry = f"# {comment}\n{entry}"
    
    jobs.append(entry)
    
    # Write to temp file and install
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cron', delete=False) as f:
        f.write('\n'.join(jobs))
        f.write('\n')
        temp_path = f.name
    
    code, out, err = run_cmd(f"crontab {temp_path}")
    os.unlink(temp_path)
    
    if code == 0:
        print(f"✅ Added cron job: {schedule} {command}")
    else:
        print(f"❌ Error: {err}")

def remove_cron(pattern):
    """Remove cron jobs matching pattern"""
    jobs = parse_crontab()
    original_count = len(jobs)
    
    new_jobs = [j for j in jobs if pattern not in j]
    
    if len(new_jobs) == original_count:
        print(f"❌ No jobs matching '{pattern}' found")
        return
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cron', delete=False) as f:
        f.write('\n'.join(new_jobs))
        f.write('\n')
        temp_path = f.name
    
    code, out, err = run_cmd(f"crontab {temp_path}")
    os.unlink(temp_path)
    
    if code == 0:
        print(f"✅ Removed {original_count - len(new_jobs)} job(s) matching '{pattern}'")
    else:
        print(f"❌ Error: {err}")

def backup_crons():
    """Backup current crontab"""
    CRON_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    jobs = parse_crontab()
    if not jobs or (len(jobs) == 1 and not jobs[0].strip()):
        print("❌ No crontab to backup")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = CRON_BACKUP_DIR / f"crontab_{timestamp}.bak"
    
    backup_file.write_text('\n'.join(jobs))
    print(f"✅ Backed up crontab to {backup_file}")

def restore_crons():
    """Restore crontab from backup"""
    backups = sorted(CRON_BACKUP_DIR.glob("crontab_*.bak"), reverse=True)
    
    if not backups:
        print(f"❌ No backups found in {CRON_BACKUP_DIR}")
        return
    
    print("Available backups:")
    for i, b in enumerate(backups[:10]):
        print(f"  {i+1}. {b.name}")
    
    try:
        choice = int(input("\nSelect backup number: ")) - 1
        if 0 <= choice < len(backups):
            backup = backups[choice]
            code, out, err = run_cmd(f"crontab {backup}")
            if code == 0:
                print(f"✅ Restored from {backup.name}")
            else:
                print(f"❌ Error: {err}")
    except ValueError:
        print("❌ Invalid selection")

def show_next_runs():
    """Show next run times for cron jobs"""
    jobs = parse_crontab()
    
    print("⏰ Next scheduled runs:\n")
    
    for job in jobs:
        job = job.strip()
        if not job or job.startswith('#'):
            continue
        
        parts = job.split(None, 5)
        if len(parts) >= 6:
            schedule = ' '.join(parts[:5])
            command = parts[5][:50]
            
            # Try to get next run time
            code, out, err = run_cmd(f"echo '{schedule}' | atq 2>/dev/null | head -1")
            
            print(f"  {schedule}")
            print(f"    → {command}")
            print()

def edit_crontab():
    """Edit crontab in editor"""
    editor = os.environ.get('EDITOR', 'nano')
    code, out, err = run_cmd(f"{editor} <(crontab -l 2>/dev/null) && crontab <(crontab -l 2>/dev/null)")
    if code == 0:
        print("✅ Crontab updated")
    else:
        print(f"❌ Error: {err}")

def main():
    parser = argparse.ArgumentParser(description="Cron Job Manager")
    parser.add_argument("command", nargs="?", help="Command to run")
    parser.add_argument("args", nargs="*", help="Arguments")
    
    args = parser.parse_args()
    cmd = args.command
    
    if not cmd or cmd == "list":
        list_crons()
    elif cmd == "list-system":
        list_system_crons()
    elif cmd == "add" and len(args.args) >= 2:
        add_cron(args.args[0], ' '.join(args.args[1:]))
    elif cmd == "remove" and args.args:
        remove_cron(args.args[0])
    elif cmd == "backup":
        backup_crons()
    elif cmd == "restore":
        restore_crons()
    elif cmd == "next":
        show_next_runs()
    elif cmd == "edit":
        edit_crontab()
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
