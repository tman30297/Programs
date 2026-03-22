#!/usr/bin/env python3
"""
Clipboard Manager - Store, search, and manage clipboard history
"""

import pyperclip
import sqlite3
import time
import os
from datetime import datetime
from pathlib import Path

DB_PATH = Path.home() / ".clipboard_manager.db"

def init_db():
    """Initialize the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clips
                 (id INTEGER PRIMARY KEY, content TEXT, timestamp TEXT, favorite INTEGER DEFAULT 0)''')
    conn.commit()
    return conn

def add_clip(conn, content):
    """Add a new clip to the database."""
    # Check if content already exists
    c = conn.cursor()
    c.execute("SELECT id FROM clips WHERE content = ?", (content,))
    if c.fetchone():
        # Update timestamp instead
        c.execute("UPDATE clips SET timestamp = ? WHERE content = ?", (datetime.now().isoformat(), content))
    else:
        c.execute("INSERT INTO clips (content, timestamp) VALUES (?, ?)", 
                  (content, datetime.now().isoformat()))
    conn.commit()

def get_clips(conn, limit=50, favorites_only=False):
    """Get recent clips."""
    c = conn.cursor()
    if favorites_only:
        c.execute("SELECT id, content, timestamp FROM clips WHERE favorite = 1 ORDER BY timestamp DESC LIMIT ?", (limit,))
    else:
        c.execute("SELECT id, content, timestamp FROM clips ORDER BY timestamp DESC LIMIT ?", (limit,))
    return c.fetchall()

def toggle_favorite(conn, clip_id):
    """Toggle favorite status."""
    c = conn.cursor()
    c.execute("UPDATE clips SET favorite = NOT favorite WHERE id = ?", (clip_id,))
    conn.commit()

def delete_clip(conn, clip_id):
    """Delete a clip."""
    c = conn.cursor()
    c.execute("DELETE FROM clips WHERE id = ?", (clip_id,))
    conn.commit()

def search_clips(conn, query):
    """Search clips."""
    c = conn.cursor()
    c.execute("SELECT id, content, timestamp FROM clips WHERE content LIKE ? ORDER BY timestamp DESC", 
              (f"%{query}%",))
    return c.fetchall()

def copy_to_clipboard(content):
    """Copy content to clipboard."""
    pyperclip.copy(content)

def monitor_clipboard(conn, interval=1.0):
    """Monitor clipboard and save new content."""
    last_content = ""
    print("Monitoring clipboard... Press Ctrl+C to stop.")
    try:
        while True:
            try:
                current = pyperclip.paste()
                if current and current != last_content and len(current.strip()) > 0:
                    add_clip(conn, current)
                    last_content = current
                    print(f"✓ Saved: {current[:50]}...")
            except Exception as e:
                pass
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped monitoring.")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Clipboard Manager")
    parser.add_argument("--watch", action="store_true", help="Monitor clipboard continuously")
    parser.add_argument("--list", action="store_true", help="List recent clips")
    parser.add_argument("--search", type=str, help="Search clips")
    parser.add_argument("--favorites", action="store_true", help="Show favorites only")
    parser.add_argument("--copy", type=int, help="Copy clip ID to clipboard")
    parser.add_argument("--favorite", type=int, help="Toggle favorite on clip ID")
    parser.add_argument("--delete", type=int, help="Delete clip ID")
    parser.add_argument("--clear", action="store_true", help="Clear all clips")
    args = parser.parse_args()
    
    conn = init_db()
    
    if args.watch:
        monitor_clipboard(conn)
    elif args.clear:
        c = conn.cursor()
        c.execute("DELETE FROM clips")
        conn.commit()
        print("All clips cleared.")
    elif args.list:
        clips = get_clips(conn, favorites_only=args.favorites)
        for idx, content, ts in clips:
            fav = "★" if args.favorites else ""
            print(f"[{idx}] {ts[:19]} {fav}")
            print(f"    {content[:100]}...")
            print()
    elif args.search:
        clips = search_clips(conn, args.search)
        for idx, content, ts in clips:
            print(f"[{idx}] {ts[:19]}")
            print(f"    {content[:100]}...")
            print()
    elif args.copy:
        clips = get_clips(conn, limit=1000)
        for idx, content, ts in clips:
            if idx == args.copy:
                copy_to_clipboard(content)
                print(f"Copied clip {idx} to clipboard")
                break
    elif args.favorite:
        toggle_favorite(conn, args.favorite)
        print(f"Toggled favorite on clip {args.favorite}")
    elif args.delete:
        delete_clip(conn, args.delete)
        print(f"Deleted clip {args.delete}")
    else:
        # Show recent by default
        clips = get_clips(conn, limit=10)
        print("Recent clips:")
        for idx, content, ts in clips:
            print(f"[{idx}] {ts[:19]}: {content[:60]}...")

if __name__ == "__main__":
    main()
