#!/usr/bin/env python3
"""
QuickSnip - CLI Snippet Manager
Store, search, and retrieve code snippets and commands from the terminal.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

SNIPPET_DIR = Path.home() / ".quicksnip"
SNIPPET_FILE = SNIPPET_DIR / "snippets.json"


def load_snippets():
    """Load snippets from storage."""
    SNIPPET_DIR.mkdir(parents=True, exist_ok=True)
    if SNIPPET_FILE.exists():
        with open(SNIPPET_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_snippets(snippets):
    """Save snippets to storage."""
    with open(SNIPPET_FILE, 'w') as f:
        json.dump(snippets, f, indent=2)


def add_snippet(name, content, tags, language):
    """Add a new snippet."""
    snippets = load_snippets()
    snippet_id = len(snippets) + 1
    
    snippets[str(snippet_id)] = {
        "name": name,
        "content": content,
        "tags": tags,
        "language": language,
        "created": datetime.now().isoformat(),
        "use_count": 0
    }
    
    save_snippets(snippets)
    print(f"✓ Added snippet '{name}' (ID: {snippet_id})")
    return snippet_id


def list_snippets(tag_filter=None, language_filter=None):
    """List all snippets with optional filters."""
    snippets = load_snippets()
    
    if not snippets:
        print("No snippets found. Add some with: quicksnip add")
        return
    
    print("\n📋 Your Snippets:")
    print("-" * 60)
    
    for sid, data in snippets.items():
        # Apply filters
        if tag_filter and tag_filter not in data.get('tags', []):
            continue
        if language_filter and data.get('language') != language_filter:
            continue
        
        tags = f"[{', '.join(data.get('tags', []))}]" if data.get('tags') else ""
        lang = data.get('language', 'text')
        count = data.get('use_count', 0)
        
        print(f"  [{sid}] {data['name']} {tags}")
        print(f"       📝 {lang} | used {count}x")
    print("-" * 60)


def get_snippet(snippet_id):
    """Get and display a snippet."""
    snippets = load_snippets()
    
    if snippet_id not in snippets:
        print(f"Error: Snippet '{snippet_id}' not found")
        return None
    
    data = snippets[snippet_id]
    
    # Increment use count
    data['use_count'] = data.get('use_count', 0) + 1
    snippets[snippet_id] = data
    save_snippets(snippets)
    
    return data


def show_snippet(snippet_id):
    """Show snippet content."""
    data = get_snippet(snippet_id)
    if not data:
        return
    
    print(f"\n📄 {data['name']} ({data.get('language', 'text')})")
    print("=" * 60)
    print(data['content'])
    print("=" * 60)
    
    if data.get('tags'):
        print(f"Tags: {', '.join(data['tags'])}")


def copy_snippet(snippet_id):
    """Copy snippet to clipboard."""
    data = get_snippet(snippet_id)
    if not data:
        return
    
    try:
        import pyperclip
        pyperclip.copy(data['content'])
        print(f"✓ Copied '{data['name']}' to clipboard!")
    except ImportError:
        print("Error: pyperclip not installed. Install with: pip install pyperclip")
    except Exception as e:
        print(f"Error copying to clipboard: {e}")


def delete_snippet(snippet_id):
    """Delete a snippet."""
    snippets = load_snippets()
    
    if snippet_id not in snippets:
        print(f"Error: Snippet '{snippet_id}' not found")
        return
    
    name = snippets[snippet_id]['name']
    del snippets[snippet_id]
    save_snippets(snippets)
    print(f"✓ Deleted snippet '{name}'")


def search_snippets(query):
    """Search snippets by name, tags, or content."""
    snippets = load_snippets()
    query = query.lower()
    
    results = []
    for sid, data in snippets.items():
        search_text = f"{data['name']} {data['content']} {' '.join(data.get('tags', []))}".lower()
        if query in search_text:
            results.append((sid, data))
    
    if not results:
        print(f"No results found for '{query}'")
        return
    
    print(f"\n🔍 Results for '{query}':")
    print("-" * 60)
    for sid, data in results[:10]:
        tags = f"[{', '.join(data.get('tags', []))}]" if data.get('tags') else ""
        preview = data['content'][:60].replace('\n', ' ') + "..." if len(data['content']) > 60 else data['content']
        print(f"  [{sid}] {data['name']} {tags}")
        print(f"       {preview}")
    print("-" * 60)


def edit_snippet(snippet_id, new_content=None, new_name=None, new_tags=None):
    """Edit a snippet."""
    snippets = load_snippets()
    
    if snippet_id not in snippets:
        print(f"Error: Snippet '{snippet_id}' not found")
        return
    
    if new_content:
        snippets[snippet_id]['content'] = new_content
    if new_name:
        snippets[snippet_id]['name'] = new_name
    if new_tags is not None:
        snippets[snippet_id]['tags'] = new_tags
    
    snippets[snippet_id]['updated'] = datetime.now().isoformat()
    save_snippets(snippets)
    print(f"✓ Updated snippet [{snippet_id}]")


def main():
    parser = argparse.ArgumentParser(
        description="QuickSnip - CLI Snippet Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  quicksnip add "git undo" "git reset --soft HEAD~1" -t git -l bash
  quicksnip list
  quicksnip show 1
  quicksnip copy 1
  quicksnip search docker
  quicksnip delete 1
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new snippet')
    add_parser.add_argument('name', help='Snippet name')
    add_parser.add_argument('content', help='Snippet content')
    add_parser.add_argument('-t', '--tags', nargs='*', default=[], help='Tags')
    add_parser.add_argument('-l', '--language', default='text', help='Language')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all snippets')
    list_parser.add_argument('-t', '--tag', help='Filter by tag')
    list_parser.add_argument('-l', '--language', help='Filter by language')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show snippet content')
    show_parser.add_argument('id', help='Snippet ID')
    
    # Copy command
    copy_parser = subparsers.add_parser('copy', help='Copy snippet to clipboard')
    copy_parser.add_argument('id', help='Snippet ID')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a snippet')
    delete_parser.add_argument('id', help='Snippet ID')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search snippets')
    search_parser.add_argument('query', help='Search query')
    
    # Edit command
    edit_parser = subparsers.add_parser('edit', help='Edit a snippet')
    edit_parser.add_argument('id', help='Snippet ID')
    edit_parser.add_argument('--content', help='New content')
    edit_parser.add_argument('--name', help='New name')
    edit_parser.add_argument('--tags', nargs='*', help='New tags')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'add':
        add_snippet(args.name, args.content, args.tags, args.language)
    elif args.command == 'list':
        list_snippets(args.tag, args.language)
    elif args.command == 'show':
        show_snippet(args.id)
    elif args.command == 'copy':
        copy_snippet(args.id)
    elif args.command == 'delete':
        delete_snippet(args.id)
    elif args.command == 'search':
        search_snippets(args.query)
    elif args.command == 'edit':
        edit_snippet(args.id, args.content, args.name, args.tags)


if __name__ == '__main__':
    main()
