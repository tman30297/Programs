#!/usr/bin/env python3
"""
Bookmarks Manager - Organize, deduplicate, and export browser bookmarks
Supports: Chrome, Firefox, Edge, Brave
"""

import argparse
import json
import os
import re
import sqlite3
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from urllib.parse import urlparse, unquote

BROWSER_PATHS = {
    "chrome": [
        "~/.config/google-chrome/Default/Bookmarks",
        "~/.config/chromium/Default/Bookmarks",
        "~/Library/Application Support/Google/Chrome/Default/Bookmarks",
        "%APPDATA%/Google/Chrome/Default/Bookmarks",
    ],
    "firefox": [
        "~/.mozilla/firefox",
        "~/Library/Application Support/Firefox/Profiles",
        "%APPDATA%/Mozilla/Firefox/Profiles",
    ],
    "edge": [
        "~/Library/Application Support/Microsoft Edge/Default/Bookmarks",
        "%APPDATA%/Microsoft/Edge/Default/Bookmarks",
    ],
    "brave": [
        "~/.config/BraveSoftware/Brave-Browser/Default/Bookmarks",
        "%APPDATA%/BraveSoftware/Brave-Browser/Default/Bookmarks",
    ],
}


def find_browser_bookmarks(browser: str = None):
    """Find bookmark files for specified browser or all browsers."""
    found = {}
    
    browsers = [browser] if browser else BROWSER_PATHS.keys()
    
    for b in browsers:
        for pattern in BROWSER_PATHS.get(b, []):
            path = os.path.expanduser(os.path.expandvars(pattern))
            if os.path.exists(path):
                if os.path.isfile(path):
                    found[b] = path
                elif os.path.isdir(path):
                    # Firefox uses profile directories
                    for item in os.listdir(path):
                        if "profile" in item.lower() or item.endswith(".default"):
                            bookmark_file = os.path.join(path, item, "places.sqlite")
                            if os.path.exists(bookmark_file):
                                found[b] = bookmark_file
                                break
    return found


def parse_chrome_bookmarks(path: str) -> list:
    """Parse Chrome/Edge/Brave JSON bookmark file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    bookmarks = []
    
    def extract_folder(folder, path=""):
        folder_name = folder.get("name", "Root")
        current_path = f"{path}/{folder_name}" if path else "Root"
        
        for item in folder.get("children", []):
            if item.get("type") == "url":
                bookmarks.append({
                    "title": item.get("name", ""),
                    "url": item.get("url", ""),
                    "folder": current_path,
                    "browser": "unknown"
                })
            elif item.get("type") == "folder":
                extract_folder(item, current_path)
    
    for root in data.get("roots", {}).values():
        if isinstance(root, dict):
            extract_folder(root)
    
    return bookmarks


def parse_firefox_sqlite(path: str) -> list:
    """Parse Firefox places.sqlite."""
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT b.title, p.url, b.parent 
        FROM moz_bookmarks b 
        JOIN moz_places p ON b.fk = p.id 
        WHERE p.url IS NOT NULL
    """)
    
    # Get folder names
    cursor.execute("SELECT id, title FROM moz_bookmarks WHERE parent = 2")
    folder_map = dict(cursor.fetchall())
    
    bookmarks = []
    for title, url, parent in cursor.fetchall():
        folder = folder_map.get(parent, "Root")
        bookmarks.append({
            "title": title or "",
            "url": url,
            "folder": folder,
            "browser": "firefox"
        })
    
    conn.close()
    return bookmarks


def load_bookmarks(path: str, browser: str = None) -> list:
    """Load bookmarks from a file."""
    if not os.path.exists(path):
        print(f"Bookmarks file not found: {path}")
        return []
    
    ext = os.path.splitext(path)[1]
    
    if ext == ".json" or "chrome" in path.lower() or "edge" in path.lower() or "brave" in path.lower():
        return parse_chrome_bookmarks(path)
    elif ext == ".sqlite" or "places" in path.lower():
        return parse_firefox_sqlite(path)
    else:
        print(f"Unknown bookmark format: {path}")
        return []


def normalize_url(url: str) -> str:
    """Normalize URL for comparison."""
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        # Remove www, lowercase domain, remove trailing slash
        netloc = parsed.netloc.lower().replace("www.", "")
        if netloc.endswith("/"):
            netloc = netloc[:-1]
        path = parsed.path.rstrip("/") or "/"
        return f"{parsed.scheme}://{netloc}{path}"
    except:
        return url.lower().strip()


def find_duplicates(bookmarks: list) -> dict:
    """Find duplicate URLs."""
    normalized = defaultdict(list)
    
    for i, bm in enumerate(bookmarks):
        norm = normalize_url(bm["url"])
        if norm:
            normalized[norm].append((i, bm))
    
    duplicates = {k: v for k, v in normalized.items() if len(v) > 1}
    return duplicates


def deduplicate(bookmarks: list, keep: str = "first") -> list:
    """Remove duplicate bookmarks."""
    seen = set()
    result = []
    
    for bm in bookmarks:
        norm = normalize_url(bm["url"])
        if norm in seen:
            continue
        seen.add(norm)
        result.append(bm)
    
    return result


def search_bookmarks(bookmarks: list, query: str) -> list:
    """Search bookmarks by title, URL, or folder."""
    query = query.lower()
    results = []
    
    for bm in bookmarks:
        if (query in bm["title"].lower() or 
            query in bm["url"].lower() or 
            query in bm["folder"].lower()):
            results.append(bm)
    
    return results


