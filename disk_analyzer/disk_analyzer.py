#!/usr/bin/env python3
"""
Disk Usage Analyzer - Find large files and directories
"""

import os
import sys
from pathlib import Path

def get_size(path):
    """Get size of file or directory in bytes."""
    try:
        if os.path.isfile(path):
            return os.path.getsize(path)
        elif os.path.isdir(path):
            total = 0
            for entry in os.scandir(path):
                try:
                    if entry.is_file(follow_symlinks=False):
                        total += entry.stat(follow_symlinks=False).st_size
                    elif entry.is_dir(follow_symlinks=False):
                        total += get_size(entry.path)
                except (PermissionError, OSError):
                    pass
            return total
    except (PermissionError, OSError):
        return 0
    return 0

def format_size(size):
    """Format bytes to human readable."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"

def scan_directory(path, top_n=20):
    """Scan directory and return largest items."""
    path = Path(path).resolve()
    items = []
    
    print(f"Scanning {path}...")
    
    # Get immediate children
    try:
        for entry in os.scandir(path):
            size = get_size(entry.path)
            items.append((size, entry.name, entry.is_dir()))
    except PermissionError:
        print("Permission denied")
        return
    
    # Sort by size
    items.sort(reverse=True)
    
    print(f"\n{'Size':>12} {'Type':<6} Name")
    print("-" * 60)
    
    for size, name, is_dir in items[:top_n]:
        dtype = "DIR " if is_dir else "FILE"
        print(f"{format_size(size):>12} {dtype:<6} {name}")

def find_large_files(path, min_size_mb=10):
    """Find files larger than min_size_mb MB recursively."""
    min_size = min_size_mb * 1024 * 1024
    path = Path(path).resolve()
    large_files = []
    
    print(f"Finding files larger than {min_size_mb}MB in {path}...")
    
    for root, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            try:
                size = os.path.getsize(fp)
                if size >= min_size:
                    large_files.append((size, fp))
            except OSError:
                pass
    
    large_files.sort(reverse=True)
    
    print(f"\nFound {len(large_files)} large files:\n")
    print(f"{'Size':>12} Path")
    print("-" * 80)
    for size, fp in large_files:
        print(f"{format_size(size):>12} {fp}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Disk Usage Analyzer")
    parser.add_argument("path", nargs="?", default=".", help="Directory to analyze")
    parser.add_argument("--top", type=int, default=20, help="Number of top items to show")
    parser.add_argument("--large", type=int, help="Find files larger than N MB")
    args = parser.parse_args()
    
    if args.large:
        find_large_files(args.path, args.large)
    else:
        scan_directory(args.path, args.top)

if __name__ == "__main__":
    main()
