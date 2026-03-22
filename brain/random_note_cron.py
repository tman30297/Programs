#!/usr/bin/env python3
"""
Brain Random Note - Daily cron to show a random note for review.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from brain import random_note

def main():
    print("🎲 Brain Random Note (Daily Review)")
    print("=" * 50)
    random_note()

if __name__ == "__main__":
    main()
