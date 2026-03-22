#!/usr/bin/env python3
"""
Daily Log Generator
Creates comprehensive daily logs of all activities
Run at 11:55 PM each night
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

LOG_DIR = Path("/media/tony/Drive2/LOGS")
LOG_DIR.mkdir(exist_ok=True)

def get_date_str(days_ago=0):
    d = datetime.now() - timedelta(days=days_ago)
    return d.strftime("%Y-%m-%d")

def generate_log(date_str):
    """Generate a comprehensive log for the given date"""
    
    log_lines = []
    log_lines.append(f"# Daily Activity Log - {date_str}")
    log_lines.append(f"Generated: {datetime.now().isoformat()}")
    log_lines.append("")
    log_lines.append("=" * 60)
    log_lines.append("")
    
    # PDF Progress
    progress_file = "/media/tony/Drive2/Programs/pdf_to_text/progress.json"
    if os.path.exists(progress_file):
        with open(progress_file) as f:
            progress = json.load(f)
        log_lines.append("## PDF Processing")
        log_lines.append(f"- Text extracted: {len(progress.get('text_extracted', []))}")
        log_lines.append(f"- Summarized: {len(progress.get('summarized', []))}")
        log_lines.append(f"- Errors: {len(progress.get('errors', []))}")
        if progress.get('last_run'):
            log_lines.append(f"- Last run: {progress['last_run']}")
        log_lines.append("")
    
    # Brain Stats
    brain_db = "/media/tony/Drive2/Brain/brain.db"
    if os.path.exists(brain_db):
        import subprocess
        result = subprocess.run(
            ["sqlite3", brain_db, "SELECT COUNT(*) FROM notes;"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            note_count = result.stdout.strip()
            log_lines.append("## Brain Knowledge Base")
            log_lines.append(f"- Total notes: {note_count}")
            log_lines.append("")
    
    # Cron Jobs
    log_lines.append("## Cron Jobs Active")
    cron_jobs = [
        "PDF Batch Processor (every 5 min)",
        "System Monitor (every 5 min)",
        "Service Starter (every 5 min)",
        "Memory updater (every 5 min)",
        "Brain auto-sync (hourly)",
        "Brain PDF auto-import (every 5 min)",
        "Self-improvement (every 2 hours)",
        "Research Aggregator (every 2 hours)",
        "Brain Graph Updater (every 4 hours)",
        "Memory Librarian (every 4 hours)",
    ]
    for job in cron_jobs:
        log_lines.append(f"- {job}")
    log_lines.append("")
    
    # Services
    log_lines.append("## Services Status")
    services = [
        ("8080", "Brain Static Server"),
        ("8081", "Brain API"),
        ("8765", "System Dashboard"),
        ("8768", "brain_all Search"),
        ("11434", "Ollama"),
    ]
    for port, name in services:
        result = subprocess.run(
            ["bash", "-c", f"netstat -tln 2>/dev/null | grep -q ':{port}' && echo UP || echo DOWN"],
            capture_output=True, text=True
        )
        status = "UP" if "UP" in result.stdout else "DOWN"
        log_lines.append(f"- {name} ({port}): {status}")
    log_lines.append("")
    
    # Memory files
    log_lines.append("## Today's Memory")
    memory_file = f"/home/tony/.openclaw/workspace/memory/{date_str}.md"
    if os.path.exists(memory_file):
        with open(memory_file) as f:
            content = f.read()
        log_lines.append(f"```\n{content[:2000]}\n```")
    else:
        log_lines.append("(No memory file found)")
    log_lines.append("")
    
    # Disk usage
    log_lines.append("## System Resources")
    result = subprocess.run(["df", "-h", "/media/tony/Drive2"], capture_output=True, text=True)
    if result.returncode == 0:
        log_lines.append("```")
        log_lines.append(result.stdout)
        log_lines.append("```")
    
    log_lines.append("")
    log_lines.append("=" * 60)
    log_lines.append(f"*End of log for {date_str}*")
    
    return "\n".join(log_lines)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--days-ago", type=int, default=0, help="Generate log for N days ago")
    args = parser.parse_args()
    
    date_str = get_date_str(args.days_ago)
    log_content = generate_log(date_str)
    
    # Save to file
    log_file = LOG_DIR / f"{date_str}_log.md"
    log_file.write_text(log_content)
    print(f"Log saved: {log_file}")
    
    # Also print to stdout
    print(log_content)

if __name__ == "__main__":
    main()
