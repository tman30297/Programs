#!/usr/bin/env python3
"""
Brain Related Sources - Daily cron to find related notes by source.
Does small batches to save resources.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from brain import find_related_by_source, show_related_by_source

def main():
    print("🔗 Brain Related Sources (Daily)")
    print("-" * 30)
    
    # Find related by source
    related = find_related_by_source(limit=5)
    
    if related:
        print(f"\n📋 Found {len(related)} sources with related notes")
        print("   Run 'brain.py related' to see details")
    else:
        print("ℹ️ No new related notes found")

if __name__ == "__main__":
    main()
