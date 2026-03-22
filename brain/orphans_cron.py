#!/usr/bin/env python3
"""
Brain Orphans Finder - Daily cron to find unconnected notes.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from brain import find_orphans, show_orphans

def main():
    print("🔍 Brain Orphans Finder (Daily)")
    print("-" * 30)
    
    orphans = find_orphans()
    
    if orphans:
        print(f"\n📋 Found {len(orphans)} orphan notes")
        print("   Run 'brain.py orphans' to see details")
    else:
        print("✅ No orphans - all notes are connected!")

if __name__ == "__main__":
    main()
