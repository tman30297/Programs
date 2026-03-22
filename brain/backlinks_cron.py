#!/usr/bin/env python3
"""
Brain Backlinks Finder - Daily cron to find new backlinks.
Does small batches to save resources.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from brain import find_backlinks, show_backlinks, NOTES_DIR

def main():
    print("🔗 Brain Backlinks Finder (Daily)")
    print("-" * 30)
    
    # Find backlinks
    backlinks = find_backlinks(max_notes=10)
    
    if backlinks:
        print(f"\n📋 Found {len(backlinks)} backlinks")
        print("   Run 'brain.py backlinks' to see details")
    else:
        print("ℹ️ No new backlinks found")
        print("   Add references like 'see note #5' in your notes!")

if __name__ == "__main__":
    main()