def export_bookmarks(bookmarks: list, output: str, format: str = "html"):
    """Export bookmarks to HTML or JSON."""
    if format == "json":
        with open(output, "w", encoding="utf-8") as f:
            json.dump(bookmarks, f, indent=2)
    elif format == "html":
        # Generate HTML bookmark file
        folders = defaultdict(list)
        for bm in bookmarks:
            folders[bm["folder"]].append(bm)
        
        with open(output, "w", encoding="utf-8") as f:
            f.write('<!DOCTYPE NETSCAPE-Bookmark-file-1>\n')
            f.write('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n')
            f.write('<TITLE>Bookmarks</TITLE>\n')
            f.write('<H1>Bookmarks</H1>\n')
            f.write('<DL><p>\n')
            
            for folder, items in sorted(folders.items()):
                f.write(f'    <DT><H3>{folder}</H3>\n')
                f.write('    <DL><p>\n')
                for bm in items:
                    title = bm["title"].replace("&", "&amp;").replace("<", "&lt;")
                    url = bm["url"].replace("&", "&amp;")
                    f.write(f'        <DT><A HREF="{url}">{title}</A>\n')
                f.write('    </DL><p>\n')
            
            f.write('</DL><p>\n')
    
    print(f"Exported {len(bookmarks)} bookmarks to {output}")


def list_folders(bookmarks: list):
    """List all bookmark folders."""
    folders = defaultdict(int)
    for bm in bookmarks:
        folders[bm["folder"]] += 1
    
    for folder, count in sorted(folders.items(), key=lambda x: -x[1]):
        print(f"  [{count:4d}] {folder}")


def stats(bookmarks: list):
    """Show bookmark statistics."""
    print(f"\n📊 Bookmark Statistics")
    print(f"  Total bookmarks: {len(bookmarks)}")
    
    # Count by folder
    folders = defaultdict(int)
    for bm in bookmarks:
        folders[bm["folder"]] += 1
    
    print(f"  Total folders: {len(folders)}")
    
    # Check for duplicates
    dups = find_duplicates(bookmarks)
    print(f"  Duplicate URLs: {len(dups)} groups ({sum(len(v) for v in dups.values())} bookmarks)")
    
    # Top domains
    domains = defaultdict(int)
    for bm in bookmarks:
        try:
            domain = urlparse(bm["url"]).netloc.replace("www.", "")
            if domain:
                domains[domain] += 1
        except:
            pass
    
    print(f"  Top domains:")
    for domain, count in sorted(domains.items(), key=lambda x: -x[1])[:5]:
        print(f"    - {domain}: {count}")


def main():
    parser = argparse.ArgumentParser(description="Browser Bookmarks Manager")
    parser.add_argument("--browser", "-b", choices=["chrome", "firefox", "edge", "brave"],
                        help="Specific browser to use")
    parser.add_argument("--path", "-p", help="Path to bookmarks file")
    parser.add_argument("--list", "-l", action="store_true", help="List all folders")
    parser.add_argument("--stats", "-s", action="store_true", help="Show statistics")
    parser.add_argument("--search", "-q", help="Search bookmarks")
    parser.add_argument("--dedupe", "-d", action="store_true", help="Remove duplicates")
    parser.add_argument("--export", "-e", help="Export to file (format: html/json)")
    parser.add_argument("--format", "-f", default="html", choices=["html", "json"],
                        help="Export format")
    parser.add_argument("--output", "-o", help="Output file path")
    
    args = parser.parse_args()
    
    # Find bookmarks
    if args.path:
        path = os.path.expanduser(args.path)
        bookmarks = load_bookmarks(path)
    else:
        found = find_browser_bookmarks(args.browser)
        if not found:
            print("No browser bookmarks found!")
            return
        
        bookmarks = []
        for browser, path in found.items():
            print(f"Loading from {browser}: {path}")
            bms = load_bookmarks(path, browser)
            for bm in bms:
                bm["browser"] = browser
            bookmarks.extend(bms)
    
    if not bookmarks:
        print("No bookmarks loaded.")
        return
    
    print(f"Loaded {len(bookmarks)} bookmarks")
    
    if args.stats:
        stats(bookmarks)
    
    if args.list:
        print("\n📁 Folders:")
        list_folders(bookmarks)
    
    if args.search:
        results = search_bookmarks(bookmarks, args.search)
        print(f"\n🔍 Found {len(results)} results for '{args.search}':")
        for bm in results[:20]:
            print(f"  • {bm['title'][:50]}")
            print(f"    {bm['url'][:70]}")
            print(f"    Folder: {bm['folder']}")
    
    if args.dedupe:
        before = len(bookmarks)
        bookmarks = deduplicate(bookmarks)
        after = len(bookmarks)
        print(f"\n🧹 Removed {before - after} duplicates. {after} bookmarks remaining.")
    
    if args.export:
        output = args.output or args.export
        export_bookmarks(bookmarks, output, args.format)
    
    if not any([args.stats, args.list, args.search, args.dedupe, args.export]):
        # Show sample by default
        print("\n📖 Sample bookmarks:")
        for bm in bookmarks[:10]:
            print(f"  • {bm['title'][:40]}")


if __name__ == "__main__":
    main()
