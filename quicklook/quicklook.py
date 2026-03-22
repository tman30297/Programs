#!/usr/bin/env python3
"""
QuickLook - Unified lookup tool
Combines dictionary, Wikipedia, unit conversion, calculations, and weather in one CLI.
"""

import argparse
import json
import re
import subprocess
import sys
import urllib.parse
from datetime import datetime

# Try importing optional dependencies
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from currency_converter import CurrencyConverter
    HAS_CURRENCY = True
except ImportError:
    HAS_CURRENCY = False

# File to store history
HISTORY_FILE = "~/.quicklook_history"

# Color codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def log_history(query, result_type):
    """Save query to history."""
    try:
        history_path = HISTORY_FILE.replace("~", subprocess.run(["sh", "-c", "echo $HOME"], capture_output=True, text=True).stdout.strip())
        with open(history_path, "a") as f:
            f.write(f"{datetime.now().isoformat()} | {result_type} | {query}\n")
    except:
        pass


def fetch_json(url, headers=None):
    """Fetch JSON from URL."""
    if not HAS_REQUESTS:
        print(f"{YELLOW}requests library needed. Install: pip install requests{RESET}")
        return None
    try:
        if headers is None:
            headers = {"User-Agent": "QuickLook/1.0 (CLI tool)"}
        elif "User-Agent" not in headers:
            headers["User-Agent"] = "QuickLook/1.0 (CLI tool)"
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"{YELLOW}Error: {e}{RESET}")
        return None


def dictionary_lookup(word):
    """Look up word in dictionary (Free Dictionary API)."""
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{urllib.parse.quote(word)}"
    data = fetch_json(url)
    
    if not data:
        return False
    
    if isinstance(data, list) and len(data) > 0:
        entry = data[0]
        print(f"\n{BOLD}{GREEN}📖 {word.upper()}{RESET}")
        if entry.get("phonetic"):
            print(f"  {entry['phonetic']}")
        
        for meaning in entry.get("meanings", [])[:2]:
            part_of_speech = meaning.get("partOfSpeech", "")
            print(f"\n  {BOLD}({part_of_speech}){RESET}")
            for i, definition in enumerate(meaning.get("definitions", [])[:2], 1):
                print(f"    {i}. {definition.get('definition', '')}")
                if definition.get("example"):
                    print(f"       {YELLOW}\"{definition['example']}\"{RESET}")
        
        log_history(word, "dictionary")
        return True
    return False


def wikipedia_lookup(topic):
    """Look up topic on Wikipedia."""
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(topic)}"
    data = fetch_json(url)
    
    if not data:
        return False
    
    if data.get("title"):
        print(f"\n{BOLD}{BLUE}📚 {data['title']}{RESET}")
        if data.get("description"):
            print(f"  {data['description']}")
        print(f"\n  {data.get('extract', 'No summary available.')}")
        
        if data.get("content_urls"):
            print(f"\n  {CYAN}🔗 {data['content_urls']['desktop']['page']}{RESET}")
        
        log_history(topic, "wikipedia")
        return True
    return False


