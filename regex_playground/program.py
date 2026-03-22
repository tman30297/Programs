#!/usr/bin/env python3
"""
Regex Playground - A CLI tool for writing, testing, and understanding regular expressions.

Usage:
    regex_playground "pattern" "test string"     - Quick test
    regex_playground --explain "pattern"         - Explain pattern
    regex_playground --interactive               - Interactive mode
    regex_playground --save "name"               - Save current pattern
    regex_playground --load "name"               - Load saved pattern
    regex_playground --list                      - List saved patterns
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

# Try to import colorama for colored output
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLORIZE = True
except ImportError:
    COLORIZE = False
    class Fore:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = ""
    class Style:
        RESET_ALL = BRIGHT = ""

# Storage location for saved patterns
PATTERNS_FILE = Path.home() / ".regex_playground_patterns.json"


class RegexMatcher:
    """Core regex matching engine with support for multiple flavors."""
    
    FLAVORS = {
        "python": "Python (re)",
        "javascript": "JavaScript",
        "pcre": "PCRE (Perl)",
    }
    
    def __init__(self, pattern: str, flavor: str = "python"):
        self.pattern = pattern
        self.flavor = flavor
        self.regex = None
        self.error = None
        self._compile()
    
    def _compile(self):
        """Compile the regex pattern."""
        try:
            self.regex = re.compile(self.pattern)
            self.error = None
        except re.error as e:
            self.error = str(e)
            self.regex = None
    
    def match(self, text: str) -> dict:
        """Perform regex matching and return results."""
        if self.error:
            return {"error": self.error, "matches": []}
        
        matches = []
        for match in self.regex.finditer(text):
            match_info = {
                "match": match.group(),
                "start": match.start(),
                "end": match.end(),
                "groups": {},
                "named_groups": dict(match.groupdict()) if match.groupdict() else {},
            }
            # Add numbered groups
            for i, group in enumerate(match.groups(), 1):
                match_info["groups"][f"group_{i}"] = group
            matches.append(match_info)
        
        return {
            "error": None,
            "matches": matches,
            "match_count": len(matches),
        }
    
    def split(self, text: str) -> list:
        """Split text by regex pattern."""
        if self.error:
            return []
        return self.regex.split(text)
    
    def sub(self, text: str, replacement: str) -> str:
        """Replace pattern matches in text."""
        if self.error:
            return text
        return self.regex.sub(replacement, text)


class PatternExplainer:
    """Human-readable regex pattern breakdown."""
    
    TOKEN_PATTERNS = [
        (r'^\(\?P<(\w+)>', 'Named capture group: '),
        (r'^\((\?:)?', 'Non-capturing group: '),
        (r'^\(\?', 'Special group: '),
        (r'^\(', 'Group start: '),
        (r'^\)', 'Group end: '),
        (r'^\[(\^)?', 'Character class start'),
        (r'^\]', 'Character class end: '),
        (r'^\d+', 'Literal: '),
        (r'^\\d', 'Any digit (0-9)'),
        (r'^\\D', 'Any non-digit'),
        (r'^\\w', 'Word character (a-z, A-Z, 0-9, _)'),
        (r'^\\W', 'Non-word character'),
        (r'^\\s', 'Whitespace'),
        (r'^\\S', 'Non-whitespace'),
        (r'^\\b', 'Word boundary'),
        (r'^\\B', 'Non-word boundary'),
        (r'^\\n', 'Newline'),
        (r'^\\t', 'Tab'),
        (r'^\\.', 'Literal dot'),
        (r'^\\^', 'Literal caret'),
        (r'^\\$', 'Literal dollar'),
        (r'^\\|', 'Literal pipe'),
        (r'^\\\*', 'Literal asterisk'),
        (r'^\\+', 'Literal plus'),
        (r'^\\?', 'Literal question mark'),
        (r'^\\{', 'Literal brace'),
        (r'^\^', 'Start of string/line'),
        (r'^$', 'End of string/line'),
        (r'^\.', 'Any character (except newline)'),
        (r'^\|', 'OR (alternation)'),
        (r'^\*', 'Zero or more (greedy)'),
        (r'^\*\?', 'Zero or more (lazy)'),
        (r'^\+', 'One or more (greedy)'),
        (r'^\+\?', 'One or more (lazy)'),
        (r'^\?', 'Zero or one (optional)'),
        (r'^\{\d+(,\d*)?\}', 'Repetition range'),
        (r'^\{(\d+),\}', 'At least N times'),
        (r'^\{(\d+),(\d+)\}', 'Between N and M times'),
        (r'^.', 'Literal character: '),
    ]
    
    COMMON_PATTERNS = {
        r'\d+': "Matches one or more digits (0-9)",
        r'\d{4}-\d{2}-\d{2}': "Matches a date in YYYY-MM-DD format",
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}': "Matches an IPv4 address",
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}': "Matches an email address",
        r'https?://': "Matches HTTP or HTTPS URL",
        r'\[.*\]': "Matches anything inside square brackets",
        r'<.*>': "Matches anything inside angle brackets",
        r'\".*\"': "Matches a double-quoted string",
        r"'.*'": "Matches a single-quoted string",
        r'\s*': "Matches zero or more whitespace characters",
    }
    
    @classmethod
    def explain(cls, pattern: str) -> str:
        """Explain a regex pattern in plain English."""
        # Check common patterns first (strip anchors for comparison)
        stripped = pattern.lstrip('^').rstrip('$')
        for common, desc in cls.COMMON_PATTERNS.items():
            # Also try matching with anchors stripped from user pattern
            if common in stripped or common in pattern:
                return f"Common pattern: {desc}"
        
        # Tokenize and explain
        tokens = []
        remaining = pattern
        depth = 0
        
        while remaining:
            matched = False
            for regex, description in cls.TOKEN_PATTERNS:
                match = re.match(regex, remaining)
                if match:
                    token_text = match.group()
                    tokens.append(f"{'  ' * depth}{description}`{token_text}`")
                    remaining = remaining[len(token_text):]
                    matched = True
                    
                    if '(' in token_text:
                        depth += 1
                    elif ')' in token_text:
                        depth = max(0, depth - 1)
                    break
            
            if not matched:
                tokens.append(f"{'  ' * depth}Literal: `{remaining[0]}`")
                remaining = remaining[1:]
        
        if not tokens:
            return "Simple literal pattern"
        
        return "Pattern breakdown:\n" + "\n".join(tokens)


class PatternStorage:
    """Manage saved regex patterns."""
    
    def __init__(self, storage_path: Path = PATTERNS_FILE):
        self.storage_path = storage_path
        self.patterns = self._load()
    
    def _load(self) -> dict:
        """Load patterns from storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save(self):
        """Save patterns to storage."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def save(self, name: str, pattern: str, description: str = "", tags: list = None):
        """Save a pattern."""
        self.patterns[name] = {
            "pattern": pattern,
            "description": description,
            "tags": tags or [],
        }
        self._save()
    
    def load(self, name: str) -> Optional[dict]:
        """Load a pattern by name."""
        return self.patterns.get(name)
    
    def delete(self, name: str) -> bool:
        """Delete a pattern."""
        if name in self.patterns:
            del self.patterns[name]
            self._save()
            return True
        return False
    
    def list_all(self) -> dict:
        """List all saved patterns."""
        return self.patterns


def highlight_matches(text: str, matches: list) -> str:
    """Add color highlighting to matched portions."""
    if not matches or not COLORIZE:
        return text
    
    # Sort matches by start position (reverse to replace from end)
    sorted_matches = sorted(matches, key=lambda m: m['start'], reverse=True)
    
    result = text
    for match in sorted_matches:
        start, end = match['start'], match['end']
        matched_text = text[start:end]
        result = result[:start] + Fore.RED + Style.BRIGHT + matched_text + Style.RESET_ALL + result[end:]
    
    return result


def print_matches(text: str, result: dict):
    """Print match results nicely."""
    if result.get("error"):
        print(f"{Fore.RED}Error: {result['error']}{Style.RESET_ALL}")
        return
    
    matches = result["matches"]
    if not matches:
        print(f"{Fore.YELLOW}No matches found{Style.RESET_ALL}")
        return
    
    print(f"{Fore.GREEN}Found {len(matches)} match(es):{Style.RESET_ALL}")
    print()
    
    for i, match in enumerate(matches, 1):
        print(f"  Match {i}: {Fore.CYAN}`{match['match']}`{Style.RESET_ALL}")
        print(f"    Position: {match['start']}-{match['end']}")
        
        if match['named_groups']:
            print(f"    Named groups: {match['named_groups']}")
        
        if match['groups']:
            print(f"    Groups: {match['groups']}")
        print()


def interactive_mode(storage: PatternStorage):
    """Run interactive regex testing mode."""
    print(f"{Fore.CYAN}=== Regex Playground (Interactive Mode) ==={Style.RESET_ALL}")
    print("Commands: :explain, :save <name>, :load <name>, :list, :quit")
    print("Enter pattern and test string when prompted.\n")
    
    current_pattern = ""
    
    while True:
        try:
            pattern = input(f"{Fore.GREEN}Pattern{Style.RESET_ALL} (or :quit): ").strip()
            
            if pattern in (":quit", ":q", "exit"):
                print("Goodbye!")
                break
            
            if not pattern:
                continue
            
            if pattern.startswith(":"):
                cmd = pattern.split()[0]
                args = pattern.split()[1:]
                
                if cmd == ":list":
                    patterns = storage.list_all()
                    if patterns:
                        print(f"{Fore.CYAN}Saved patterns:{Style.RESET_ALL}")
                        for name, data in patterns.items():
                            print(f"  {name}: {data['pattern']}")
                            if data.get('description'):
                                print(f"    {data['description']}")
                    else:
                        print("No saved patterns.")
                    continue
                
                elif cmd == ":load":
                    if not args:
                        print("Usage: :load <name>")
                        continue
                    loaded = storage.load(args[0])
                    if loaded:
                        current_pattern = loaded['pattern']
                        print(f"{Fore.GREEN}Loaded: {current_pattern}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}Pattern not found: {args[0]}{Style.RESET_ALL}")
                    continue
                
                elif cmd == ":save":
                    if not args:
                        print("Usage: :save <name>")
                        continue
                    if current_pattern:
                        storage.save(args[0], current_pattern)
                        print(f"{Fore.GREEN}Saved pattern as '{args[0]}'{Style.RESET_ALL}")
                    else:
                        print("No pattern to save. Enter a pattern first.")
                    continue
                
                elif cmd == ":explain":
                    if current_pattern:
                        explanation = PatternExplainer.explain(current_pattern)
                        print(f"\n{explanation}\n")
                    else:
                        print("No pattern to explain.")
                    continue
                
                else:
                    print(f"Unknown command: {cmd}")
                    continue
            
            current_pattern = pattern
            
            # Get test string
            test_string = input(f"{Fore.GREEN}Test string{Style.RESET_ALL}: ").strip()
            
            # Show highlighted matches
            matcher = RegexMatcher(pattern)
            result = matcher.match(test_string)
            
            print()
            highlighted = highlight_matches(test_string, result.get("matches", []))
            print(f"Highlighted: {highlighted}")
            print()
            
            print_matches(test_string, result)
            
        except KeyboardInterrupt:
            print("\nUse :quit to exit.")
        except EOFError:
            break


def main():
    parser = argparse.ArgumentParser(
        description="Regex Playground - Test and explain regular expressions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  regex_playground "\\d+" "abc123def456"
  regex_playground --explain "^\\d{4}-\\d{2}-\\d{2}$"
  regex_playground --interactive
  regex_playground --save my-date "^\\d{4}-\\d{2}-\\d{2}$"
  regex_playground --load my-date "2024-03-14"
  regex_playground --split "," "a,b,c,d"
  regex_playground --sub "REPLACED" "\\d+" "abc123"
        """
    )
    
    parser.add_argument("pattern", nargs="?", help="Regex pattern")
    parser.add_argument("test_string", nargs="?", help="String to test against")
    
    parser.add_argument("--explain", "-e", metavar="PATTERN", help="Explain a pattern")
    parser.add_argument("--groups", "-g", action="store_true", help="Show captured groups")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--flavor", "-f", default="python", choices=RegexMatcher.FLAVORS.keys(),
                        help="Regex flavor")
    
    parser.add_argument("--save", "-s", metavar="NAME", help="Save pattern with name")
    parser.add_argument("--load", "-l", metavar="NAME", help="Load saved pattern")
    parser.add_argument("--delete", "-d", metavar="NAME", help="Delete saved pattern")
    parser.add_argument("--list", action="store_true", help="List saved patterns")
    
    parser.add_argument("--split", metavar="SEPARATOR", help="Split string by pattern")
    parser.add_argument("--sub", nargs=2, metavar=("REPLACEMENT", "PATTERN"),
                        help="Replace pattern matches")
    
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    storage = PatternStorage()
    
    # Handle list first
    if args.list:
        patterns = storage.list_all()
        if patterns:
            print(f"{Fore.CYAN}Saved patterns:{Style.RESET_ALL}")
            for name, data in patterns.items():
                print(f"  {Fore.GREEN}{name}{Style.RESET_ALL}: {data['pattern']}")
                if data.get('description'):
                    print(f"    {data['description']}")
                if data.get('tags'):
                    print(f"    Tags: {', '.join(data['tags'])}")
        else:
            print("No saved patterns yet.")
        return
    
    # Handle delete
    if args.delete:
        if storage.delete(args.delete):
            print(f"{Fore.GREEN}Deleted pattern: {args.delete}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Pattern not found: {args.delete}{Style.RESET_ALL}")
        return
    
    # Handle interactive mode
    if args.interactive:
        interactive_mode(storage)
        return
    
    # Handle explain
    if args.explain:
        pattern = args.explain
        explanation = PatternExplainer.explain(pattern)
        print(explanation)
        return
    
    # Initialize test_string early to avoid scope issues
    test_string = args.test_string
    
    # Handle load
    # Note: Due to argparse quirk, when using --load, the test string gets captured as pattern
    if args.load:
        loaded = storage.load(args.load)
        if loaded:
            # If no explicit test_string, the test string was captured as positional pattern
            if not test_string and args.pattern:
                test_string = args.pattern
            
            args.pattern = loaded['pattern']
            if loaded.get('description'):
                print(f"{Fore.CYAN}{loaded['description']}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Pattern not found: {args.load}{Style.RESET_ALL}")
            return
    
    # Handle save
    if args.save:
        if not args.pattern:
            print(f"{Fore.RED}No pattern to save{Style.RESET_ALL}")
            return
        storage.save(args.save, args.pattern)
        print(f"{Fore.GREEN}Saved pattern as '{args.save}'{Style.RESET_ALL}")
        return
    
    # Need at least pattern for remaining operations
    if not args.pattern:
        parser.print_help()
        return
    
    # If no test_string yet, check if pattern contains both (space-separated)
    if not test_string and args.pattern and ' ' in args.pattern and not args.load:
        parts = args.pattern.split(' ', 1)
        if len(parts) == 2:
            args.pattern, test_string = parts
    
    matcher = RegexMatcher(args.pattern, args.flavor)
    
    # Handle split
    # Due to argparse quirks with optionals before positionals,
    # when using --split, the string to split may be in args.pattern
    if args.split:
        # String to split is in test_string OR pattern (argparse issue)
        str_to_split = args.test_string or args.pattern
        if not str_to_split:
            print(f"{Fore.RED}No string to split{Style.RESET_ALL}")
            return
            
        # Use pattern if provided, otherwise literal split
        if args.pattern and args.pattern != str_to_split:
            result = matcher.split(str_to_split)
        else:
            result = str_to_split.split(args.split)
            
        print(f"{Fore.CYAN}Split result:{Style.RESET_ALL}")
        for i, part in enumerate(result, 1):
            print(f"  {i}: {repr(part)}")
        return
    
    # Handle sub
    if args.sub:
        replacement, pattern = args.sub
        sub_matcher = RegexMatcher(pattern, args.flavor)
        result = sub_matcher.sub(args.split if args.split else "", replacement)
        print(f"{Fore.CYAN}Result:{Style.RESET_ALL} {result}")
        return
    
    # Basic match operation
    if not test_string:
        # Interactive if no test string provided
        print(f"{Fore.YELLOW}Enter test string (or use --interactive):{Style.RESET_ALL}")
        test_string = input("Test string: ").strip()
    
    if not test_string:
        print(f"{Fore.RED}No test string provided{Style.RESET_ALL}")
        return
    
    result = matcher.match(test_string)
    
    # Show highlighted matches
    highlighted = highlight_matches(test_string, result.get("matches", []))
    print(f"\n{Fore.CYAN}Test string (highlights):{Style.RESET_ALL}")
    print(f"  {highlighted}\n")
    
    print_matches(test_string, result)


if __name__ == "__main__":
    main()
