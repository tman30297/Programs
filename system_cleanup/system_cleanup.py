#!/usr/bin/env python3
"""
System Cleanup Utility
Cleans temporary files, caches, and helps free up disk space.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# Colors for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def format_size(size_bytes):
    """Format bytes to human readable size."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"

def get_dir_size(path):
    """Get total size of a directory."""
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total += os.path.getsize(fp)
                except (OSError, FileNotFoundError):
                    pass
    except PermissionError:
        pass
    return total

def clean_temp_files(dry_run=False):
    """Clean temporary files."""
    cleaned = 0
    paths = [
        Path('/tmp'),
        Path('/var/tmp'),
        Path.home() / '.cache',
    ]
    
    # Also check user temp on Windows-like paths
    if os.name == 'nt':
        paths.append(Path(os.environ.get('TEMP', '')))
    
    for path in paths:
        if not path.exists():
            continue
        
        print(f"{Colors.BLUE}Scanning: {path}{Colors.RESET}")
        count = 0
        size = 0
        
        try:
            for item in path.iterdir():
                try:
                    # Skip files older than 24 hours
                    mtime = datetime.fromtimestamp(item.stat().st_mtime)
                    if datetime.now() - mtime < timedelta(hours=24):
                        continue
                    
                    item_size = item.stat().st_size if item.is_file() else get_dir_size(item)
                    size += item_size
                    count += 1
                    
                    if not dry_run:
                        if item.is_file():
                            item.unlink()
                        else:
                            shutil.rmtree(item)
                except (OSError, PermissionError):
                    pass
        except PermissionError:
            print(f"  {Colors.YELLOW}Permission denied: {path}{Colors.RESET}")
            continue
        
        if count > 0:
            print(f"  {Colors.GREEN}Found {count} items ({format_size(size)}){Colors.RESET}")
            cleaned += size
    
    return cleaned

def clean_browser_cache(browser='all', dry_run=False):
    """Clean browser caches."""
    cleaned = 0
    home = Path.home()
    
    browser_paths = {}
    
    # Chrome
    if browser in ['all', 'chrome']:
        browser_paths['Chrome'] = [
            home / '.cache' / 'google-chrome',
            home / '.config' / 'google-chrome' / 'Default' / 'Cache',
            home / '.config' / 'google-chrome' / 'Default' / 'Code Cache',
        ]
    
    # Firefox
    if browser in ['all', 'firefox']:
        firefox_profiles = home / '.mozilla' / 'firefox'
        if firefox_profiles.exists():
            for profile in firefox_profiles.iterdir():
                if profile.is_dir():
                    browser_paths.setdefault('Firefox', []).extend([
                        profile / 'cache2',
                        profile / 'startupCache',
                    ])
    
    # Edge
    if browser in ['all', 'edge']:
        browser_paths['Edge'] = [
            home / '.cache' / 'microsoft-edge',
            home / '.config' / 'microsoft-edge' / 'Default' / 'Cache',
        ]
    
    for browser_name, paths in browser_paths.items():
        print(f"{Colors.BLUE}Scanning {browser_name} cache:{Colors.RESET}")
        count = 0
        size = 0
        
        for path in paths:
            if not path.exists():
                continue
            
            try:
                if path.is_file():
                    size += path.stat().st_size
                    count += 1
                    if not dry_run:
                        path.unlink()
                else:
                    size += get_dir_size(path)
                    count += sum(1 for _ in path.rglob('*') if _.is_file())
                    if not dry_run:
                        shutil.rmtree(path)
            except (OSError, PermissionError) as e:
                print(f"  {Colors.YELLOW}Error: {e}{Colors.RESET}")
        
        if count > 0:
            print(f"  {Colors.GREEN}Found {count} items ({format_size(size)}){Colors.RESET}")
            cleaned += size
    
    return cleaned

