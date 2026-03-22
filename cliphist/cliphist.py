#!/usr/bin/env python3
"""
ClipHist - Clipboard History Manager
Save, search, and manage your clipboard history.
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Config
HISTORY_FILE = Path.home() / ".cliphist" / "history.json"
MAX_HISTORY = 1000

def load_history():
    """Load clipboard history from file."""
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_history(history):
    """Save clipboard history to file."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def add_to_history(text):
    """Add new entry to history, avoiding duplicates."""
    if not text or not text.strip():
        return False
    
    text = text.strip()
    history = load_history()
    
    # Check for duplicate (most recent entry)
    if history and history[0].get('text') == text:
        return False
    
    entry = {
        'text': text,
        'timestamp': datetime.now().isoformat(),
        'preview': text[:80] + ('...' if len(text) > 80 else '')
    }
    
    history.insert(0, entry)
    
    # Trim to max history
    if len(history) > MAX_HISTORY:
        history = history[:MAX_HISTORY]
    
    save_history(history)
    return True

def list_history(limit=20, search=None):
    """List clipboard history."""
    history = load_history()
    
    if search:
        history = [h for h in history if search.lower() in h['text'].lower()]
    
    if not history:
        print("No clipboard history found.")
        return
    
    for i, entry in enumerate(history[:limit]):
        ts = datetime.fromisoformat(entry['timestamp']).strftime("%Y-%m-%d %H:%M")
        print(f"{i+1:3}. [{ts}] {entry['preview']}")

def get_entry(index):
    """Get a specific history entry by index."""
    history = load_history()
    try:
        idx = int(index) - 1
        if 0 <= idx < len(history):
            return history[idx]['text']
    except ValueError:
        pass
    return None

def copy_entry(index):
    """Copy a history entry back to clipboard."""
    text = get_entry(index)
    if text:
        try:
            import pyperclip
            pyperclip.copy(text)
            print(f"Copied entry #{index} to clipboard!")
            return True
        except ImportError:
            # Fallback: print to stdout for manual copy
            print(text)
            print("\n(pyperclip not installed - install with: pip install pyperclip)")
            return False
    print(f"Entry #{index} not found.")
    return False

def clear_history():
    """Clear all clipboard history."""
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()
    print("Clipboard history cleared.")

def main():
    parser = argparse.ArgumentParser(
        description='ClipHist - Clipboard History Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  cliphist add "some text"    Add text to history
  cliphist                    Show recent history
  cliphist list               Show recent history
  cliphist list --search foo  Search for 'foo' in history
  cliphist copy 3             Copy entry #3 back to clipboard
  cliphist clear              Clear all history
        '''
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add text to history')
    add_parser.add_argument('text', nargs='+', help='Text to add')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List history')
    list_parser.add_argument('-n', '--limit', type=int, default=20, help='Number of entries')
    list_parser.add_argument('-s', '--search', help='Search text')
    
    # Copy command
    copy_parser = subparsers.add_parser('copy', help='Copy entry to clipboard')
    copy_parser.add_argument('index', help='Entry index to copy')
    
    # Clear command
    subparsers.add_parser('clear', help='Clear all history')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        text = ' '.join(args.text)
        if add_to_history(text):
            print(f"Added to history: {text[:50]}...")
        else:
            print("Duplicate or empty - not added.")
    
    elif args.command == 'list':
        list_history(args.limit, args.search)
    
    elif args.command == 'copy':
        copy_entry(args.index)
    
    elif args.command == 'clear':
        clear_history()
    
    else:
        # Default: show history
        list_history()

if __name__ == '__main__':
    main()
