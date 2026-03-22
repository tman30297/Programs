#!/usr/bin/env python3
"""
Utility Toolkit
- Password Generator
- JSON Formatter/Validator
- CSV to JSON Converter
- Web Server Status Checker
"""

import json
import csv
import random
import string
import argparse
import sys
import socket
import urllib.request
import urllib.error
from pathlib import Path


# ========== Password Generator ==========
def generate_password(length=16, use_special=True, use_numbers=True, use_uppercase=True):
    """Generate a secure random password."""
    chars = string.ascii_lowercase
    if use_uppercase:
        chars += string.ascii_uppercase
    if use_numbers:
        chars += string.digits
    if use_special:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    password = ''.join(random.choice(chars) for _ in range(length))
    return password


def password_generator_cli(args):
    """CLI for password generator."""
    if args.count:
        for _ in range(args.count):
            pw = generate_password(args.length, args.special, args.numbers, args.uppercase)
            print(pw)
    else:
        pw = generate_password(args.length, args.special, args.numbers, args.uppercase)
        print(pw)


# ========== JSON Formatter/Validator ==========
def format_json(input_data, indent=2, sort_keys=False):
    """Format JSON data with proper indentation."""
    if isinstance(input_data, str):
        data = json.loads(input_data)
    else:
        data = input_data
    return json.dumps(data, indent=indent, sort_keys=sort_keys)


def validate_json(input_data):
    """Validate JSON and return details."""
    try:
        if isinstance(input_data, str):
            data = json.loads(input_data)
        else:
            data = input_data
        return True, "Valid JSON", data
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}", None


def json_tool_cli(args):
    """CLI for JSON formatter/validator."""
    if args.file:
        with open(args.file, 'r') as f:
            content = f.read()
    else:
        content = args.input
    
    if args.validate:
        valid, msg, data = validate_json(content)
        print(f"Status: {'✓ Valid' if valid else '✗ Invalid'}")
        print(f"Message: {msg}")
        if valid and args.file:
            with open(args.file, 'w') as f:
                f.write(format_json(data, indent=args.indent, sort_keys=args.sort))
            print(f"Formatted and saved to {args.file}")
    else:
        data = json.loads(content) if isinstance(content, str) else content
        print(format_json(data, indent=args.indent, sort_keys=args.sort))


# ========== CSV to JSON Converter ==========
def csv_to_json(csv_file, json_file=None, delimiter=',', encoding='utf-8'):
    """Convert CSV file to JSON."""
    rows = []
    with open(csv_file, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            rows.append(dict(row))
    
    json_data = json.dumps(rows, indent=2)
    
    if json_file:
        with open(json_file, 'w') as f:
            f.write(json_data)
        return json_data, len(rows)
    
    return json_data, len(rows)


def csv_to_json_cli(args):
    """CLI for CSV to JSON converter."""
    json_data, count = csv_to_json(
        args.csv_file, 
        args.output, 
        args.delimiter,
        args.encoding
    )
    print(f"Converted {count} rows")
    if not args.output:
        print(json_data)


# ========== Web Server Status Checker ==========
def check_server(url, timeout=5):
    """Check if a web server is responding."""
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        req = urllib.request.Request(url, method='GET')
        req.add_header('User-Agent', 'Mozilla/5.0 (compatible; UtilityBot/1.0)')
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return {
                'url': url,
                'status': 'UP',
                'status_code': response.status,
                'response_time': response.getheader('Server', 'Unknown'),
                'error': None
            }
    except urllib.error.HTTPError as e:
        return {
            'url': url,
            'status': 'DOWN',
            'status_code': e.code,
            'error': f"HTTP {e.code}: {e.reason}"
        }
    except urllib.error.URLError as e:
        return {
            'url': url,
            'status': 'DOWN',
            'status_code': None,
            'error': str(e.reason)
        }
    except socket.timeout:
        return {
            'url': url,
            'status': 'TIMEOUT',
            'status_code': None,
            'error': 'Connection timed out'
        }
    except Exception as e:
        return {
            'url': url,
            'status': 'ERROR',
            'status_code': None,
            'error': str(e)
        }


def check_port(host, port, timeout=3):
    """Check if a specific port is open."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


def server_status_cli(args):
    """CLI for web server status checker."""
    if args.check_port:
        host, port = args.target.split(':')
        port = int(port)
        is_open = check_port(host, port)
        status = "OPEN" if is_open else "CLOSED"
        print(f"{args.target}: {status}")
    else:
        result = check_server(args.target, args.timeout)
        print(f"URL: {result['url']}")
        print(f"Status: {result['status']}")
        if result['status_code']:
            print(f"Status Code: {result['status_code']}")
        if result['error']:
            print(f"Error: {result['error']}")


# ========== Main ==========
def main():
    parser = argparse.ArgumentParser(description='Utility Toolkit')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Password generator
    pw_parser = subparsers.add_parser('password', help='Generate secure passwords')
    pw_parser.add_argument('-l', '--length', type=int, default=16, help='Password length')
    pw_parser.add_argument('--no-special', dest='special', action='store_false', help='Exclude special characters')
    pw_parser.add_argument('--no-numbers', dest='numbers', action='store_false', help='Exclude numbers')
    pw_parser.add_argument('--no-uppercase', dest='uppercase', action='store_false', help='Exclude uppercase')
    pw_parser.add_argument('-c', '--count', type=int, help='Generate multiple passwords')
    
    # JSON tool
    json_parser = subparsers.add_parser('json', help='Format or validate JSON')
    json_parser.add_argument('-i', '--input', help='JSON string input')
    json_parser.add_argument('-f', '--file', help='JSON file to process')
    json_parser.add_argument('--validate', action='store_true', help='Validate JSON only')
    json_parser.add_argument('--indent', type=int, default=2, help='Indent spaces')
    json_parser.add_argument('--sort', action='store_true', help='Sort keys')
    
    # CSV to JSON
    csv_parser = subparsers.add_parser('csv2json', help='Convert CSV to JSON')
    csv_parser.add_argument('csv_file', help='Input CSV file')
    csv_parser.add_argument('-o', '--output', help='Output JSON file')
    csv_parser.add_argument('-d', '--delimiter', default=',', help='CSV delimiter')
    csv_parser.add_argument('-e', '--encoding', default='utf-8', help='File encoding')
    
    # Server status
    server_parser = subparsers.add_parser('check', help='Check server status')
    server_parser.add_argument('target', help='URL or host:port to check')
    server_parser.add_argument('-t', '--timeout', type=int, default=5, help='Timeout in seconds')
    server_parser.add_argument('-p', '--check-port', action='store_true', help='Check port instead of HTTP')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        print("\n--- Examples ---")
        print("python utility_toolkit.py password -l 20")
        print("python utility_toolkit.py json -i '{\"a\":1}'")
        print("python utility_toolkit.py csv2json data.csv -o output.json")
        print("python utility_toolkit.py check https://example.com")
        return
    
    if args.command == 'password':
        password_generator_cli(args)
    elif args.command == 'json':
        json_tool_cli(args)
    elif args.command == 'csv2json':
        csv_to_json_cli(args)
    elif args.command == 'check':
        server_status_cli(args)


if __name__ == '__main__':
    main()
