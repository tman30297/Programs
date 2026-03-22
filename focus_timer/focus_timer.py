#!/usr/bin/env python3
"""
Focus Timer - A simple productivity timer with Pomodoro support
Usage: focus [minutes] [--pomodoro] [--break]
"""

import argparse
import time
import os
import sys

def notify(title, message):
    """Send desktop notification"""
    if sys.platform == "linux":
        os.system(f'notify-send "{title}" "{message}" 2>/dev/null')
    elif sys.platform == "darwin":
        os.system(f'osascript -e \'display notification "{message}" with title "{title}"\'')
    else:
        print(f"\n🔔 {title}: {message}")

def format_time(seconds):
    """Format seconds into MM:SS"""
    mins, secs = divmod(seconds, 60)
    return f"{mins:02d}:{secs:02d}"

def countdown(minutes, message="Timer done!"):
    """Run a countdown timer"""
    total_seconds = minutes * 60
    
    print(f"\n⏱️  Starting {minutes} minute timer...")
    print("Press Ctrl+C to cancel\n")
    
    try:
        while total_seconds > 0:
            sys.stdout.write(f"\r{format_time(total_seconds)} ")
            sys.stdout.flush()
            time.sleep(1)
            total_seconds -= 1
        
        print(f"\n\n✅ {message}")
        notify("Focus Timer", message)
        return True
        
    except KeyboardInterrupt:
        print("\n\n❌ Timer cancelled")
        return False

def pomodoro(work_minutes=25, break_minutes=5, cycles=4):
    """Run Pomodoro technique"""
    print(f"\n🍅 Starting Pomodoro: {cycles} work sessions of {work_minutes}min, {break_minutes}min breaks\n")
    
    for i in range(1, cycles + 1):
        print(f"\n--- Session {i}/{cycles} ---")
        if countdown(work_minutes, f"Work session {i} complete! Take a break."):
            if i < cycles:
                print(f"\n☕ Break time! ({break_minutes} min)")
                countdown(break_minutes, "Break over! Back to work!")
        else:
            print("Pomodoro cancelled")
            return
    
    print("\n🎉 All cycles complete! Great work!")

def main():
    parser = argparse.ArgumentParser(description="Focus Timer - Productivity timer")
    parser.add_argument("minutes", nargs="?", type=int, default=25, help="Minutes for timer (default: 25)")
    parser.add_argument("-p", "--pomodoro", action="store_true", help="Run Pomodoro technique")
    parser.add_argument("-b", "--break", dest="is_break", action="store_true", help="Short break timer")
    parser.add_argument("-w", "--work", type=int, default=25, help="Work minutes for pomodoro (default: 25)")
    parser.add_argument("-r", "--rest", type=int, default=5, help="Break minutes for pomodoro (default: 5)")
    parser.add_argument("-c", "--cycles", type=int, default=4, help="Number of pomodoro cycles (default: 4)")
    
    args = parser.parse_args()
    
    if args.pomodoro:
        pomodoro(args.work, args.rest, args.cycles)
    elif args.is_break:
        countdown(args.minutes, "Break is over!")
    else:
        countdown(args.minutes)

if __name__ == "__main__":
    main()
