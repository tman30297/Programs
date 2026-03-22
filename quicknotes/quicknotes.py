#!/usr/bin/env python3
"""
Quick Notes - Fast note-taking with tagging and search
"""

import os
import sqlite3
import datetime
from pathlib import Path

DB_PATH = Path.home() / ".quicknotes.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notes
                 (id INTEGER PRIMARY KEY, title TEXT, content TEXT, 
                  tags TEXT, created TEXT, updated TEXT)''')
    conn.commit()
    return conn

def add_note(conn, title, content, tags=""):
    now = datetime.datetime.now().isoformat()
    c = conn.cursor()
    c.execute("INSERT INTO notes (title, content, tags, created, updated) VALUES (?, ?, ?, ?, ?)",
              (title, content, tags, now, now))
    conn.commit()
    return c.lastrowid

def update_note(conn, note_id, title=None, content=None, tags=None):
    now = datetime.datetime.now().isoformat()
    c = conn.cursor()
    if title:
        c.execute("UPDATE notes SET title = ?, updated = ? WHERE id = ?", (title, now, note_id))
    if content:
        c.execute("UPDATE notes SET content = ?, updated = ? WHERE id = ?", (content, now, note_id))
    if tags is not None:
        c.execute("UPDATE notes SET tags = ?, updated = ? WHERE id = ?", (tags, now, note_id))
    conn.commit()

def delete_note(conn, note_id):
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()

def get_notes(conn, tag=None, search=None):
    c = conn.cursor()
    if tag:
        c.execute("SELECT * FROM notes WHERE tags LIKE ? ORDER BY updated DESC", (f"%{tag}%",))
    elif search:
        c.execute("SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? ORDER BY updated DESC",
                  (f"%{search}%", f"%{search}%"))
    else:
        c.execute("SELECT * FROM notes ORDER BY updated DESC")
    return c.fetchall()

def get_note(conn, note_id):
    c = conn.cursor()
    c.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    return c.fetchone()

def list_tags(conn):
    c = conn.cursor()
    c.execute("SELECT tags FROM notes")
    all_tags = set()
    for row in c.fetchall():
        if row[3]:
            for tag in row[3].split(","):
                all_tags.add(tag.strip())
    return sorted(all_tags)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Quick Notes")
    parser.add_argument("--add", nargs="+", help="Add note (title followed by content)")
    parser.add_argument("--tags", type=str, help="Tags for note (comma-separated)")
    parser.add_argument("--list", action="store_true", help="List all notes")
    parser.add_argument("--search", type=str, help="Search notes")
    parser.add_argument("--tag", type=str, help="Filter by tag")
    parser.add_argument("--show", type=int, help="Show note by ID")
    parser.add_argument("--edit", type=int, help="Edit note by ID")
    parser.add_argument("--delete", type=int, help="Delete note by ID")
    parser.add_argument("--tags-list", action="store_true", help="List all tags")
    args = parser.parse_args()
    
    conn = init_db()
    
    if args.add:
        title = args.add[0]
        content = " ".join(args.add[1:])
        tags = args.tags or ""
        note_id = add_note(conn, title, content, tags)
        print(f"Note saved (ID: {note_id})")
    elif args.list:
        notes = get_notes(conn)
        for note in notes:
            print(f"[{note[0]}] {note[1]}")
            print(f"    Tags: {note[3] or 'none'}")
            print(f"    {note[4][:10]} - {note[2][:80]}...")
            print()
    elif args.search:
        notes = get_notes(conn, search=args.search)
        print(f"Results for '{args.search}':")
        for note in notes:
            print(f"[{note[0]}] {note[1]}: {note[2][:60]}...")
    elif args.tag:
        notes = get_notes(conn, tag=args.tag)
        print(f"Notes tagged '{args.tag}':")
        for note in notes:
            print(f"[{note[0]}] {note[1]}: {note[2][:60]}...")
    elif args.show:
        note = get_note(conn, args.show)
        if note:
            print(f"Title: {note[1]}")
            print(f"Tags: {note[3] or 'none'}")
            print(f"Created: {note[4]}")
            print(f"Updated: {note[5]}")
            print(f"\n{note[2]}")
        else:
            print("Note not found")
    elif args.delete:
        delete_note(conn, args.delete)
        print(f"Deleted note {args.delete}")
    elif args.tags_list:
        tags = list_tags(conn)
        print("All tags:", ", ".join(tags) if tags else "none")
    else:
        # Default: show recent
        notes = get_notes(conn)[:5]
        print("Recent notes:")
        for note in notes:
            print(f"[{note[0]}] {note[1]} - {note[2][:50]}...")

if __name__ == "__main__":
    main()
