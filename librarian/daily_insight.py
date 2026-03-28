#!/usr/bin/env python3
"""
Daily Search Insight - Analyzes research patterns

Run daily to learn what Tony is researching.
"""

import csv
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

LOG_PATH = Path(__file__).parent / "search_log.csv"
BRAIN_NOTES = "/media/tony/Drive2/Brain/notes/"

def get_todays_searches() -> list:
    """Get today's searches."""
    if not LOG_PATH.exists():
        return []
    
    today = datetime.now().date()
    searches = []
    with open(LOG_PATH, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dt = datetime.fromisoformat(row['timestamp']).date()
            if dt == today:
                searches.append(row['query'])
    return searches

def get_top_searches(days: int = 7, limit: int = 5) -> list:
    """Get top searches over N days."""
    if not LOG_PATH.exists():
        return []
    
    cutoff = datetime.now() - timedelta(days=days)
    counts = Counter()
    
    with open(LOG_PATH, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dt = datetime.fromisoformat(row['timestamp'])
            if dt >= cutoff:
                counts[row['query'].lower()] += 1
    
    return counts.most_common(limit)

def analyze_patterns() -> str:
    """Generate insight report."""
    todays = get_todays_searches()
    top_week = get_top_searches(7)
    
    if not todays and not top_week:
        return "No search data yet."
    
    report = ["📊 Daily Search Insight\n"]
    
    if todays:
        report.append(f"Today: {len(todays)} searches")
        report.append(f"  Topics: {', '.join(set(todays))}")
    else:
        report.append("Today: No searches")
    
    if top_week:
        report.append("\nThis week:")
        for query, count in top_week:
            report.append(f"  - {query}: {count}x")
    
    # Suggest Brain note if searching same thing often
    if top_week and top_week[0][1] >= 5:
        q = top_week[0][0]
        report.append(f"\n💡 Consider adding '{q}' to Brain?")
    
    return "\n".join(report)

if __name__ == "__main__":
    print(analyze_patterns())