def unit_convert(value, from_unit, to_unit):
    """Convert units using built-in conversions."""
    # Common conversions
    conversions = {
        # Length
        ("m", "km"): 0.001,
        ("km", "m"): 1000,
        ("m", "mi"): 0.000621371,
        ("mi", "m"): 1609.34,
        ("m", "ft"): 3.28084,
        ("ft", "m"): 0.3048,
        ("m", "yd"): 1.09361,
        ("yd", "m"): 0.9144,
        ("cm", "in"): 0.393701,
        ("in", "cm"): 2.54,
        ("km", "mi"): 0.621371,
        ("mi", "km"): 1.60934,
        # Weight
        ("kg", "lb"): 2.20462,
        ("lb", "kg"): 0.453592,
        ("g", "oz"): 0.035274,
        ("oz", "g"): 28.3495,
        ("kg", "g"): 1000,
        ("g", "kg"): 0.001,
        # Temperature (special handling)
        ("c", "f"): lambda c: c * 9/5 + 32,
        ("f", "c"): lambda f: (f - 32) * 5/9,
        ("c", "k"): lambda c: c + 273.15,
        ("k", "c"): lambda k: k - 273.15,
        # Volume
        ("l", "gal"): 0.264172,
        ("gal", "l"): 3.78541,
        ("ml", "oz"): 0.033814,
        ("oz", "ml"): 29.5735,
        # Data
        ("kb", "mb"): 0.001,
        ("mb", "kb"): 1000,
        ("mb", "gb"): 0.001,
        ("gb", "mb"): 1000,
        ("gb", "tb"): 0.001,
        ("tb", "gb"): 1000,
        ("b", "kb"): 0.001,
        ("kb", "b"): 1000,
        # Time
        ("sec", "min"): 1/60,
        ("min", "sec"): 60,
        ("min", "hr"): 1/60,
        ("hr", "min"): 60,
        ("hr", "day"): 1/24,
        ("day", "hr"): 24,
    }
    
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    
    # Try direct conversion
    key = (from_unit, to_unit)
    if key in conversions:
        factor = conversions[key]
        if callable(factor):
            result = factor(float(value))
        else:
            result = float(value) * factor
        print(f"\n{GREEN}💱 {value} {from_unit} = {result:.4f} {to_unit}{RESET}")
        log_history(f"{value} {from_unit} to {to_unit}", "conversion")
        return True
    
    # Try reverse conversion
    rev_key = (to_unit, from_unit)
    if rev_key in conversions:
        factor = conversions[rev_key]
        if callable(factor):
            result = factor(float(value))
        else:
            result = float(value) / factor
        print(f"\n{GREEN}💱 {value} {from_unit} = {result:.4f} {to_unit}{RESET}")
        log_history(f"{value} {from_unit} to {to_unit}", "conversion")
        return True
    
    return False


def calculate(expr):
    """Evaluate a math expression safely."""
    # Only allow safe characters
    if not re.match(r'^[\d\s\+\-\*\/\.\(\)\%\^\[\]]+$', expr):
        print(f"{YELLOW}Invalid characters in expression{RESET}")
        return False
    
    try:
        # Use eval with some math functions
        allowed = {
            'abs': abs, 'round': round, 'min': min, 'max': max,
            'pow': pow, 'sqrt': lambda x: x**0.5
        }
        result = eval(expr, {"__builtins__": {}}, allowed)
        
        if isinstance(result, float):
            if result.is_integer():
                result = int(result)
            else:
                result = round(result, 10)
        
        print(f"\n{GREEN}🔢 {expr} = {BOLD}{result}{RESET}")
        log_history(expr, "calc")
        return True
    except Exception as e:
        print(f"{YELLOW}Error: {e}{RESET}")
        return False


def get_weather(location):
    """Get weather using wttr.in (no API key needed)."""
    if not HAS_REQUESTS:
        # Fall back to curl
        try:
            result = subprocess.run(
                ["curl", "-s", f"wttr.in/{urllib.parse.quote(location)}?format=j1"],
                capture_output=True, text=True, timeout=10
            )
            data = json.loads(result.stdout)
        except Exception as e:
            print(f"{YELLOW}Error fetching weather: {e}{RESET}")
            return False
    else:
        url = f"https://wttr.in/{urllib.parse.quote(location)}?format=j1"
        data = fetch_json(url)
    
    if not data or "current_condition" not in data:
        print(f"{YELLOW}Could not get weather for '{location}'{RESET}")
        return False
    
    current = data["current_condition"][0]
    
    print(f"\n{BOLD}{BLUE}🌤️ Weather in {location.title()}{RESET}")
    print(f"  {BOLD}Temperature:{RESET} {current['temp_C']}°C ({current['temp_F']}°F)")
    print(f"  {BOLD}Condition:{RESET} {current['weatherDesc'][0]['value']}")
    print(f"  {BOLD}Humidity:{RESET} {current['humidity']}%")
    print(f"  {BOLD}Wind:{RESET} {current['windspeedKmph']} km/h")
    
    if data.get("weather"):
        today = data["weather"][0]
        print(f"  {BOLD}Chance of rain:{RESET} {today.get('chanceofrain', 'N/A')}%")
    
    log_history(location, "weather")
    return True


