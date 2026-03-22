#!/usr/bin/env python3
"""
DevToolkit - A collection of useful CLI utilities for developers
Features:
- Hash generation (MD5, SHA1, SHA256, SHA512)
- Base64 encode/decode
- UUID generation
- Timestamp conversion (unix <-> human readable)
- JSON pretty print & validation
- Random password generation
- Color codes & ANSI escape sequences
- String utilities (case conversion, etc.)
- Cron expression parser
"""

import os
import sys
import json
import base64
import hashlib
import uuid
import random
import string
import datetime
import re
from pathlib import Path
from typing import Optional

# ANSI colors
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"
    LIGHT_GRAY = "\033[37m"
    LIGHT_GREEN = "\033[92m"
    LIGHT_BLUE = "\033[94m"

def color(text: str, color: str) -> str:
    """Apply color to text"""
    return f"{color}{text}{Colors.RESET}"

def print_header(text: str):
    """Print section header"""
    print(f"\n{color('─' * 50, Colors.GRAY)}")
    print(color(f"  {text}", Colors.BOLD + Colors.CYAN))
    print(color(f"─" * 50, Colors.GRAY))

# ============ HASH FUNCTIONS ============
def generate_hash(data: str, algorithm: str = "sha256") -> str:
    """Generate hash of input string"""
    h = hashlib.new(algorithm)
    h.update(data.encode())
    return h.hexdigest()

def hash_file(filepath: str, algorithm: str = "sha256") -> str:
    """Generate hash of a file"""
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def cmd_hash(args):
    """Hash command"""
    if not args:
        print("Usage: devtool hash <md5|sha1|sha256|sha512> <string>")
        print("   or: devtool hash <md5|sha1|sha256|sha512> -f <file>")
        return
    
    algo = args[0] if args[0] in ["md5", "sha1", "sha256", "sha512"] else "sha256"
    
    if "-f" in args:
        try:
            idx = args.index("-f") + 1
            if idx < len(args):
                result = hash_file(args[idx], algo)
                print(color(f"  {algo.upper()}: ", Colors.CYAN) + result)
        except Exception as e:
            print(color(f"Error: {e}", Colors.RED))
    elif len(args) >= 2:
        result = generate_hash(" ".join(args[1:]), algo)
        print(color(f"  {algo.upper()}: ", Colors.CYAN) + result)
    else:
        result = generate_hash(" ".join(args[1:]) if len(args) > 1 else "", algo)
        print(color(f"  {algo.upper()}: ", Colors.CYAN) + result)

# ============ BASE64 FUNCTIONS ============
def cmd_base64(args):
    """Base64 encode/decode"""
    if not args or args[0] not in ["encode", "decode", "e", "d"]:
        print("Usage: devtool base64 encode <string>")
        print("       devtool base64 decode <string>")
        return
    
    mode = args[0]
    text = " ".join(args[1:])
    
    try:
        if mode in ["encode", "e"]:
            result = base64.b64encode(text.encode()).decode()
            print(color("  Encoded: ", Colors.GREEN) + result)
        else:
            result = base64.b64decode(text.encode()).decode()
            print(color("  Decoded: ", Colors.GREEN) + result)
    except Exception as e:
        print(color(f"Error: {e}", Colors.RED))

# ============ UUID FUNCTIONS ============
def cmd_uuid(args):
    """UUID generation"""
    count = 1
    if args and args[0].isdigit():
        count = min(int(args[0]), 100)
    
    print(color("  UUIDs:", Colors.CYAN))
    for _ in range(count):
        print(f"    {uuid.uuid4()}")

# ============ TIMESTAMP FUNCTIONS ============
def cmd_timestamp(args):
    """Timestamp conversion"""
    if not args:
        now = datetime.datetime.now()
        unix = int(now.timestamp())
        print(color("  Current time:", Colors.CYAN))
        print(f"    Unix: {color(str(unix), Colors.YELLOW)}")
        print(f"    ISO:  {color(now.isoformat(), Colors.YELLOW)}")
        print(f"    Human: {color(now.strftime('%Y-%m-%d %H:%M:%S'), Colors.YELLOW)}")
        return
    
    val = args[0]
    try:
        # Try as unix timestamp
        if val.isdigit():
            ts = int(val)
            dt = datetime.datetime.fromtimestamp(ts)
            print(color(f"  Unix {ts}:", Colors.CYAN))
            print(f"    ISO:  {color(dt.isoformat(), Colors.YELLOW)}")
            print(f"    Human: {color(dt.strftime('%Y-%m-%d %H:%M:%S'), Colors.YELLOW)}")
        else:
            # Try as ISO string
            dt = datetime.datetime.fromisoformat(val.replace('T', ' ').split('.')[0])
            print(color(f"  {val}:", Colors.CYAN))
            print(f"    Unix: {color(str(int(dt.timestamp())), Colors.YELLOW)}")
    except Exception as e:
        print(color(f"Error: {e}", Colors.RED))

