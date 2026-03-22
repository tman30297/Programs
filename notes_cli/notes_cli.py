#!/usr/bin/env python3
"""
Notes CLI - A simple command-line notes manager with tags and search.
Usage: notes.py <command> [args]
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

NOTES_DIR = Path.home() / ".notes_data"
NOTES_FILE = NOTES_DIR / "notes.json"

def init_notes():
    """Initialize notes storage directory and file."""
    NOTES_DIR.mkdir(exist_ok=True)
    if not NOTES_FILE.exists():
        NOTES_FILE.write_text(json.dumps([], indent=2))

def load_notes():
    """Load all notes from storage."""
    init_notes()
    try:
        return json.loads(NOTES_FILE.read_text())
    except json.JSONDecodeError:
        return []

def save_notes(notes):
    """Save all notes to storage."""
    NOTES_FILE.write_text(json.dumps(notes, indent=2))

def create_note(title, content, tags=None):
    """Create a new note."""
    notes = load_notes()
    note = {
        "id": len(notes) + 1,
        "title": title,
        "content": content,
        "tags": [t.strip() for t in (tags or "").split(",") if t.strip()],
        "created": datetime.now().isoformat(),
        "modified": datetime.now().isoformat()
    }
    notes.append(note)
    save_notes(notes)
    print(f"✓ Created note #{note['id']}: {title}")
    return note

def list_notes(tag=None, search=None):
    """List all notes, optionally filtered by tag or search term."""
    notes = load_notes()
    
    if tag:
        notes = [n for n in notes if tag in n.get("tags", [])]
    
    if search:
        search = search.lower()
        notes = [n for n in notes if search in n["title"].lower() or search in n["content"].lower()]
    
    if not notes:
        print("No notes found.")
        return
    
    for note in notes:
        tags_str = f" [{', '.join(note['tags'])}]" if note.get("tags") else ""
        print(f"\n#{note['id']} | {note['title']}{tags_str}")
        print(f"   {note['content'][:100]}{'...' if len(note['content']) > 100 else ''}")
        print(f"   Created: {note['created'][:10]}")

def view_note(note_id):
    """View a specific note."""
    notes = load_notes()
    note = next((n for n in notes if n["id"] == note_id), None)
    
    if not note:
        print(f"Note #{note_id} not found.")
        return
    
    tags_str = f"Tags: {', '.join(note['tags'])}" if note.get("tags") else "Tags: (none)"
    print(f"\n{'='*50}")
    print(f"Title: {note['title']}")
    print(f"{tags_str}")
    print(f"Created:  {note['created']}")
    print(f"Modified: {note['modified']}")
    print(f"{'='*50}")
    print(note["content"])

def edit_note(note_id, title=None, content=None, tags=None):
    """Edit an existing note."""
    notes = load_notes()
    note = next((n for n in notes if n["id"] == note_id), None)
    
    if not note:
        print(f"Note #{note_id} not found.")
        return
    
    if title:
        note["title"] = title
    if content:
        note["content"] = content
    if tags is not None:
        note["tags"] = [t.strip() for t in tags.split(",") if t.strip()]
    
    note["modified"] = datetime.now().isoformat()
    save_notes(notes)
    print(f"✓ Updated note #{note_id}")

def delete_note(note_id):
    """Delete a note."""
    notes = load_notes()
    notes = [n for n in notes if n["id"] != note_id]
    save_notes(notes)
    print(f"✓ Deleted note #{note_id}")

def main():
    parser = argparse.ArgumentParser(description="Notes CLI - Manage your notes")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Create note
    add_parser = subparsers.add_parser("add", help="Add a new note")
    add_parser.add_argument("title", help="Note title")
    add_parser.add_argument("content", help="Note content")
    add_parser.add_argument("-t", "--tags", help="Comma-separated tags", default="")
    
    # List notes
    list_parser = subparsers.add_parser("list", help="List all notes")
    list_parser.add_argument("-t", "--tag", help="Filter by tag")
    list_parser.add_argument("-s", "--search", help="Search in title/content")
    
    # View note
    view_parser = subparsers.add_parser("view", help="View a note")
    view_parser.add_argument("id", type=int, help="Note ID")
    
    # Edit note
    edit_parser = subparsers.add_parser("edit", help="Edit a note")
    edit_parser.add_argument("id", type=int, help="Note ID")
    edit_parser.add_argument("--title", help="New title")
    edit_parser.add_argument("--content", help="New content")
    edit_parser.add_argument("--tags", help="New tags (comma-separated)")
    
    # Delete note
    delete_parser = subparsers.add_parser("delete", help="Delete a note")
    delete_parser.add_argument("id", type=int, help="Note ID")
    
    args = parser.parse_args()
    
    if args.command == "add":
        create_note(args.title, args.content, args.tags)
    elif args.command == "list":
        list_notes(args.tag, args.search)
    elif args.command == "view":
        view_note(args.id)
    elif args.command == "edit":
        edit_note(args.id, args.title, args.content, args.tags)
    elif args.command == "delete":
        delete_note(args.id)

if __name__ == "__main__":
    main()