def show_help():
    """Show help message."""
    help_text = f"""
{BOLD}QuickLook - Unified Lookup Tool{RESET}

{BOLD}Usage:{RESET}
  quicklook <query>

{BOLD}Examples:{RESET}
  quicklook <word>              # Dictionary lookup
  quicklook wikipedia <topic>   # Wikipedia summary
  quicklook convert <value> <from> <to>  # Unit conversion
  quicklook calc <expression>  # Calculator
  quicklook weather <location> # Weather

{BOLD}Unit Conversion Examples:{RESET}
  convert 100 km to mi
  convert 50 kg to lb
  convert 72 f to c
  convert 500 mb to gb

{BOLD}Built-in Commands:{RESET}
  quicklook history             # Show recent lookups
  quicklook help                # This help

{BOLD}Supported Units:{RESET}
  Length: m, km, mi, ft, yd, cm, in
  Weight: kg, lb, g, oz
  Volume: l, gal, ml, oz
  Data: b, kb, mb, gb, tb
  Time: sec, min, hr, day
  Temperature: c, f, k

{GREEN}Install requests for better weather: pip install requests{RESET}
"""
    print(help_text)


def show_history():
    """Show lookup history."""
    try:
        history_path = HISTORY_FILE.replace("~", subprocess.run(["sh", "-c", "echo $HOME"], capture_output=True, text=True).stdout.strip())
        with open(history_path, "r") as f:
            lines = f.readlines()[-20:][::-1]  # Last 20, reversed
            if lines:
                print(f"\n{BOLD}Recent Lookups:{RESET}")
                for line in lines:
                    parts = line.strip().split(" | ")
                    if len(parts) >= 3:
                        print(f"  {parts[1]:12} | {parts[2]}")
            else:
                print(f"{YELLOW}No history yet.{RESET}")
    except FileNotFoundError:
        print(f"{YELLOW}No history yet.{RESET}")
    except Exception as e:
        print(f"{YELLOW}Error: {e}{RESET}")


def parse_query(args):
    """Parse the query and route to appropriate handler."""
    if not args or "-h" in args or "--help" in args:
        show_help()
        return
    
    if args[0] in ["history", "--history", "-history"]:
        show_history()
        return
    
    # Check for commands
    if args[0] == "wiki" or args[0] == "wikipedia":
        if len(args) < 2:
            print(f"{YELLOW}Usage: quicklook wikipedia <topic>{RESET}")
            return
        wikipedia_lookup(" ".join(args[1:]))
        return
    
    if args[0] == "convert" or args[0] == "to":
        # Parse: convert 100 km to mi
        if len(args) < 4:
            print(f"{YELLOW}Usage: convert <value> <from_unit> to <to_unit>{RESET}")
            return
        
        try:
            value = float(args[1])
            from_unit = args[2]
            
            # Handle "to" keyword
            if args[3].lower() == "to":
                to_unit = args[4]
            else:
                to_unit = args[3]
            
            if not unit_convert(value, from_unit, to_unit):
                print(f"{YELLOW}Unknown conversion. Check units.{RESET}")
        except ValueError:
            print(f"{YELLOW}Invalid number: {args[1]}{RESET}")
        return
    
    if args[0] == "calc" or args[0] == "=":
        expr = " ".join(args[1:]) if args[0] == "calc" else " ".join(args)
        calculate(expr)
        return
    
    if args[0] == "weather" or args[0] == "temp":
        if len(args) < 2:
            print(f"{YELLOW}Usage: quicklook weather <location>{RESET}")
            return
        get_weather(" ".join(args[1:]))
        return
    
    # Default: dictionary lookup
    word = " ".join(args)
    if not dictionary_lookup(word):
        # Try Wikipedia as fallback
        print(f"{YELLOW}Not found in dictionary, trying Wikipedia...{RESET}")
        if not wikipedia_lookup(word):
            print(f"{YELLOW}No results found for '{word}'{RESET}")


def main():
    parser = argparse.ArgumentParser(description="QuickLook - Unified lookup tool", add_help=False)
    parser.add_argument("query", nargs="*", help="Query to look up")
    args = parser.parse_args()
    
    parse_query(args.query)


if __name__ == "__main__":
    main()
