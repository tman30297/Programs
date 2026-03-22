#!/usr/bin/env python3
"""
LinkVault - CLI Bookmark Manager with Tags
Store, organize, search, and retrieve bookmarks from the terminal.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

DATA_FILE = Path.home() / ".linkvault.json"

def load_bookmarks():
    """Load bookmarks from JSON file."""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"bookmarks": [], "tags": {}}

def save_bookmarks(data):
    """Save bookmarks to JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_bookmark(url, title, tags):
    """Add a new bookmark."""
    data = load_bookmarks()
    
    # Check for duplicate URL
    for bm in data["bookmarks"]:
        if bm["url"] == url:
            print(f"⚠️  Bookmark already exists: {bm['title']}")
            return False
    
    bookmark = {
        "id": len(data["bookmarks"]) + 1,
        "url": url,
        "title": title,
        "tags": [t.lower().strip() for t in tags],
        "created": datetime.now().isoformat(),
        "last_accessed": None
    }
    
    data["bookmarks"].append(bookmark)
    
    # Update tag index
    for tag in bookmark["tags"]:
        if tag not in data["tags"]:
            data["tags"][tag] = []
        data["tags"][tag].append(bookmark["id"])
    
    save_bookmarks(data)
    print(f"✅ Added: {title}")
    print(f"   Tags: {', '.join(bookmark['tags'])}")
    return True

def list_bookmarks(tag_filter=None, search=None):
    """List all bookmarks, optionally filtered by tag or search term."""
    data = load_bookmarks()
    bookmarks = data["bookmarks"]
    
    if tag_filter:
        tag = tag_filter.lower()
        if tag in data["tags"]:
            bookmark_ids = data["tags"][tag]
            bookmarks = [bm for bm in bookmarks if bm["id"] in bookmark_ids]
            print(f"📂 Filtered by tag: {tag}")
        else:
            print(f"No bookmarks found with tag: {tag}")
            return
    
    if search:
        search = search.lower()
        bookmarks = [bm for bm in bookmarks 
                     if search in bm["title"].lower() 
                     or search in bm["url"].lower()
                     or search in " ".join(bm["tags"])]
        print(f"🔍 Search: {search}")
    
    if not bookmarks:
        print("No bookmarks found.")
        return
    
    print(f"\n📚 Your Bookmarks ({len(bookmarks)}):\n")
    for bm in bookmarks:
        tags_str = " ".join(f"[{t}]" for t in bm["tags"])
        print(f"  {bm['id']:3d}. {bm['title']}")
        print(f"      {bm['url']}")
        if tags_str:
            print(f"      {tags_str}")
        print()

def open_bookmark(bm_id):
    """Open a bookmark in the browser."""
    data = load_bookmarks()
    for bm in data["bookmarks"]:
        if bm["id"] == bm_id:
            bm["last_accessed"] = datetime.now().isoformat()
            save_bookmarks(data)
            
            # Try to open in browser
            import subprocess
            try:
                subprocess.run(["xdg-open", bm["url"]], check=True)
                print(f"🌐 Opened: {bm['title']}")
            except:
                print(f"❌ Could not open browser. URL: {bm['url']}")
            return
    
    print(f"❌ Bookmark #{bm_id} not found")

def delete_bookmark(bm_id):
    """Delete a bookmark."""
    data = load_bookmarks()
    for i, bm in enumerate(data["bookmarks"]):
        if bm["id"] == bm_id:
            # Remove from tag index
            for tag in bm["tags"]:
                if tag in data["tags"]:
                    data["tags"][tag] = [id for id in data["tags"][tag] if id != bm_id]
                    if not data["tags"][tag]:
                        del data["tags"][tag]
            
            deleted = data["bookmarks"].pop(i)
            save_bookmarks(data)
            print(f"🗑️  Deleted: {deleted['title']}")
            return
    
    print(f"❌ Bookmark #{bm_id} not found")

def list_tags():
    """List all tags and their counts."""
    data = load_bookmarks()
    if not data["tags"]:
        print("No tags yet. Add bookmarks with tags!")
        return
    
    print("\n🏷️  Tags:\n")
    for tag, ids in sorted(data["tags"].items(), key=lambda x: -len(x[1])):
        print(f"  {tag:20s} ({len(ids)} bookmarks)")

def export_bookmarks(filename):
    """Export bookmarks to a file."""
    data = load_bookmarks()
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Exported to: {filename}")

def import_bookmarks(filename):
    """Import bookmarks from a file."""
    with open(filename, 'r') as f:
        imported = json.load(f)
    
    data = load_bookmarks()
    
    # Merge, avoiding duplicates
    for bm in imported.get("bookmarks", []):
        if not any(b["url"] == bm["url"] for b in data["bookmarks"]):
            bm["id"] = len(data["bookmarks"]) + 1
            data["bookmarks"].append(bm)
            for tag in bm.get("tags", []):
                if tag not in data["tags"]:
                    data["tags"][tag] = []
                data["tags"][tag].append(bm["id"])
    
    save_bookmarks(data)
    print(f"✅ Imported bookmarks from: {filename}")

def main():
    parser = argparse.ArgumentParser(
        prog="linkvault",
        description="🔗 CLI Bookmark Manager with Tags"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new bookmark")
    add_parser.add_argument("url", help="URL of the bookmark")
    add_parser.add_argument("title", help="Title of the bookmark")
    add_parser.add_argument("-t", "--tags", nargs="*", help="Tags for the bookmark")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all bookmarks")
    list_parser.add_argument("-t", "--tag", help="Filter by tag")
    list_parser.add_argument("-s", "--search", help="Search in titles/urls/tags")
    
    # Open command
    open_parser = subparsers.add_parser("open", help="Open a bookmark in browser")
    open_parser.add_argument("id", type=int, help="Bookmark ID to open")
    
    # Delete command
    del_parser = subparsers.add_parser("delete", help="Delete a bookmark")
    del_parser.add_argument("id", type=int, help="Bookmark ID to delete")
    
    # Tags command
    subparsers.add_parser("tags", help="List all tags")
    
    # Export command
    exp_parser = subparsers.add_parser("export", help="Export bookmarks to file")
    exp_parser.add_argument("filename", help="Export filename")
    
    # Import command
    imp_parser = subparsers.add_parser("import", help="Import bookmarks from file")
    imp_parser.add_argument("filename", help="Import filename")
    
    args = parser.parse_args()
    
    if args.command == "add":
        tags = args.tags or []
        add_bookmark(args.url, args.title, tags)
    elif args.command == "list":
        list_bookmarks(tag_filter=args.tag, search=args.search)
    elif args.command == "open":
        open_bookmark(args.id)
    elif args.command == "delete":
        delete_bookmark(args.id)
    elif args.command == "tags":
        list_tags()
    elif args.command == "export":
        export_bookmarks(args.filename)
    elif args.command == "import":
        import_bookmarks(args.filename)
    else:
        parser.print_help()
        print("\n📌 Quick examples:")
        print("   linkvault add https://github.com GitHub -t code dev")
        print("   linkvault list -t code")
        print("   linkvault list -s python")
        print("   linkvault open 1")
        print("   linkvault tags")

if __name__ == "__main__":
    main()
