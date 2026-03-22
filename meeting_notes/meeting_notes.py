#!/usr/bin/env python3
"""
Meeting Notes Manager - CLI tool for organizing meeting notes
Usage: meeting_notes.py [command] [options]
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

NOTES_DIR = Path.home() / ".meeting_notes"
CONFIG_FILE = NOTES_DIR / "config.json"

def ensure_dir():
    """Ensure the notes directory exists."""
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'w') as f:
            json.dump({"default_tag": "meeting"}, f)

def load_config():
    """Load configuration."""
    with open(CONFIG_FILE) as f:
        return json.load(f)

def save_note(title: str, content: str, tags: list = None):
    """Save a new meeting note."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{timestamp}_{title.replace(' ', '_')}.json"
    
    note = {
        "title": title,
        "content": content,
        "tags": tags or [],
        "created": datetime.now().isoformat(),
        "filename": filename
    }
    
    filepath = NOTES_DIR / filename
    with open(filepath, 'w') as f:
        json.dump(note, f, indent=2)
    
    print(f"✓ Note saved: {title}")
    return filepath

def list_notes(tag: str = None, search: str = None):
    """List all notes, optionally filtered by tag or search term."""
    notes = []
    for f in NOTES_DIR.glob("*.json"):
        if f.name == "config.json":
            continue
        try:
            with open(f) as nf:
                note = json.load(nf)
                notes.append(note)
        except:
            continue
    
    # Filter
    if tag:
        notes = [n for n in notes if tag in n.get("tags", [])]
    if search:
        search_lower = search.lower()
        notes = [n for n in notes if search_lower in n.get("title", "").lower() 
                 or search_lower in n.get("content", "").lower()]
    
    # Sort by date
    notes.sort(key=lambda x: x.get("created", ""), reverse=True)
    
    if not notes:
        print("No notes found.")
        return
    
    print(f"\n📋 Found {len(notes)} note(s):\n")
    for note in notes:
        date = note.get("created", "")[:10]
        tags = f" [{', '.join(note.get('tags', []))}]" if note.get("tags") else ""
        print(f"  {date} - {note.get('title', 'Untitled')}{tags}")
    print()

def view_note(title_or_file: str):
    """View a specific note."""
    # Try exact match first
    for f in NOTES_DIR.glob("*.json"):
        if f.name == "config.json":
            continue
        with open(f) as nf:
            note = json.load(nf)
            if title_or_file in note.get("title", "") or title_or_file in f.name:
                print(f"\n=== {note.get('title', 'Untitled')} ===")
                print(f"Date: {note.get('created', '')}")
                print(f"Tags: {', '.join(note.get('tags', [])) or 'none'}")
                print(f"\n{note.get('content', '')}\n")
                return
    
    print(f"Note not found: {title_or_file}")

def delete_note(title_or_file: str):
    """Delete a note."""
    for f in NOTES_DIR.glob("*.json"):
        if f.name == "config.json":
            continue
        with open(f) as nf:
            note = json.load(nf)
            if title_or_file in note.get("title", "") or title_or_file in f.name:
                f.unlink()
                print(f"✓ Deleted: {note.get('title', 'Untitled')}")
                return
    
    print(f"Note not found: {title_or_file}")

def export_notes(output_dir: str = None):
    """Export all notes to markdown files."""
    out_dir = Path(output_dir) if output_dir else NOTES_DIR / "export"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for f in NOTES_DIR.glob("*.json"):
        if f.name == "config.json":
            continue
        with open(f) as nf:
            note = json.load(nf)
            md_filename = f"{note.get('created', '')[:10]}_{note.get('title', 'note').replace(' ', '_')}.md"
            content = f"# {note.get('title', 'Meeting Note')}\n\n"
            content += f"**Date:** {note.get('created', '')}\n"
            content += f"**Tags:** {', '.join(note.get('tags', [])) or 'none'}\n\n"
            content += f"---\n\n{note.get('content', '')}\n"
            
            with open(out_dir / md_filename, 'w') as of:
                of.write(content)
            count += 1
    
    print(f"✓ Exported {count} notes to {out_dir}")

def main():
    ensure_dir()
    
    parser = argparse.ArgumentParser(description="Meeting Notes Manager")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Add note
    add_parser = subparsers.add_parser("add", help="Add a new note")
    add_parser.add_argument("title", help="Note title")
    add_parser.add_argument("-c", "--content", help="Note content (or use stdin)")
    add_parser.add_argument("-t", "--tag", action="append", help="Add tag (can repeat)")
    
    # List notes
    list_parser = subparsers.add_parser("list", help="List notes")
    list_parser.add_argument("-t", "--tag", help="Filter by tag")
    list_parser.add_argument("-s", "--search", help="Search in notes")
    
    # View note
    view_parser = subparsers.add_parser("view", help="View a note")
    view_parser.add_argument("title", help="Title or filename to view")
    
    # Delete note
    del_parser = subparsers.add_parser("delete", help="Delete a note")
    del_parser.add_argument("title", help="Title or filename to delete")
    
    # Export
    export_parser = subparsers.add_parser("export", help="Export to markdown")
    export_parser.add_argument("-o", "--output", help="Output directory")
    
    args = parser.parse_args()
    
    if args.command == "add":
        content = args.content
        if not content:
            print("Enter note content (Ctrl+D to finish):")
            content = sys.stdin.read()
        save_note(args.title, content, args.tag)
    
    elif args.command == "list":
        list_notes(args.tag, args.search)
    
    elif args.command == "view":
        view_note(args.title)
    
    elif args.command == "delete":
        delete_note(args.title)
    
    elif args.command == "export":
        export_notes(args.output)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()