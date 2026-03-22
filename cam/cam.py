#!/usr/bin/env python3
"""
Command Alias Manager - Define powerful shell aliases with variables
Features:
- Aliases with {variable} placeholders that prompt for values
- Pre-defined variable values for quick execution
- Command history and usage tracking
- Alias categories/groups
- Import/export aliases
- Quick execute with command-line args

Usage:
  cam                    # Interactive menu
  cam list               # List all aliases
  cam add <name> <cmd>   # Add new alias
  cam run <name> [args]  # Run alias with args
  cam edit <name>        # Edit alias
  cam delete <name>     # Delete alias
  cam export            # Export all aliases
  cam import <file>     # Import aliases
"""

import os
import sys
import json
import sqlite3
import subprocess
import shlex
import re
from pathlib import Path
from datetime import datetime

# Config
HOME = Path.home()
DATA_DIR = HOME / ".command_alias_manager"
DB_PATH = DATA_DIR / "aliases.db"
CONFIG_PATH = DATA_DIR / "config.json"

DATA_DIR.mkdir(exist_ok=True)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS aliases
                 (id INTEGER PRIMARY KEY, name TEXT UNIQUE, command TEXT,
                  description TEXT, category TEXT DEFAULT 'general',
                  created_at TEXT, updated_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY, alias_id INTEGER,
                  executed_at TEXT, args TEXT,
                  FOREIGN KEY(alias_id) REFERENCES aliases(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS var_presets
                 (id INTEGER PRIMARY KEY, alias_id INTEGER, preset_name TEXT,
                  var_values TEXT, FOREIGN KEY(alias_id) REFERENCES aliases(id))''')
    conn.commit()
    return conn

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {"shell": "/bin/bash", "editor": os.environ.get("EDITOR", "nano")}

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

def extract_variables(command):
    """Extract {varname} patterns from command"""
    return re.findall(r'\{(\w+)\}', command)

def prompt_variables(command, preset=None):
    """Prompt user for variable values"""
    variables = extract_variables(command)
    values = {}
    
    for var in variables:
        default = preset.get(var, "") if preset else ""
        val = input(f"  {var}" + (f" [{default}]: " if default else ": ")).strip()
        values[var] = val if val else default
    
    return values

def expand_command(command, values):
    """Replace {var} placeholders with values"""
    result = command
    for var, val in values.items():
        result = result.replace(f"{{{var}}}", val)
    return result

def execute_command(command, shell="/bin/bash"):
    """Execute command and return output"""
    try:
        result = subprocess.run(
            command, shell=True, executable=shell,
            capture_output=True, text=True, timeout=300
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1
    except Exception as e:
        return "", str(e), 1

# --- CLI Commands ---

def cmd_list(category=None):
    conn = get_db()
    c = conn.cursor()
    
    if category:
        c.execute("SELECT * FROM aliases WHERE category=? ORDER BY name", (category,))
    else:
        c.execute("SELECT * FROM aliases ORDER BY category, name")
    
    aliases = c.fetchall()
    if not aliases:
        print("No aliases defined yet. Use 'cam add' to create one.")
        return
    
    current_cat = None
    for a in aliases:
        if a['category'] != current_cat:
            current_cat = a['category']
            print(f"\n[{current_cat.upper()}]")
        vars_ = extract_variables(a['command'])
        var_str = f" ({', '.join(vars_)})" if vars_ else ""
        desc = f" - {a['description']}" if a['description'] else ""
        print(f"  {a['name']}{var_str}{desc}")
    print()

def cmd_add(name=None, command=None, description="", category="general"):
    conn = init_db()
    c = conn.cursor()
    
    if not name:
        name = input("Alias name: ").strip()
    if not command:
        print("Command (use {var} for variables, e.g., 'git commit -m {message}'):")
        command = input("> ").strip()
    if not description:
        description = input("Description (optional): ").strip()
    if not category:
        category = input("Category [general]: ").strip() or "general"
    
    try:
        now = datetime.now().isoformat()
        c.execute("INSERT INTO aliases (name, command, description, category, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                  (name, command, description, category, now, now))
        conn.commit()
        vars_ = extract_variables(command)
        print(f"✓ Alias '{name}' created{(' with variables: ' + ', '.join(vars_)) if vars_ else ''}")
    except sqlite3.IntegrityError:
        print(f"Error: Alias '{name}' already exists. Use 'cam edit {name}' to modify.")

def cmd_run(name, *args):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM aliases WHERE name=?", (name,))
    alias = c.fetchone()
    
    if not alias:
        print(f"Alias '{name}' not found.")
        return
    
    command = alias['command']
    variables = extract_variables(command)
    values = {}
    
    # Parse args (--var value format)
    arg_iter = iter(args)
    for arg in arg_iter:
        if arg.startswith("--"):
            var_name = arg[2:]
            try:
                values[var_name] = next(arg_iter)
            except StopIteration:
                print(f"Error: Missing value for --{var_name}")
                return
        elif variables:
            # Positional args fill variables in order
            for var in variables:
                if var not in values:
                    values[var] = arg
                    break
    
    # Prompt for missing variables
    for var in variables:
        if var not in values:
            default = ""
            val = input(f"  {var}" + (f" [{default}]: " if default else ": ")).strip()
            values[var] = val if val else default
    
    expanded = expand_command(command, values)
    print(f"\n▶ {expanded}\n")
    
    # Execute
    config = load_config()
    stdout, stderr, code = execute_command(expanded, config.get("shell", "/bin/bash"))
    
    if stdout:
        print(stdout, end="")
    if stderr:
        print(stderr, end="", file=sys.stderr)
    
    # Save to history
    c.execute("INSERT INTO history (alias_id, executed_at, args) VALUES (?, ?, ?)",
              (alias['id'], datetime.now().isoformat(), json.dumps(values)))
    conn.commit()
    
    return code

def cmd_edit(name):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM aliases WHERE name=?", (name,))
    alias = c.fetchone()
    
    if not alias:
        print(f"Alias '{name}' not found.")
        return
    
    print(f"Editing '{name}' (leave empty to keep current value):")
    
    new_name = input(f"  Name [{alias['name']}]: ").strip() or alias['name']
    new_cmd = input(f"  Command [{alias['command']}]: ").strip() or alias['command']
    new_desc = input(f"  Description [{alias['description']}]: ").strip() or alias['description']
    new_cat = input(f"  Category [{alias['category']}]: ").strip() or alias['category']
    
    c.execute("UPDATE aliases SET name=?, command=?, description=?, category=?, updated_at=? WHERE id=?",
              (new_name, new_cmd, new_desc, new_cat, datetime.now().isoformat(), alias['id']))
    conn.commit()
    print(f"✓ Alias '{new_name}' updated.")

def cmd_delete(name):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM aliases WHERE name=?", (name,))
    if c.rowcount:
        conn.commit()
        print(f"✓ Alias '{name}' deleted.")
    else:
        print(f"Alias '{name}' not found.")

def cmd_history(name=None, limit=10):
    conn = get_db()
    c = conn.cursor()
    
    if name:
        c.execute("""SELECT h.*, a.name as alias_name FROM history h
                     JOIN aliases a ON h.alias_id = a.id
                     WHERE a.name=? ORDER BY h.executed_at DESC LIMIT ?""", (name, limit))
    else:
        c.execute("""SELECT h.*, a.name as alias_name FROM history h
                     JOIN aliases a ON h.alias_id = a.id
                     ORDER BY h.executed_at DESC LIMIT ?""", (limit,))
    
    for row in c.fetchall():
        args = json.loads(row['args']) if row['args'] else {}
        args_str = " ".join(f"--{k} {v}" for k, v in args.items())
        print(f"  {row['executed_at'][:19]} | {row['alias_name']} {args_str}")

def cmd_export(path=None):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM aliases")
    
    aliases = []
    for row in c.fetchall():
        aliases.append({
            "name": row['name'],
            "command": row['command'],
            "description": row['description'],
            "category": row['category']
        })
    
    export_path = path or input("Export file path: ").strip()
    if not export_path:
        print("No path specified.")
        return
    
    with open(export_path, 'w') as f:
        json.dump(aliases, f, indent=2)
    print(f"✓ Exported {len(aliases)} aliases to {export_path}")

def cmd_import(path):
    if not Path(path).exists():
        print(f"File not found: {path}")
        return
    
    with open(path) as f:
        aliases = json.load(f)
    
    conn = init_db()
    c = conn.cursor()
    imported = 0
    
    for a in aliases:
        try:
            now = datetime.now().isoformat()
            c.execute("INSERT OR REPLACE INTO aliases (name, command, description, category, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                      (a['name'], a['command'], a.get('description', ''), a.get('category', 'general'), now, now))
            imported += 1
        except Exception as e:
            print(f"  Warning: Could not import '{a.get('name', 'unknown')}': {e}")
    
    conn.commit()
    print(f"✓ Imported {imported} aliases.")

def cmd_search(query):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM aliases WHERE name LIKE ? OR command LIKE ? OR description LIKE ?",
              (f"%{query}%", f"%{query}%", f"%{query}%"))
    
    for row in c.fetchall():
        print(f"  {row['name']} [{row['category']}]")
        print(f"    {row['command']}")
        if row['description']:
            print(f"    {row['description']}")
        print()

def cmd_show(name):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM aliases WHERE name=?", (name,))
    alias = c.fetchone()
    
    if not alias:
        print(f"Alias '{name}' not found.")
        return
    
    print(f"Name: {alias['name']}")
    print(f"Category: {alias['category']}")
    print(f"Command: {alias['command']}")
    print(f"Description: {alias['description']}")
    print(f"Variables: {', '.join(extract_variables(alias['command'])) or 'none'}")
    print(f"Created: {alias['created_at']}")
    print(f"Updated: {alias['updated_at']}")

def cmd_categories():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT category, COUNT(*) as count FROM aliases GROUP BY category ORDER BY count DESC")
    
    print("Categories:")
    for row in c.fetchall():
        print(f"  {row['category']}: {row['count']} alias(es)")

def interactive():
    """Interactive TUI menu"""
    while True:
        print("\n=== Command Alias Manager ===")
        print("  1. List aliases")
        print("  2. Add new alias")
        print("  3. Run alias")
        print("  4. Edit alias")
        print("  5. Delete alias")
        print("  6. Search aliases")
        print("  7. View history")
        print("  8. Categories")
        print("  9. Export aliases")
        print(" 10. Import aliases")
        print("  0. Exit")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "1":
            cmd_list()
        elif choice == "2":
            cmd_add()
        elif choice == "3":
            name = input("Alias name: ").strip()
            if name:
                cmd_run(name)
        elif choice == "4":
            name = input("Alias name: ").strip()
            if name:
                cmd_edit(name)
        elif choice == "5":
            name = input("Alias name: ").strip()
            if name:
                cmd_delete(name)
        elif choice == "6":
            query = input("Search query: ").strip()
            if query:
                cmd_search(query)
        elif choice == "7":
            cmd_history()
        elif choice == "8":
            cmd_categories()
        elif choice == "9":
            path = input("Export file path: ").strip()
            cmd_export(path)
        elif choice == "10":
            path = input("Import file path: ").strip()
            cmd_import(path)
        elif choice == "0":
            break

def main():
    init_db()
    
    if len(sys.argv) < 2:
        interactive()
        return
    
    cmd = sys.argv[1]
    args = sys.argv[2:]
    
    if cmd in ("list", "ls"):
        cmd_list(*args)
    elif cmd in ("add", "new"):
        cmd_add(*args)
    elif cmd in ("run", "exec", "x"):
        if not args:
            print("Usage: cam run <name> [args...]")
            sys.exit(1)
        sys.exit(cmd_run(args[0], *args[1:]) or 0)
    elif cmd in ("edit", "e"):
        if not args:
            print("Usage: cam edit <name>")
            sys.exit(1)
        cmd_edit(args[0])
    elif cmd in ("delete", "rm", "del"):
        if not args:
            print("Usage: cam delete <name>")
            sys.exit(1)
        cmd_delete(args[0])
    elif cmd in ("history", "hist"):
        cmd_history(*args)
    elif cmd in ("export", "exp"):
        cmd_export(*args)
    elif cmd in ("import", "imp"):
        if not args:
            print("Usage: cam import <file>")
            sys.exit(1)
        cmd_import(args[0])
    elif cmd in ("search", "find"):
        if not args:
            print("Usage: cam search <query>")
            sys.exit(1)
        cmd_search(args[0])
    elif cmd in ("show", "info"):
        if not args:
            print("Usage: cam show <name>")
            sys.exit(1)
        cmd_show(args[0])
    elif cmd in ("categories", "cats"):
        cmd_categories()
    elif cmd in ("help", "-h", "--help"):
        print(__doc__)
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
