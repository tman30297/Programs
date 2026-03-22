#!/usr/bin/env python3
"""
Quick Launcher - A Spotlight/Alfred-like command launcher
Features:
- File search (recent + by name)
- Quick calculations
- Web search
- Clipboard history
- Custom shortcuts/commands
- System commands
"""

import os
import sys
import re
import sqlite3
import subprocess
import datetime
import json
import glob
import shlex
from pathlib import Path
from urllib.parse import quote

# Config
HOME = Path.home()
DATA_DIR = HOME / ".quicklauncher"
DB_PATH = DATA_DIR / "launcher.db"
CONFIG_PATH = DATA_DIR / "config.json"
SHORTCUTS_PATH = DATA_DIR / "shortcuts.json"

DATA_DIR.mkdir(exist_ok=True)

def init_db():
    """Initialize database for clipboard history and usage stats"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clipboard_history
                 (id INTEGER PRIMARY KEY, content TEXT, content_type TEXT, 
                  copied_at TEXT, used_count INTEGER DEFAULT 1)''')
    c.execute('''CREATE TABLE IF NOT EXISTS recent_files
                 (id INTEGER PRIMARY KEY, path TEXT, accessed_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS search_history
                 (id INTEGER PRIMARY KEY, query TEXT, searched_at TEXT)''')
    conn.commit()
    return conn

def load_config():
    """Load configuration"""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {
        "search_paths": [str(HOME)],
        "max_results": 10,
        "browser": "firefox",
        "calculator_precision": 4
    }

def save_config(config):
    """Save configuration"""
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

def load_shortcuts():
    """Load user-defined shortcuts"""
    if SHORTCUTS_PATH.exists():
        with open(SHORTCUTS_PATH) as f:
            return json.load(f)
    # Default shortcuts
    defaults = {
        "gh": "https://github.com/search?q={query}",
        "google": "https://google.com/search?q={query}",
        "youtube": "https://youtube.com/results?search_query={query}",
        "wiki": "https://en.wikipedia.org/wiki/{query}",
        "dict": "https://dictionary.com/browse/{query}",
        "npm": "https://npmjs.com/search?q={query}",
        "pip": "https://pypi.org/search/?q={query}",
        "ghu": "https://github.com/{query}",
        "weather": "https://wttr.in/{query}",
    }
    save_shortcuts(defaults)
    return defaults

def save_shortcuts(shortcuts):
    """Save shortcuts"""
    with open(SHORTCUTS_PATH, 'w') as f:
        json.dump(shortcuts, f, indent=2)

# === CALCULATOR ===
def calculate(expr):
    """Evaluate a mathematical expression safely"""
    expr = expr.replace('^', '**').replace('×', '*').replace('÷', '/')
    
    # Safe math evaluation
    allowed = set('0123456789.+-*/%()** ')
    if all(c in allowed or c.isspace() for c in expr):
        try:
            result = eval(expr)
            if isinstance(result, float):
                result = round(result, 10)
                if result == int(result):
                    result = int(result)
            return str(result)
        except:
            return None
    return None

# === CLIPBOARD ===
def get_clipboard():
    """Get current clipboard content"""
    try:
        # Try xclip first (Linux)
        result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'], 
                               capture_output=True, text=True, timeout=1)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    try:
        # Try pbpaste (macOS)
        result = subprocess.run(['pbpaste'], capture_output=True, text=True, timeout=1)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return None

def set_clipboard(text):
    """Set clipboard content"""
    try:
        subprocess.run(['xclip', '-selection', 'clipboard', '-i'], 
                      input=text, text=True, timeout=1)
        return True
    except:
        pass
    try:
        subprocess.run(['pbcopy'], input=text, text=True, timeout=1)
        return True
    except:
        pass
    return False

def add_to_clipboard_history(conn, content):
    """Add to clipboard history"""
    if not content or len(content) > 10000:
        return
    c = conn.cursor()
    # Check if exists
    c.execute("SELECT id, used_count FROM clipboard_history WHERE content = ?", (content,))
    row = c.fetchone()
    if row:
        c.execute("UPDATE clipboard_history SET used_count = ?, copied_at = ? WHERE id = ?",
                  (row[1] + 1, datetime.datetime.now().isoformat(), row[0]))
    else:
        content_type = "text"
        if content.startswith('http'):
            content_type = "url"
        c.execute("INSERT INTO clipboard_history (content, content_type, copied_at) VALUES (?, ?, ?)",
                  (content, content_type, datetime.datetime.now().isoformat()))
    conn.commit()

def get_clipboard_history(conn, limit=20):
    """Get clipboard history"""
    c = conn.cursor()
    c.execute("SELECT content, content_type, used_count, copied_at FROM clipboard_history ORDER BY copied_at DESC LIMIT ?", (limit,))
    return c.fetchall()

# === FILE SEARCH ===
def search_files(query, max_results=10):
    """Search files by name in search paths"""
    config = load_config()
    results = []
    query_lower = query.lower()
    
    for search_path in config.get("search_paths", []):
        path = Path(search_path)
        if not path.exists():
            continue
        try:
            # Search by name
            for item in path.rglob(f"*{query}*"):
                if len(results) >= max_results:
                    break
                if item.is_file():
                    rel = item.relative_to(HOME)
                    results.append({
                        "type": "file",
                        "name": item.name,
                        "path": str(item),
                        "display": f"📄 {rel}"
                    })
        except PermissionError:
            continue
    return results[:max_results]

def get_recent_files(conn, limit=10):
    """Get recently accessed files"""
    c = conn.cursor()
    c.execute("SELECT path, accessed_at FROM recent_files ORDER BY accessed_at DESC LIMIT ?", (limit,))
    return c.fetchall()

def add_recent_file(conn, filepath):
    """Add to recent files"""
    c = conn.cursor()
    c.execute("DELETE FROM recent_files WHERE path = ?", (filepath,))
    c.execute("INSERT INTO recent_files (path, accessed_at) VALUES (?, ?)",
              (filepath, datetime.datetime.now().isoformat()))
    # Keep only last 100
    c.execute("DELETE FROM recent_files WHERE id NOT IN (SELECT id FROM recent_files ORDER BY accessed_at DESC LIMIT 100)")
    conn.commit()

# === SHORTCUTS / URL HANDLING ===
def handle_shortcut(query):
    """Handle built-in shortcuts and URL queries"""
    shortcuts = load_shortcuts()
    
    # Check for shortcut prefix (e.g., "gh myrepo" or just "gh myrepo")
    parts = query.split()
    if len(parts) >= 1:
        prefix = parts[0].lower()
        if prefix in shortcuts:
            shortcut = shortcuts[prefix]
            if len(parts) > 1:
                # Has query argument
                query_arg = " ".join(parts[1:])
                url = shortcut.replace("{query}", quote(query_arg))
            else:
                url = shortcut.replace("{query}", "")
            return {"type": "url", "url": url, "display": f"🌐 {url}"}
    
    # Check if it's a direct URL
    if query.startswith("http://") or query.startswith("https://"):
        return {"type": "url", "url": query, "display": f"🌐 {query}"}
    
    # Check for domain-like input (e.g., "github.com/user")
    if re.match(r'^[\w.-]+\.\w+', query):
        if not query.startswith("http"):
            url = f"https://{query}"
            return {"type": "url", "url": url, "display": f"🌐 {url}"}
    
    return None

# === SYSTEM COMMANDS ===
SYSTEM_COMMANDS = {
    "reboot": "sudo reboot",
    "shutdown": "sudo shutdown -h now",
    "lock": "loginctl lock-session",
    "suspend": "systemctl suspend",
    "exit": "exit 0",
}

def handle_system_command(query):
    """Handle system commands"""
    query = query.lower().strip()
    if query in SYSTEM_COMMANDS:
        return {"type": "system", "command": SYSTEM_COMMANDS[query], "display": f"⚙️ {query}"}
    return None

# === MAIN LAUNCHER ===
def search(query):
    """Main search function"""
    if not query:
        return []
    
    conn = init_db()
    results = []
    query = query.strip()
    
    # 1. Check for calculator
    calc_result = calculate(query)
    if calc_result is not None:
        results.append({"type": "calc", "result": calc_result, "display": f"🧮 {query} = {calc_result}"})
    
    # 2. Check for shortcuts/URLs
    shortcut_result = handle_shortcut(query)
    if shortcut_result:
        results.append(shortcut_result)
    
    # 3. Check for system commands
    sys_result = handle_system_command(query)
    if sys_result:
        results.append(sys_result)
    
    # 4. Search files
    files = search_files(query)
    results.extend(files)
    
    # 5. Search clipboard history for matching text
    clipboard_history = get_clipboard_history(conn)
    for item in clipboard_history[:5]:
        content = item[0]
        if query.lower() in content.lower():
            results.append({
                "type": "clipboard",
                "content": content[:100],
                "display": f"📋 {content[:80]}..."
            })
    
    return results

def show_recent():
    """Show recent items"""
    conn = init_db()
    results = []
    
    # Recent files
    recent = get_recent_files(conn)
    for path, accessed in recent[:5]:
        results.append({
            "type": "recent",
            "path": path,
            "display": f"📁 {Path(path).name}"
        })
    
    return results

def show_clipboard():
    """Show clipboard history"""
    conn = init_db()
    history = get_clipboard_history(conn)
    results = []
    for i, item in enumerate(history[:10]):
        content = item[0][:80]
        ctype = item[1]
        count = item[2]
        icon = "🔗" if ctype == "url" else "📋"
        results.append({
            "type": "clipboard_item",
            "index": i,
            "content": item[0],
            "display": f"{icon} {content}{'...' if len(item[0]) > 80 else ''} (used {count}x)"
        })
    return results

def add_shortcut(prefix, url_template):
    """Add a new shortcut"""
    shortcuts = load_shortcuts()
    shortcuts[prefix] = url_template
    save_shortcuts(shortcuts)
    return f"Added shortcut: {prefix} -> {url_template}"

def list_shortcuts():
    """List all shortcuts"""
    shortcuts = load_shortcuts()
    return [{"prefix": k, "url": v} for k, v in shortcuts.items()]

def open_result(result):
    """Open a result based on its type"""
    conn = init_db()
    
    if result["type"] == "file":
        path = result["path"]
        add_recent_file(conn, path)
        # Open with xdg-open
        subprocess.Popen(["xdg-open", path])
        return f"Opened: {path}"
    
    elif result["type"] == "url":
        config = load_config()
        browser = config.get("browser", "firefox")
        subprocess.Popen([browser, result["url"]])
        return f"Opened: {result['url']}"
    
    elif result["type"] == "clipboard":
        set_clipboard(result["content"])
        return "Copied to clipboard"
    
    elif result["type"] == "clipboard_item":
        set_clipboard(result["content"])
        add_to_clipboard_history(conn, result["content"])
        return "Copied to clipboard"
    
    elif result["type"] == "recent":
        path = result["path"]
        add_recent_file(conn, path)
        subprocess.Popen(["xdg-open", path])
        return f"Opened: {path}"
    
    elif result["type"] == "system":
        return "Would execute system command (not implemented for safety)"
    
    return "Unknown result type"

# === CLI INTERFACE ===
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Quick Launcher")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--open", "-o", type=int, help="Open result by index")
    parser.add_argument("--recent", "-r", action="store_true", help="Show recent files")
    parser.add_argument("--clipboard", "-c", action="store_true", help="Show clipboard history")
    parser.add_argument("--add-shortcut", nargs=2, metavar=("PREFIX", "URL"), help="Add shortcut (e.g., gh 'https://github.com/{query}')")
    parser.add_argument("--list-shortcuts", "-ls", action="store_true", help="List shortcuts")
    parser.add_argument("--copy", "-cp", type=int, help="Copy result to clipboard by index")
    args = parser.parse_args()
    
    if args.add_shortcut:
        print(add_shortcut(args.add_shortcut[0], args.add_shortcut[1]))
        return
    
    if args.list_shortcuts:
        print("Shortcuts:")
        for sc in list_shortcuts():
            print(f"  {sc['prefix']}: {sc['url']}")
        return
    
    if args.recent:
        results = show_recent()
        for i, r in enumerate(results):
            print(f"[{i}] {r['display']}")
        return
    
    if args.clipboard:
        results = show_clipboard()
        for i, r in enumerate(results):
            print(f"[{i}] {r['display']}")
        return
    
    if args.query:
        results = search(args.query)
        for i, r in enumerate(results):
            print(f"[{i}] {r['display']}")
        
        if args.open is not None and args.open < len(results):
            print(f"\n{open_result(results[args.open])}")
        
        if args.copy is not None and args.copy < len(results):
            result = results[args.copy]
            if result["type"] in ["file", "recent"]:
                result = {"type": "clipboard_item", "content": result["path"], "index": args.copy}
            print(f"\n{open_result(result)}")
    else:
        # Default: show recent
        results = show_recent()
        print("Recent files:")
        for i, r in enumerate(results):
            print(f"[{i}] {r['display']}")
        print("\nUsage: quicklauncher <query>")
        print("  quicklauncher --recent       # Show recent files")
        print("  quicklauncher --clipboard    # Show clipboard history")
        print("  quicklauncher --list-shortcuts")
        print("  quicklauncher --add-shortcut gh 'https://github.com/{query}'")

if __name__ == "__main__":
    main()
