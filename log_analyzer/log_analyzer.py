#!/usr/bin/env python3
"""
Log File Analyzer - Analyze and parse log files
Usage: log_analyzer.py <file> [options]
Options:
  -n, --lines NUM      Show last N lines (default: 50)
  -e, --error          Show only error lines
  -w, --warning        Show only warning lines
  -i, --info           Show only info lines
  -g, --grep PATTERN   Search for pattern
  -s, --stats          Show log statistics
  -t, --tail           Follow log in real-time
  --since DATE         Show entries since date
  --until DATE         Show entries until date
  --json               Parse JSON logs
  --ip                 Extract IP addresses
  --url                Extract URLs
  --error-rate         Show error rate over time
"""

import os
import sys
import re
import argparse
import subprocess
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import json

def run_cmd(cmd, capture=True):
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    return result.returncode, result.stdout, result.stderr

def tail_file(filepath, lines=50):
    """Get last N lines of file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.readlines()
            return content[-lines:]
    except Exception as e:
        return [f"Error reading file: {e}"]

def filter_level(lines, level):
    """Filter log lines by level"""
    patterns = {
        'error': [r'\bERROR\b', r'\bFATAL\b', r'\bCRITICAL\b', r'\berror\b', r'\bfailed\b', r'\bfailure\b'],
        'warning': [r'\bWARN\b', r'\bWARNING\b', r'\bwarning\b'],
        'info': [r'\bINFO\b', r'\binfo\b'],
    }
    
    if level not in patterns:
        return lines
    
    regex = '|'.join(patterns[level])
    return [l for l in lines if re.search(regex, l, re.IGNORECASE)]

def grep_lines(lines, pattern):
    """Search for pattern in lines"""
    try:
        regex = re.compile(pattern, re.IGNORECASE)
        return [l for l in lines if regex.search(l)]
    except re.error:
        # Fall back to simple string search
        return [l for l in lines if pattern.lower() in l.lower()]

def extract_ips(lines):
    """Extract IP addresses from log lines"""
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    ips = []
    for line in lines:
        ips.extend(re.findall(ip_pattern, line))
    return Counter(ips)

def extract_urls(lines):
    """Extract URLs from log lines"""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = []
    for line in lines:
        urls.extend(re.findall(url_pattern, line))
    return Counter(urls)

def parse_json_logs(lines):
    """Parse JSON formatted logs"""
    parsed = []
    for line in lines:
        try:
            data = json.loads(line.strip())
            parsed.append(data)
        except json.JSONDecodeError:
            continue
    return parsed

def show_stats(lines):
    """Show log file statistics"""
    print(f"📊 Log Statistics for: {args.file}\n")
    print(f"  Total lines: {len(lines)}")
    
    # Line count by level
    errors = len(filter_level(lines, 'error'))
    warnings = len(filter_level(lines, 'warning'))
    infos = len(filter_level(lines, 'info'))
    
    print(f"  Errors:   {errors}")
    print(f"  Warnings: {warnings}")
    print(f"  Info:     {infos}")
    
    # Most common words
    word_counter = Counter()
    for line in lines:
        words = re.findall(r'\b\w+\b', line.lower())
        word_counter.update(words)
    
    # Filter common words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
                 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
                 'it', 'its', 'this', 'that', 'these', 'those', 'i', 'you', 'we', 'they'}
    
    meaningful = {w: c for w, c in word_counter.items() if w not in stop_words and len(w) > 2}
    
    print(f"\n  Most common terms:")
    for word, count in meaningful.most_common(10):
        print(f"    {word}: {count}")
    
    # Time-based analysis (try to extract timestamps)
    timestamps = []
    ts_patterns = [
        r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})',
        r'(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})',
        r'(\w{3} \d{2} \d{2}:\d{2}:\d{2})',
    ]
    
    for line in lines:
        for pattern in ts_patterns:
            match = re.search(pattern, line)
            if match:
                timestamps.append(match.group(1))
                break
    
    if timestamps:
        print(f"\n  Time range:")
        print(f"    First: {timestamps[0]}")
        print(f"    Last:  {timestamps[-1]}")

def error_rate_over_time(lines, interval_minutes=60):
    """Calculate error rate over time"""
    errors_by_time = defaultdict(int)
    
    # Try to parse timestamps
    ts_pattern = r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2})'
    
    for line in lines:
        if re.search(r'\bERROR\b|\bFATAL\b|\bfailed\b', line, re.IGNORECASE):
            match = re.search(ts_pattern, line)
            if match:
                # Round to interval
                ts = match.group(1)[:16]  # Get YYYY-MM-DD HH:MM
                errors_by_time[ts] += 1
    
    if not errors_by_time:
        print("❌ Could not parse timestamps")
        return
    
    print(f"\n📈 Error rate over time (by hour):\n")
    for ts in sorted(errors_by_time.keys()):
        bar = '█' * errors_by_time[ts]
        print(f"  {ts}: {bar} ({errors_by_time[ts]})")

def follow_log(filepath):
    """Follow log file in real-time"""
    print(f"📡 Following {filepath} (Ctrl+C to exit)...\n")
    cmd = f"tail -f {filepath}"
    subprocess.run(cmd, shell=True)

def main():
    global args
    parser = argparse.ArgumentParser(description="Log File Analyzer")
    parser.add_argument("file", nargs="?", help="Log file to analyze")
    parser.add_argument("-n", "--lines", type=int, default=50, help="Number of lines")
    parser.add_argument("-e", "--error", action="store_true", help="Show errors")
    parser.add_argument("-w", "--warning", action="store_true", help="Show warnings")
    parser.add_argument("-i", "--info", action="store_true", help="Show info")
    parser.add_argument("-g", "--grep", help="Search pattern")
    parser.add_argument("-s", "--stats", action="store_true", help="Show statistics")
    parser.add_argument("-t", "--tail", action="store_true", help="Follow log")
    parser.add_argument("--since", help="Since date")
    parser.add_argument("--until", help="Until date")
    parser.add_argument("--json", action="store_true", help="Parse JSON logs")
    parser.add_argument("--ip", action="store_true", help="Extract IP addresses")
    parser.add_argument("--url", action="store_true", help="Extract URLs")
    parser.add_argument("--error-rate", action="store_true", help="Show error rate")
    
    args = parser.parse_args()
    
    if not args.file:
        print(__doc__)
        return
    
    filepath = Path(args.file).expanduser()
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        return
    
    # Get lines
    lines = tail_file(filepath, args.lines)
    
    # Apply filters
    if args.error:
        lines = filter_level(lines, 'error')
    elif args.warning:
        lines = filter_level(lines, 'warning')
    elif args.info:
        lines = filter_level(lines, 'info')
    
    if args.grep:
        lines = grep_lines(lines, args.grep)
    
    # Special modes
    if args.stats:
        all_lines = tail_file(filepath, 10000)  # Get more for stats
        show_stats(all_lines)
        return
    
    if args.error_rate:
        all_lines = tail_file(filepath, 10000)
        error_rate_over_time(all_lines)
        return
    
    if args.ip:
        all_lines = tail_file(filepath, 5000)
        ips = extract_ips(all_lines)
        print("🔢 IP Addresses found:\n")
        for ip, count in ips.most_common(20):
            print(f"  {ip:<18} {count}")
        return
    
    if args.url:
        all_lines = tail_file(filepath, 5000)
        urls = extract_urls(all_lines)
        print("🔗 URLs found:\n")
        for url, count in urls.most_common(20):
            print(f"  {count:>3} - {url[:70]}")
        return
    
    if args.json:
        lines = parse_json_logs(lines)
        for entry in lines[:args.lines]:
            print(json.dumps(entry, indent=2))
        return
    
    if args.tail:
        follow_log(filepath)
        return
    
    # Default: show filtered lines
    for line in lines:
        # Colorize based on level
        if re.search(r'\bERROR\b|\bFATAL\b|\bCRITICAL\b', line, re.IGNORECASE):
            print(f"🔴 {line.rstrip()}")
        elif re.search(r'\bWARN\b|\bWARNING\b', line, re.IGNORECASE):
            print(f"🟡 {line.rstrip()}")
        elif re.search(r'\bINFO\b', line, re.IGNORECASE):
            print(f"🔵 {line.rstrip()}")
        else:
            print(line.rstrip())

if __name__ == "__main__":
    main()