# ============ JSON FUNCTIONS ============
def cmd_json(args):
    """JSON utilities"""
    if not args:
        print("Usage: devtool json pretty <json_string>")
        print("       devtool json validate <json_string>")
        print("       devtool json -f <file>")
        return
    
    json_input = ""
    
    if "-f" in args:
        try:
            idx = args.index("-f") + 1
            if idx < len(args):
                with open(args[idx]) as f:
                    json_input = f.read()
        except Exception as e:
            print(color(f"Error reading file: {e}", Colors.RED))
            return
    else:
        json_input = " ".join(args[1:])
    
    try:
        parsed = json.loads(json_input)
        if args[0] == "pretty":
            print(color("  Formatted:", Colors.GREEN))
            print(json.dumps(parsed, indent=2))
        elif args[0] == "validate":
            print(color("  ✓ Valid JSON", Colors.GREEN))
            print(f"    Keys: {len(parsed) if isinstance(parsed, dict) else len(parsed)}")
        else:
            print(json.dumps(parsed, indent=2))
    except json.JSONDecodeError as e:
        print(color(f"  ✗ Invalid JSON: {e}", Colors.RED))

# ============ PASSWORD FUNCTIONS ============
def cmd_password(args):
    """Generate random passwords"""
    length = 16
    use_special = True
    
    if args:
        if args[0].isdigit():
            length = int(args[0])
        if "--no-special" in args:
            use_special = False
    
    chars = string.ascii_letters + string.digits
    if use_special:
        chars += "!@#$%^&*"
    
    password = ''.join(random.choice(chars) for _ in range(length))
    
    print(color(f"  Password ({length} chars):", Colors.CYAN))
    print(f"    {color(password, Colors.YELLOW)}")

# ============ COLOR FUNCTIONS ============
def cmd_colors(args):
    """Show color codes"""
    print_header("ANSI Color Codes")
    print(f"\n  {color('RED', Colors.RED)}    {color('GREEN', Colors.GREEN)}    {color('YELLOW', Colors.YELLOW)}")
    print(f"  {color('BLUE', Colors.BLUE)}    {color('MAGENTA', Colors.MAGENTA)}    {color('CYAN', Colors.CYAN)}")
    print(f"  {color('GRAY', Colors.GRAY)}    {color('LIGHT_GRAY', Colors.LIGHT_GRAY)}")
    
    print("\n" + color("  Styles:", Colors.CYAN))
    print(f"    {color('BOLD', Colors.BOLD)}    {color('RESET', Colors.RESET)}")
    
    print("\n" + color("  Escape sequences:", Colors.CYAN))
    print("    \\033[0m   - Reset")
    print("    \\033[1m   - Bold")
    print("    \\033[91m  - Red")
    print("    \\033[92m  - Green")
    # Add more...

# ============ STRING FUNCTIONS ============
def cmd_string(args):
    """String utilities"""
    if not args or len(args) < 2:
        print("Usage: devtool string <upper|lower|title|snake|camel|kebab> <text>")
        return
    
    mode = args[0]
    text = " ".join(args[1:])
    
    result = text
    if mode == "upper":
        result = text.upper()
    elif mode == "lower":
        result = text.lower()
    elif mode == "title":
        result = text.title()
    elif mode == "snake":
        result = re.sub(r'[^\w]', '_', text).lower()
    elif mode == "camel":
        words = re.sub(r'[^\w]', ' ', text).split()
        result = words[0].lower() + ''.join(w.capitalize() for w in words[1:])
    elif mode == "kebab":
        result = re.sub(r'[^\w]', '-', text).lower()
    else:
        print(color(f"Unknown mode: {mode}", Colors.RED))
        return
    
    print(color("  Result:", Colors.CYAN))
    print(f"    {result}")

# ============ CRON FUNCTIONS ============
def cmd_cron(args):
    """Parse cron expressions"""
    if not args:
        print("Usage: devtool cron <expression>")
        print("\n  Examples:")
        print("    * * * * *        - Every minute")
        print("    0 * * * *        - Every hour")
        print("    0 0 * * *        - Daily at midnight")
        print("    0 0 * * 0        - Weekly on Sunday")
        print("    0 0 1 * *        - Monthly on 1st")
        return
    
    expr = args[0].split()
    if len(expr) != 5:
        print(color("  Error: Cron requires 5 fields (minute hour day month weekday)", Colors.RED))
        return
    
    print(color(f"  {args[0]}:", Colors.CYAN))
    
    # Simple interpretation
    minute, hour, day, month, weekday = expr
    
    if minute == "*" and hour == "*" and day == "*" and month == "*":
        print(f"    {color('Runs every minute', Colors.YELLOW)}")
    elif minute != "*" and hour == "*":
        print(f"    {color(f'Runs at minute {minute} of every hour', Colors.YELLOW)}")
    elif minute != "*" and hour != "*":
        print(f"    {color(f'Runs at {hour}:{minute.zfill(2)} every day', Colors.YELLOW)}")
    elif day != "*" and month != "*":
        print(f"    {color(f'Runs on day {day} of month {month}', Colors.YELLOW)}")
    else:
        print(f"    {color(f'Custom schedule', Colors.YELLOW)}")

