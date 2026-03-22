#!/usr/bin/env python3
"""
Log Watcher - Real-time log file monitor with filtering and colorization
Usage: logwatch.py <logfile> [--pattern PATTERN] [--grep PATTERN] [--lines N] [--no-color]
"""

import argparse
import os
import sys
import time
import re
from collections import defaultdict, deque

# ANSI color codes
COLORS = {
    'red': '\033[91m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'magenta': '\033[95m',
    'cyan': '\033[96m',
    'white': '\033[97m',
    'reset': '\033[0m',
    'bold': '\033[1m',
}

# Log level color mapping
LEVEL_COLORS = {
    'ERROR': 'red',
    'FATAL': 'red',
    'CRITICAL': 'red',
    'WARN': 'yellow',
    'WARNING': 'yellow',
    'INFO': 'green',
    'DEBUG': 'cyan',
    'TRACE': 'white',
}

def colorize(text, color, use_color=True):
    """Apply color to text if colors are enabled."""
    if not use_color or color not in COLORS:
        return text
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"

def detect_level(line, use_color=True):
    """Detect log level and colorize accordingly."""
    for level, color in LEVEL_COLORS.items():
        if f'[{level}]' in line.upper() or f' {level} ' in line.upper():
            return colorize(line, color, use_color)
    return line

def tail_file(filepath, n=10):
    """Get last n lines of a file."""
    try:
        with open(filepath, 'r') as f:
            return deque(f, n)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied for '{filepath}'", file=sys.stderr)
        sys.exit(1)

def watch_log(filepath, pattern=None, grep=None, lines=0, use_color=True, stats=False):
    """Watch log file in real-time with optional filtering."""
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Track stats if enabled
    level_counts = defaultdict(int) if stats else None
    
    # Get initial file size
    file_size = os.path.getsize(filepath)
    
    # Show last n lines first
    if lines > 0:
        for line in tail_file(filepath, lines):
            line = line.rstrip()
            if grep and grep.lower() not in line.lower():
                continue
            if pattern and not re.search(pattern, line):
                continue
            if stats:
                for level in LEVEL_COLORS.keys():
                    if level in line.upper():
                        level_counts[level] += 1
                        break
            print(colorize(line, detect_level(line, use_color).split('\033[')[0] if use_color else '', use_color) if use_color else line)
    
    print(f"\n--- Watching {filepath} (Press Ctrl+C to stop) ---")
    
    try:
        while True:
            try:
                new_size = os.path.getsize(filepath)
            except OSError:
                break
            
            if new_size > file_size:
                with open(filepath, 'r') as f:
                    f.seek(file_size)
                    for line in f:
                        line = line.rstrip()
                        if grep and grep.lower() not in line.lower():
                            continue
                        if pattern and not re.search(pattern, line):
                            continue
                        if stats:
                            for level in LEVEL_COLORS.keys():
                                if level in line.upper():
                                    level_counts[level] += 1
                                    break
                        
                        # Colorize based on log level
                        if use_color:
                            level_color = None
                            for lvl, clr in LEVEL_COLORS.items():
                                if lvl in line.upper():
                                    level_color = clr
                                    break
                            print(colorize(line, level_color, True))
                        else:
                            print(line)
                
                file_size = new_size
            elif new_size < file_size:
                # File was truncated, reset
                print("\n--- File truncated, restarting ---")
                file_size = 0
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        if stats and level_counts:
            print("\n--- Log Level Statistics ---")
            for level, count in sorted(level_counts.items(), key=lambda x: -x[1]):
                color = LEVEL_COLORS.get(level, 'white')
                print(colorize(f"  {level}: {count}", color, use_color))

def main():
    parser = argparse.ArgumentParser(
        description='Real-time log file monitor with filtering',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s /var/log/syslog                    # Watch syslog
  %(prog)s app.log --lines 20                 # Show last 20 lines first
  %(prog)s app.log --grep ERROR                # Filter for ERROR lines
  %(prog)s app.log --pattern "\\d+\\.\\d+\\.\\d+"  # Filter by regex
  %(prog)s app.log --stats                     # Show log level statistics
  %(prog)s app.log --no-color                  # Disable colors
        '''
    )
    parser.add_argument('logfile', help='Path to log file to watch')
    parser.add_argument('-n', '--lines', type=int, default=0, 
                        help='Number of initial lines to show (default: 0)')
    parser.add_argument('-g', '--grep', 
                        help='Filter lines containing this text')
    parser.add_argument('-p', '--pattern', 
                        help='Filter lines matching this regex pattern')
    parser.add_argument('-s', '--stats', action='store_true',
                        help='Show log level statistics on exit')
    parser.add_argument('--no-color', action='store_true',
                        help='Disable colored output')
    
    args = parser.parse_args()
    
    use_color = not args.no_color and sys.stdout.isatty()
    
    watch_log(
        args.logfile,
        pattern=args.pattern,
        grep=args.grep,
        lines=args.lines,
        use_color=use_color,
        stats=args.stats
    )

if __name__ == '__main__':
    main()
