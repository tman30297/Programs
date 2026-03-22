#!/usr/bin/env python3
"""
AI Prompt Library - Manage and quickly access prompts for Ollama/LLMs
Usage: promptlib.py [command] [args]
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Config location
CONFIG_DIR = Path.home() / ".promptlib"
PROMPTS_FILE = CONFIG_DIR / "prompts.json"

def ensure_config():
    """Ensure config directory and prompts file exist"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not PROMPTS_FILE.exists():
        PROMPTS_FILE.write_text(json.dumps({"prompts": [], "categories": ["general", "coding", "writing", "analysis"]}, indent=2))

def load_prompts():
    """Load prompts from file"""
    ensure_config()
    return json.loads(PROMPTS_FILE.read_text())

def save_prompts(data):
    """Save prompts to file"""
    PROMPTS_FILE.write_text(json.dumps(data, indent=2))

def list_prompts(category=None, search=None):
    """List all prompts, optionally filtered"""
    data = load_prompts()
    prompts = data.get("prompts", [])
    
    if category:
        prompts = [p for p in prompts if p.get("category") == category]
    if search:
        search_lower = search.lower()
        prompts = [p for p in prompts if search_lower in p.get("name", "").lower() or search_lower in p.get("content", "").lower()]
    
    if not prompts:
        print("No prompts found.")
        return
    
    for i, p in enumerate(prompts, 1):
        cat = p.get("category", "general")
        print(f"{i}. [{cat}] {p['name']}")
        print(f"   {p['content'][:80]}...")
        print()

def add_prompt(name, content, category="general"):
    """Add a new prompt"""
    data = load_prompts()
    
    # Check for duplicate names
    if any(p["name"] == name for p in data.get("prompts", [])):
        print(f"Error: Prompt '{name}' already exists.")
        return False
    
    prompt = {
        "name": name,
        "content": content,
        "category": category
    }
    
    data.setdefault("prompts", []).append(prompt)
    save_prompts(data)
    print(f"Added prompt: {name} [{category}]")
    return True

def delete_prompt(name):
    """Delete a prompt by name"""
    data = load_prompts()
    prompts = data.get("prompts", [])
    
    for i, p in enumerate(prompts):
        if p["name"] == name:
            prompts.pop(i)
            data["prompts"] = prompts
            save_prompts(data)
            print(f"Deleted prompt: {name}")
            return True
    
    print(f"Prompt '{name}' not found.")
    return False

def get_prompt(name):
    """Get a prompt's full content by name"""
    data = load_prompts()
    
    for p in data.get("prompts", []):
        if p["name"] == name:
            return p
    
    return None

def list_categories():
    """List all categories"""
    data = load_prompts()
    cats = data.get("categories", [])
    prompts = data.get("prompts", [])
    
    print("Categories:")
    for cat in cats:
        count = sum(1 for p in prompts if p.get("category") == cat)
        print(f"  - {cat} ({count} prompts)")
    
    # Show uncategorized
    uncategorized = sum(1 for p in prompts if p.get("category") not in cats)
    if uncategorized:
        print(f"  - uncategorized ({uncategorized} prompts)")

def add_category(category):
    """Add a new category"""
    data = load_prompts()
    cats = data.get("categories", [])
    
    if category in cats:
        print(f"Category '{category}' already exists.")
        return False
    
    cats.append(category)
    data["categories"] = cats
    save_prompts(data)
    print(f"Added category: {category}")
    return True

def export_prompt(name):
    """Print prompt in a copyable format"""
    p = get_prompt(name)
    if p:
        print(f"# Prompt: {p['name']}")
        print(f"# Category: {p.get('category', 'general')}")
        print("---")
        print(p["content"])
    else:
        print(f"Prompt '{name}' not found.")

def main():
    parser = argparse.ArgumentParser(description="AI Prompt Library Manager")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List prompts")
    list_parser.add_argument("-c", "--category", help="Filter by category")
    list_parser.add_argument("-s", "--search", help="Search in name/content")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new prompt")
    add_parser.add_argument("name", help="Prompt name")
    add_parser.add_argument("content", help="Prompt content (use quotes)")
    add_parser.add_argument("-c", "--category", default="general", help="Category")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get prompt content")
    get_parser.add_argument("name", help="Prompt name")
    
    # Delete command
    del_parser = subparsers.add_parser("delete", help="Delete a prompt")
    del_parser.add_argument("name", help="Prompt name")
    
    # Categories command
    subparsers.add_parser("categories", help="List categories")
    
    # Add category command
    cat_parser = subparsers.add_parser("add-category", help="Add a category")
    cat_parser.add_argument("category", help="Category name")
    
    # Export command
    exp_parser = subparsers.add_parser("export", help="Export prompt (copyable)")
    exp_parser.add_argument("name", help="Prompt name")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_prompts(args.category, args.search)
    elif args.command == "add":
        add_prompt(args.name, args.content, args.category)
    elif args.command == "get":
        p = get_prompt(args.name)
        if p:
            print(p["content"])
    elif args.command == "delete":
        delete_prompt(args.name)
    elif args.command == "categories":
        list_categories()
    elif args.command == "add-category":
        add_category(args.category)
    elif args.command == "export":
        export_prompt(args.name)
    else:
        parser.print_help()
        print("\nExamples:")
        print("  promptlib.py list                          # List all prompts")
        print("  promptlib.py list -c coding               # List coding prompts")
        print("  promptlib.py add 'my prompt' 'content'    # Add a prompt")
        print("  promptlib.py get my prompt                # Get prompt content")
        print("  promptlib.py export my prompt             # Export for copying")
        print("  promptlib.py categories                   # List categories")

if __name__ == "__main__":
    main()