def clean_python_cache(dry_run=False):
    """Clean Python cache files (__pycache__, .pyc, etc.)."""
    cleaned = 0
    print(f"{Colors.BLUE}Scanning for Python cache files...{Colors.RESET}")
    
    count = 0
    size = 0
    
    for path in Path.home().rglob('__pycache__'):
        try:
            path_size = get_dir_size(path)
            size += path_size
            count += 1
            if not dry_run:
                shutil.rmtree(path)
        except (OSError, PermissionError):
            pass
    
    for path in Path.home().rglob('*.pyc'):
        try:
            size += path.stat().st_size
            count += 1
            if not dry_run:
                path.unlink()
        except (OSError, PermissionError):
            pass
    
    for path in Path.home().rglob('*.pyo'):
        try:
            size += path.stat().st_size
            count += 1
            if not dry_run:
                path.unlink()
        except (OSError, PermissionError):
            pass
    
    if count > 0:
        print(f"  {Colors.GREEN}Found {count} Python cache items ({format_size(size)}){Colors.RESET}")
        cleaned += size
    
    return cleaned

def clean_logs(dry_run=False, older_than_days=7):
    """Clean old log files."""
    cleaned = 0
    print(f"{Colors.BLUE}Scanning for old log files...{Colors.RESET}")
    
    log_paths = [
        Path('/var/log'),
        Path.home() / '.local' / 'share' / 'Trash',
    ]
    
    count = 0
    size = 0
    cutoff = datetime.now() - timedelta(days=older_than_days)
    
    for base_path in log_paths:
        if not base_path.exists():
            continue
        
        try:
            for path in base_path.rglob('*.log'):
                try:
                    mtime = datetime.fromtimestamp(path.stat().st_mtime)
                    if mtime < cutoff:
                        path_size = path.stat().st_size
                        size += path_size
                        count += 1
                        if not dry_run:
                            path.unlink()
                except (OSError, FileNotFoundError):
                    pass
        except PermissionError:
            pass
    
    if count > 0:
        print(f"  {Colors.GREEN}Found {count} old log files ({format_size(size)}){Colors.RESET}")
        cleaned += size
    
    return cleaned

def clean_downloads(dry_run=False, older_than_days=90):
    """Clean old files in Downloads folder."""
    cleaned = 0
    downloads = Path.home() / 'Downloads'
    
    if not downloads.exists():
        return 0
    
    print(f"{Colors.BLUE}Scanning Downloads folder...{Colors.RESET}")
    
    count = 0
    size = 0
    cutoff = datetime.now() - timedelta(days=older_than_days)
    
    # Only auto-clean common installer/package types
    safe_extensions = {'.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm', '.AppImage'}
    
    for path in downloads.iterdir():
        try:
            if path.is_file():
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                if mtime < cutoff and path.suffix.lower() in safe_extensions:
                    size += path.stat().st_size
                    count += 1
                    if not dry_run:
                        print(f"    Removing: {path.name}")
                        path.unlink()
        except (OSError, FileNotFoundError):
            pass
    
    if count > 0:
        print(f"  {Colors.GREEN}Found {count} old installer files ({format_size(size)}){Colors.RESET}")
        cleaned += size

    return cleaned

def clean_thumbnail_cache(dry_run=False):
    """Clean thumbnail caches."""
    cleaned = 0
    thumb_paths = [
        Path.home() / '.cache' / 'thumbnails',
        Path.home() / '.thumbnails',
    ]
    
    for path in thumb_paths:
        if not path.exists():
            continue
        
        print(f"{Colors.BLUE}Scanning: {path}{Colors.RESET}")
        
        count = 0
        size = 0
        
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    try:
                        size += item.stat().st_size
                        count += 1
                        if not dry_run:
                            item.unlink()
                    except (OSError, FileNotFoundError):
                        pass
        except PermissionError:
            pass
        
        if count > 0:
            print(f"  {Colors.GREEN}Found {count} thumbnails ({format_size(size)}){Colors.RESET}")
            cleaned += size
    
    return cleaned

