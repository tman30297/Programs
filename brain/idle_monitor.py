#!/usr/bin/env python3
"""
Idle Detector - Monitors user activity and runs Brain tasks when idle.
"""

import subprocess
import os
import time

# Check if user is active by checking:
# 1. SSH sessions
# 2. Terminal activity
# 3. Last input

def check_user_activity():
    """Check if user is active on the system."""
    
    # Check for active SSH sessions (excluding this script)
    result = subprocess.run(
        ["who"],
        capture_output=True, text=True
    )
    
    # If someone is logged in via SSH or tty
    if result.stdout.strip():
        # Check for active terminal sessions
        w_output = result.stdout.lower()
        
        # If there are active sessions, check for recent activity
        # Check last command run
        last_result = subprocess.run(
            ["last", "-n", "1", "-i"],
            capture_output=True, text=True
        )
        
        if "still logged in" in last_result.stdout.lower():
            return True  # User is active
    
    # Check for recent keyboard/mouse activity via X or console
    # Check last input device
    if os.path.exists("/var/run/utmp"):
        result = subprocess.run(
            ["last", "-n", "1", "-x", "shutdown"],
            capture_output=True, text=True
        )
        # If system is running and users logged in
        if "wtmp" in result.stdout or "still logged in" in result.stdout:
            return True
    
    # Check for desktop session (X11/Wayland)
    result = subprocess.run(
        ["loginctl", "list-sessions"],
        capture_output=True, text=True
    )
    if result.returncode == 0 and result.stdout.strip():
        return True
    
    return False  # No activity detected

def run_brain_tasks():
    """Run Brain improvement tasks."""
    tasks = [
        # Import PDFs
        ["python3", "/media/tony/Drive2/Programs/brain/pdf_auto_import.py"],
        # Sync external sources
        ["python3", "/media/tony/Drive2/Programs/brain/auto_sync.py"],
        # Import RSS
        ["python3", "/media/tony/Drive2/Programs/brain/rss_importer.py"],
        # Export for browser
        ["python3", "/media/tony/Drive2/Programs/brain/brain.py", "export"],
    ]
    
    for task in tasks:
        print(f"Running: {' '.join(task)}")
        try:
            result = subprocess.run(task, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print(f"✓ Success")
            else:
                print(f"⚠ Error: {result.stderr[:100]}")
        except Exception as e:
            print(f"✗ Failed: {e}")

def main():
    import sys
    
    # Check if already running
    pid_file = "/tmp/idle_brain.pid"
    
    if len(sys.argv) > 1 and sys.argv[1] == "--stop":
        # Stop the idle monitor
        if os.path.exists(pid_file):
            with open(pid_file) as f:
                pid = int(f.read().strip())
            try:
                os.kill(pid, 9)
            except:
                pass
            os.remove(pid_file)
        print("Idle monitor stopped")
        return
    
    # Write PID
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))
    
    print("🧠 Idle Brain Monitor started")
    print("Checking every 30 minutes for user idle...")
    
    idle_count = 0
    IDLE_THRESHOLD = 2  # 2 checks = 1 hour (but we'll check every 30 min)
    
    while True:
        is_active = check_user_activity()
        
        if is_active:
            print("👤 User is active")
            idle_count = 0
        else:
            idle_count += 1
            print(f"😴 User idle for {idle_count * 30} minutes")
            
            if idle_count >= IDLE_THRESHOLD:
                print("🚀 User idle > 1 hour - Running Brain tasks...")
                run_brain_tasks()
                idle_count = 0  # Reset after running
        
        time.sleep(1800)  # Sleep 30 minutes

if __name__ == "__main__":
    main()
