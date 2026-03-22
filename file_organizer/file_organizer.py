#!/usr/bin/env python3
"""
File Organizer - Automatically sort files into folders by type
Usage: python file_organizer.py [directory] [--dry-run] [--undo]
"""

import os
import shutil
import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Define file categories and their extensions
FILE_CATEGORIES = {
    "Images": ["jpg", "jpeg", "png", "gif", "bmp", "svg", "webp", "ico", "tiff", "raw", "psd", "ai"],
    "Videos": ["mp4", "mkv", "avi", "mov", "wmv", "flv", "webm", "m4v", "mpeg", "mpg"],
    "Audio": ["mp3", "wav", "flac", "aac", "ogg", "wma", "m4a", "opus", "aiff"],
    "Documents": ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "rtf", "odt", "ods", "odp", "csv", "md"],
    "Archives": ["zip", "rar", "7z", "tar", "gz", "bz2", "xz", "iso", "dmg"],
    "Code": ["py", "js", "html", "css", "java", "c", "cpp", "h", "cs", "go", "rs", "ts", "jsx", "tsx", "php", "rb", "swift", "kt", "sh", "bash", "sql", "json", "xml", "yaml", "yml", "toml"],
    "Executables": ["exe", "msi", "deb", "rpm", "app", "dmg", "bin", "sh"],
    "Design": ["sketch", "fig", "xd", "indd", "afdesign", "afphoto"],
}

# Reverse mapping: extension -> category
EXT_TO_CATEGORY = {}
for category, extensions in FILE_CATEGORIES.items():
    for ext in extensions:
        EXT_TO_CATEGORY[ext.lower()] = category

HISTORY_FILE = Path.home() / ".file_organizer_history.json"


def load_history():
    """Load the operation history for undo functionality."""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []


def save_history(history):
    """Save operation history."""
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def categorize_file(filename):
    """Determine the category for a file based on its extension."""
    ext = Path(filename).suffix.lstrip('.').lower()
    return EXT_TO_CATEGORY.get(ext, "Others")


def organize_directory(directory, dry_run=False, undo_last=False):
    """Organize files in the given directory by moving them into category folders."""
    directory = Path(directory).resolve()
    
    if not directory.exists():
        print(f"Error: Directory '{directory}' does not exist.")
        return False
    
    if not directory.is_dir():
        print(f"Error: '{directory}' is not a directory.")
        return False
    
    history = load_history()
    
    # Undo last operation
    if undo_last and history:
        last_op = history[-1]
        print(f"Undoing last organization in: {last_op['directory']}")
        
        for item in last_op['moves']:
            src = Path(item['moved_to'])
            dst = Path(item['original_location'])
            
            if src.exists():
                # Create parent directory if needed
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                print(f"  Restored: {src.name} -> {dst}")
        
        history.pop()
        save_history(history)
        print("Undo complete!")
        return True
    
    # Organize files
    moves = []
    files_by_category = defaultdict(list)
    
    # Get all files (not directories)
    for item in directory.iterdir():
        if item.is_file() and not item.name.startswith('.'):
            category = categorize_file(item.name)
            files_by_category[category].append(item)
    
    # Display what will happen
    print(f"\nOrganizing: {directory}")
    print("=" * 50)
    
    if not files_by_category:
        print("No files to organize.")
        return True
    
    for category, files in sorted(files_by_category.items()):
        print(f"\n{category}:")
        for f in files:
            print(f"  - {f.name}")
    
    if dry_run:
        print("\n[DRY RUN] No files were moved.")
        return True
    
    # Confirm before proceeding
    response = input("\nProceed with organization? [y/N]: ").strip().lower()
    if response != 'y':
        print("Cancelled.")
        return False
    
    # Move files
    print("\nMoving files...")
    for category, files in files_by_category.items():
        category_dir = directory / category
        category_dir.mkdir(exist_ok=True)
        
        for f in files:
            # Handle name collisions
            target = category_dir / f.name
            counter = 1
            while target.exists():
                stem = f.stem
                ext = f.suffix
                target = category_dir / f"{stem}_{counter}{ext}"
                counter += 1
            
            shutil.move(str(f), str(target))
            moves.append({
                "original_location": str(f),
                "moved_to": str(target),
                "category": category
            })
            print(f"  {f.name} -> {category}/")
    
    # Save to history
    history.append({
        "directory": str(directory),
        "timestamp": datetime.now().isoformat(),
        "moves": moves
    })
    save_history(history)
    
    print(f"\nDone! Organized {len(moves)} files.")
    return True


def show_stats(directory=None):
    """Show statistics about file organization."""
    history = load_history()
    
    if not history:
        print("No organization history found.")
        return
    
    if directory:
        ops = [h for h in history if h['directory'] == str(Path(directory).resolve())]
    else:
        ops = history
    
    print(f"\nOrganization History ({len(ops)} operations)")
    print("=" * 50)
    
    for i, op in enumerate(ops[-10:], 1):  # Show last 10
        print(f"\n{i}. {op['timestamp'][:19]}")
        print(f"   Directory: {op['directory']}")
        
        # Group by category
        by_cat = defaultdict(int)
        for m in op['moves']:
            by_cat[m['category']] += 1
        
        for cat, count in sorted(by_cat.items()):
            print(f"   {cat}: {count} files")


def main():
    parser = argparse.ArgumentParser(description="Organize files into folders by type")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to organize (default: current)")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without moving files")
    parser.add_argument("--undo", action="store_true", help="Undo the last organization")
    parser.add_argument("--stats", action="store_true", help="Show organization history")
    parser.add_argument("--config", action="store_true", help="Show current configuration")
    
    args = parser.parse_args()
    
    if args.stats:
        show_stats(args.directory if args.directory != "." else None)
    elif args.config:
        print("File Categories:")
        for cat, exts in FILE_CATEGORIES.items():
            print(f"  {cat}: {', '.join(exts)}")
    else:
        organize_directory(args.directory, args.dry_run, args.undo)


if __name__ == "__main__":
    main()
