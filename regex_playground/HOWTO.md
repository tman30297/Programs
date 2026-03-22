# Regex Playground

A powerful CLI tool for writing, testing, and understanding regular expressions.

## Installation

```bash
pip install colorama
# Optional: for better regex support
pip install regex
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

```bash
# Basic matching
python program.py "\d+" "abc123def456"

# Explain a pattern
python program.py --explain "^\d{4}-\d{2}-\d{2}$"

# Interactive mode
python program.py --interactive
```

## Usage

### Quick Test
```bash
python program.py "pattern" "test string"
```

### Explain Pattern
```bash
python program.py --explain "^(https?://)?(www\.)?([a-zA-Z0-9]+)\."
```
Output:
```
Common pattern: Matches HTTP or HTTPS URL
```

### Interactive Mode
```bash
python program.py --interactive
```
This opens an interactive shell where you can:
- Enter patterns and test strings
- Use `:explain` to explain current pattern
- Use `:save mypattern` to save current pattern
- Use `:load mypattern` to load a saved pattern
- Use `:list` to see all saved patterns
- Use `:quit` to exit

### Save & Load Patterns
```bash
# Save a pattern
python program.py --save my-date "\d{4}-\d{2}-\d{2}"

# Load and test a pattern
python program.py --load my-date "2024-03-14"
```

### Split by Pattern
```bash
python program.py --split "," "a,b,c,d"
```

### Find and Replace
```bash
python program.py --sub "NUMBER" "\d+" "abc123def"
# Output: abcNUMBERdef
```

### List Saved Patterns
```bash
python program.py --list
```

### Delete Saved Pattern
```bash
python program.py --delete my-date
```

## Features

- **Real-time matching** - See matches instantly
- **Visual highlighting** - Color-coded match display (requires colorama)
- **Pattern explanation** - Human-readable breakdown of complex patterns
- **Named groups** - Extract named capture groups
- **Multiple flavors** - Support for Python, JavaScript, PCRE regex
- **Pattern library** - Save and reuse your favorite patterns

## Examples

### Email Validation
```bash
python program.py "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$" "user@example.com"
```

### Date Extraction
```bash
python program.py "\d{4}-\d{2}-\d{2}" "Meeting on 2024-03-14 and 2024-04-01"
```

### URL Parsing
```bash
python program.py "https?://[^\s]+" "Visit https://example.com today!"
```

### Phone Numbers
```bash
python program.py "\b\d{3}[-.]?\d{3}[-.]?\d{4}\b" "Call 555-123-4567 or 555.123.4567"
```

## Configuration

Patterns are saved to `~/.regex_playground_patterns.json`

## Requirements

- Python 3.7+
- colorama (optional, for colored output)
- regex (optional, for advanced regex features)