def show_disk_usage():
    """Show current disk usage."""
    print(f"\n{Colors.BOLD}Disk Usage:{Colors.RESET}")
    
    try:
        usage = shutil.disk_usage('/')
        print(f"  Total: {format_size(usage.total)}")
        print(f"  Used:  {format_size(usage.used)}")
        print(f"  Free:  {format_size(usage.free)}")
        print(f"  Usage: {usage.used / usage.total * 100:.1f}%")
    except Exception as e:
        print(f"  Error: {e}")

def main():
    parser = argparse.ArgumentParser(
        description='System Cleanup Utility - Free up disk space',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Interactive mode
  %(prog)s --dry-run          # Preview what would be cleaned
  %(prog)s --temp --browser   # Clean temp and browser cache
  %(prog)s --all              # Clean everything
  %(prog)s --size             # Show disk usage
        """
    )
    
    parser.add_argument('--dry-run', '-n', action='store_true',
                        help='Preview what would be cleaned without deleting')
    parser.add_argument('--temp', '-t', action='store_true',
                        help='Clean temporary files')
    parser.add_argument('--browser', '-b', action='store_true',
                        help='Clean browser cache')
    parser.add_argument('--python', '-p', action='store_true',
                        help='Clean Python cache files')
    parser.add_argument('--logs', '-l', action='store_true',
                        help='Clean old log files')
    parser.add_argument('--downloads', '-d', action='store_true',
                        help='Clean old files in Downloads')
    parser.add_argument('--thumbnails', action='store_true',
                        help='Clean thumbnail cache')
    parser.add_argument('--all', '-a', action='store_true',
                        help='Clean everything')
    parser.add_argument('--size', '-s', action='store_true',
                        help='Show disk usage')
    parser.add_argument('--older-than', type=int, default=7,
                        help='For logs: delete files older than N days (default: 7)')
    
    args = parser.parse_args()
    
    # Show disk usage
    show_disk_usage()
    
    # If no specific options, run in interactive mode
    if not any([args.temp, args.browser, args.python, args.logs, 
                args.downloads, args.thumbnails, args.all, args.size]):
        args.temp = True
        args.browser = True
        args.thumbnails = True
    
    if args.size:
        sys.exit(0)
    
    if args.dry_run:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}=== DRY RUN MODE ==={Colors.RESET}")
        print(f"{Colors.YELLOW}No files will be deleted. Use without -n to actually clean.{Colors.RESET}\n")
    
    total_cleaned = 0
    
    if args.temp or args.all:
        print(f"\n{Colors.BOLD}Cleaning temporary files...{Colors.RESET}")
        total_cleaned += clean_temp_files(args.dry_run)
    
    if args.browser or args.all:
        print(f"\n{Colors.BOLD}Cleaning browser cache...{Colors.RESET}")
        total_cleaned += clean_browser_cache(dry_run=args.dry_run)
    
    if args.python or args.all:
        print(f"\n{Colors.BOLD}Cleaning Python cache...{Colors.RESET}")
        total_cleaned += clean_python_cache(args.dry_run)
    
    if args.logs or args.all:
        print(f"\n{Colors.BOLD}Cleaning old logs...{Colors.RESET}")
        total_cleaned += clean_logs(args.dry_run, args.older_than)
    
    if args.downloads or args.all:
        print(f"\n{Colors.BOLD}Cleaning old Downloads...{Colors.RESET}")
        total_cleaned += clean_downloads(args.dry_run)
    
    if args.thumbnails or args.all:
        print(f"\n{Colors.BOLD}Cleaning thumbnail cache...{Colors.RESET}")
        total_cleaned += clean_thumbnail_cache(args.dry_run)
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}Total space {'would be ' if args.dry_run else ''}freed: {format_size(total_cleaned)}{Colors.RESET}")
    
    show_disk_usage()
    
    if args.dry_run:
        print(f"\n{Colors.YELLOW}Run again without --dry-run to actually delete these files.{Colors.RESET}")

if __name__ == '__main__':
    main()
