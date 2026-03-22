#!/usr/bin/env python3
"""
Password Generator - Generate secure random passwords
Usage: python password_gen.py [-l LENGTH] [-c] [-n] [-s] [-q]
Options:
  -l, --length    Password length (default: 16)
  -c, --caps      Include uppercase letters (default: yes)
  -n, --numbers   Include numbers (default: yes)
  -s, --symbols   Include special symbols (default: yes)
  -q, --quiet     Quiet mode - only output password
  -h, --help      Show this help message
"""

import argparse
import secrets
import string
import sys

try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False

def generate_password(length=16, use_caps=True, use_numbers=True, use_symbols=True):
    """Generate a secure random password."""
    chars = string.ascii_lowercase  # Always include lowercase
    
    if use_caps:
        chars += string.ascii_uppercase
    if use_numbers:
        chars += string.digits
    if use_symbols:
        chars += string.punctuation
    
    # Ensure at least one character from each selected category
    password = []
    if use_caps:
        password.append(secrets.choice(string.ascii_uppercase))
    if use_numbers:
        password.append(secrets.choice(string.digits))
    if use_symbols:
        password.append(secrets.choice(string.punctuation))
    
    # Fill the rest randomly using cryptographically secure random
    while len(password) < length:
        password.append(secrets.choice(chars))
    
    # Shuffle to avoid predictable positions (using secure random)
    # Convert to list for shuffle, then back
    secure_shuffled = list(password)
    # Fisher-Yates shuffle with secrets
    for i in range(len(secure_shuffled) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        secure_shuffled[i], secure_shuffled[j] = secure_shuffled[j], secure_shuffled[i]
    
    return ''.join(secure_shuffled)

def main():
    parser = argparse.ArgumentParser(description='Generate secure random passwords')
    parser.add_argument('-l', '--length', type=int, default=16, help='Password length (default: 16)')
    parser.add_argument('-c', '--caps', action='store_true', default=True, help='Include uppercase letters')
    parser.add_argument('-n', '--numbers', action='store_true', default=True, help='Include numbers')
    parser.add_argument('-s', '--symbols', action='store_true', default=True, help='Include special symbols')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode - only output password')
    parser.add_argument('--no-caps', action='store_false', dest='caps', help='Exclude uppercase letters')
    parser.add_argument('--no-numbers', action='store_false', dest='numbers', help='Exclude numbers')
    parser.add_argument('--no-symbols', action='store_false', dest='symbols', help='Exclude special symbols')
    parser.add_argument('--copy', action='store_true', help='Copy password to clipboard')
    
    args = parser.parse_args()
    
    # Validate length
    if args.length < 4:
        print("Error: Password length must be at least 4", file=sys.stderr)
        sys.exit(1)
    
    password = generate_password(
        length=args.length,
        use_caps=args.caps,
        use_numbers=args.numbers,
        use_symbols=args.symbols
    )
    
    if args.quiet:
        print(password)
    else:
        print(f"🔐 Generated password ({len(password)} chars): {password}")
    
    # Copy to clipboard if requested
    if args.copy and HAS_PYPERCLIP:
        try:
            pyperclip.copy(password)
            print("✓ Copied to clipboard!")
        except Exception:
            print("⚠ Could not copy to clipboard")
    elif args.copy:
        print("⚠ pyperclip not installed - run: pip install pyperclip")
    
    return password

if __name__ == '__main__':
    main()
