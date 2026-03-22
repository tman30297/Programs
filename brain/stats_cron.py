#!/usr/bin/env python3
"""
Brain Stats - Weekly cron to show statistics.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from brain import show_stats

def main():
    print("🧠 Brain Weekly Stats")
    print("=" * 40)
    show_stats()

if __name__ == "__main__":
    main()
