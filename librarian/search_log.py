#!/usr/bin/env python3
"""
Search Audit Log - Tracks PDF searches over time

Provides insight into research patterns.
"""

import csv
import os
from datetime import datetime
from pathlib import Path

LOG_PATH = Path(__file__).parent / "search_log.csv"

def log_search(query: str, results_count: int) -> None:
    """Append search to audit log."""
    file_exists = LOG_PATH.exists()
    with open(LOG_PATH, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['query', 'timestamp', 'results_count'])
        writer.writerow([query, datetime.now().isoformat(), results_count])

def get_popular_searches(limit: int = 10) -> list:
    """Get most frequent searches."""
    if not LOG_PATH.exists():
        return []
    
    counts = {}
    with open(LOG_PATH, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            q = row['query'].lower()
            counts[q] = counts.get(q, 0) + 1
    
    sorted_q = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [{'query': q, 'count': c} for q, c in sorted_q[:limit]]

def get_recent_searches(limit: int = 10) -> list:
    """Get recent searches."""
    if not LOG_PATH.exists():
        return []
    
    searches = []
    with open(LOG_PATH, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            searches.append(row)
    
    return searches[-limit:][::-1]

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: search_log.py popular|recent")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "popular":
        for item in get_popular_searches():
            print(f"{item['count']:3d} x {item['query']}")
    elif cmd == "recent":
        for item in get_recent_searches():
            print(f"{item['timestamp'][:19]} - {item['query']} ({item['results_count']} results)")