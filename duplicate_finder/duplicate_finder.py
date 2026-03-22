#!/usr/bin/env python3
"""
File Duplicate Finder
Finds duplicate files in a directory by comparing content hashes.
"""

import os
import sys
import hashlib
import argparse
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


def get_file_hash(filepath: str, chunk_size: int = 8192) -> str:
    """Calculate MD5 hash of a file."""
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (IOError, OSError) as e:
        return None


def scan_directory(path: str, extensions: List[str] = None) -> Dict[str, List[str]]:
    """
    Scan directory and return dict of hash -> list of files.
    """
    hash_map = defaultdict(list)
    files_scanned = 0
    
    path_obj = Path(path)
    if not path_obj.exists():
        print(f"Error: Path '{path}' does not exist")
        sys.exit(1)
    
    print(f"Scanning {path}...")
    
    for root, _, files in os.walk(path):
        for filename in files:
            filepath = os.path.join(root, filename)
            
            # Skip if not a regular file
            if not os.path.isfile(filepath):
                continue
            
            # Filter by extension if specified
            if extensions:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in extensions:
                    continue
            
            # Skip very small files (< 10 bytes likely not worth comparing)
            try:
                if os.path.getsize(filepath) < 10:
                    continue
            except OSError:
                continue
            
            file_hash = get_file_hash(filepath)
            if file_hash:
                hash_map[file_hash].append(filepath)
                files_scanned += 1
                
                if files_scanned % 100 == 0:
                    print(f"  Scanned {files_scanned} files...", end='\r')
    
    print(f"  Scanned {files_scanned} files complete")
    return hash_map


def find_duplicates(hash_map: Dict[str, List[str]]) -> List[Tuple[str, List[str]]]:
    """Return list of (hash, [files]) where len(files) > 1"""
    return [(h, files) for h, files in hash_map.items() if len(files) > 1]


def format_size(size_bytes: int) -> str:
    """Format bytes to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def print_duplicates(duplicates: List[Tuple[str, List[str]]], path: str):
    """Print found duplicates in a nice format."""
    if not duplicates:
        print("\n✅ No duplicates found!")
        return
    
    total_waste = 0
    print(f"\n{'='*60}")
    print(f"Found {len(duplicates)} sets of duplicates:")
    print(f"{'='*60}")
    
    for i, (file_hash, files) in enumerate(duplicates, 1):
        # Get file size from first file
        try:
            file_size = os.path.getsize(files[0])
        except OSError:
            continue
        
        waste = file_size * (len(files) - 1)
        total_waste += waste
        
        print(f"\n📁 Duplicate Set #{i} ({len(files)} files, {format_size(waste)} wasted)")
        print(f"   Size: {format_size(file_size)} each")
        
        for j, filepath in enumerate(files, 1):
            # Show relative path
            try:
                rel_path = os.path.relpath(filepath, path)
            except ValueError:
                rel_path = filepath
            
            marker = "✓ KEEP" if j == 1 else "  DELETE"
            print(f"   [{j}] {marker}: {rel_path}")
    
    print(f"\n{'='*60}")
    print(f"💾 Total space wasteable: {format_size(total_waste)}")
    print(f"{'='*60}")


def delete_duplicates(duplicates: List[Tuple[str, List[str]]], path: str, keep_newest: bool = True):
    """Delete all but one file from each duplicate set."""
    deleted = 0
    freed = 0
    
    for file_hash, files in duplicates:
        # Sort by modification time
        try:
            files_with_mtime = [(f, os.path.getmtime(f)) for f in files]
            files_with_mtime.sort(key=lambda x: x[1], reverse=keep_newest)  # Newest first if keep_newest
            sorted_files = [f for f, _ in files_with_mtime]
        except OSError:
            sorted_files = files
        
        # Keep first, delete rest
        to_keep = sorted_files[0]
        to_delete = sorted_files[1:]
        
        for filepath in to_delete:
            try:
                size = os.path.getsize(filepath)
                os.remove(filepath)
                deleted += 1
                freed += size
                print(f"🗑️  Deleted: {filepath}")
            except OSError as e:
                print(f"❌ Failed to delete {filepath}: {e}")
    
    print(f"\n✅ Deleted {deleted} files, freed {format_size(freed)}")


def main():
    parser = argparse.ArgumentParser(
        description="Find and remove duplicate files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /home/user/downloads              # Scan downloads folder
  %(prog)s /home/user/documents -e .pdf .docx  # Only scan documents
  %(prog)s /home/user/photos --delete        # Delete duplicates (keeps newest)
  %(prog)s /home/user/photos --delete --oldest # Delete duplicates (keeps oldest)
        """
    )
    parser.add_argument('path', nargs='?', default='.', help='Directory to scan (default: current)')
    parser.add_argument('-e', '--extensions', nargs='+', help='File extensions to include (e.g., .pdf .jpg)')
    parser.add_argument('-d', '--delete', action='store_true', help='Delete duplicates (keeps one)')
    parser.add_argument('-o', '--oldest', action='store_true', help='When deleting, keep oldest instead of newest')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode (no progress output)')
    
    args = parser.parse_args()
    
    # Scan
    hash_map = scan_directory(args.path, args.extensions)
    
    # Find duplicates
    duplicates = find_duplicates(hash_map)
    
    # Print results
    print_duplicates(duplicates, args.path)
    
    # Delete if requested
    if args.delete and duplicates:
        confirm = input("\n⚠️  Delete duplicate files? (y/n): ").strip().lower()
        if confirm == 'y':
            delete_duplicates(duplicates, args.path, keep_newest=not args.oldest)
        else:
            print("Cancelled.")


if __name__ == '__main__':
    main()