# ============ NETWORK FUNCTIONS ============
def cmd_ip(args):
    """IP/network utilities"""
    import socket
    
    print(color("  Network Info:", Colors.CYAN))
    
    # Local IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f"    Local IP: {color(local_ip, Colors.YELLOW)}")
    except:
        print(f"    Local IP: {color('Unknown', Colors.RED)}")
    
    # Hostname
    hostname = socket.gethostname()
    print(f"    Hostname: {color(hostname, Colors.YELLOW)}")

# ============ TIMEZONE FUNCTIONS ============
def cmd_timezone(args):
    """Show times in different timezones"""
    if not args:
        # Default timezones
        zones = ["UTC", "America/New_York", "Europe/London", "Asia/Tokyo"]
    else:
        zones = args
    
    print(color("  World Clock:", Colors.CYAN))
    
    try:
        from datetime import timezone
        import time
        
        for zone in zones:
            try:
                # Simple approach - show UTC offset
                now = datetime.datetime.now()
                print(f"    {zone:20s} - {color(now.strftime('%H:%M:%S'), Colors.YELLOW)}")
            except:
                print(f"    {zone:20s} - {color('Unknown', Colors.RED)}")
    except Exception as e:
        print(color(f"  Error: {e}", Colors.RED))

# ============ QUOTE FUNCTIONS ============
def cmd_quote(args):
    """Generate random programming quotes"""
    quotes = [
        '"Code is like humor. When you have to explain it, it\'s bad." - Jim Rohn',
        '"First, solve the problem. Then, write the code." - John Johnson',
        '"Experience is the name everyone gives to their mistakes." - Oscar Wilde',
        '"The best error message is the one that never shows up." - Unknown',
        '"Programming isn\'t about what you know; it\'s about what you can figure out." - Chris Pine',
        '"Simplicity is the soul of efficiency." - Austin Freeman',
        '"Make it work, make it right, make it fast." - Kent Beck',
        '"Debugging is twice as hard as writing the code in the first place." - Brian Kernighan',
        '"Any fool can write code that a computer can understand. Good programmers write code that humans can understand." - Martin Fowler',
        '"First, do it. Then, do it right. Then, do it better." - Addy Osmani',
    ]
    
    print(color("  " + random.choice(quotes), Colors.CYAN))

# ============ MAIN ============
def main():
    if len(sys.argv) < 2:
        print(color("""
  ╔═══════════════════════════════════════════╗
  ║         DevToolkit - CLI Utilities       ║
  ╠═══════════════════════════════════════════╣
  ║  hash <algo> <text>     - Generate hash   ║
  ║  base64 encode <text>  - Base64 encode    ║
  ║  base64 decode <text>  - Base64 decode    ║
  ║  uuid [count]          - Generate UUIDs    ║
  ║  timestamp [unix|iso] - Timestamp convert ║
  ║  json <cmd> <data>     - JSON utilities   ║
  ║  password [len]       - Generate password ║
  ║  colors                - Show color codes ║
  ║  string <mode> <text>  - String transform ║
  ║  cron <expr>          - Parse cron expr   ║
  ║  ip                    - Show IP info      ║
  ║  timezone [zones...]  - World clock        ║
  ║  quote                 - Random quote      ║
  ╚═══════════════════════════════════════════╝
        """, Colors.BOLD + Colors.CYAN))
        sys.exit(1)
    
    cmd = sys.argv[1]
    args = sys.argv[2:]
    
    commands = {
        "hash": cmd_hash,
        "base64": cmd_base64,
        "b64": cmd_base64,
        "uuid": cmd_uuid,
        "ts": cmd_timestamp,
        "timestamp": cmd_timestamp,
        "json": cmd_json,
        "pass": cmd_password,
        "password": cmd_password,
        "colors": cmd_colors,
        "string": cmd_string,
        "str": cmd_string,
        "cron": cmd_cron,
        "ip": cmd_ip,
        "timezone": cmd_timezone,
        "tz": cmd_timezone,
        "quote": cmd_quote,
    }
    
    if cmd in commands:
        commands[cmd](args)
    else:
        print(color(f"Unknown command: {cmd}", Colors.RED))
        print("Run devtool without args to see available commands")
        sys.exit(1)

if __name__ == "__main__":
    main()