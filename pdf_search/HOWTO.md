# PDF Text Search Tool

A CLI tool that searches for keywords across multiple PDF files and shows which documents contain the search term and on which pages.

## Installation

No installation needed - just run the Python script directly.

However, you need the `pypdf` library:
```bash
pip install pypdf
```

Or the script will attempt to install it automatically on first run.

## Usage

```bash
python pdf_search.py <search_term> [directory] [options]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `search_term` | **Required.** The text string to search for |
| `directory` | **Optional.** Directory to search (default: `/media/tony/Drive2/python3/`) |

### Options

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Show detailed progress and errors |

## Examples

### Basic search in default directory
```bash
python pdf_search.py "python"
```

### Search in a specific directory
```bash
python pdf_search.py "class" /media/tony/Drive2/Rust/
```

### Verbose mode (shows progress)
```bash
python pdf_search.py "import" --verbose
```

### Search for a specific term
```bash
python pdf_search.py "def " /media/tony/Drive2/python3/
```

## Output Format

```
Found 'python' in 3 PDF(s):

Found in: python_crash_course.pdf
  Page 5, 12, 23 - (3 matches)

Found in: fluent_python.pdf
  Page 1, 8 - (2 matches)
```

## Features

- **Recursive search** - Finds PDFs in all subdirectories
- **Case-insensitive** - Searches regardless of capitalization
- **Page tracking** - Shows exactly which pages contain the term
- **Match counting** - Displays total matches per file
- **Sorted results** - Files with most matches appear first
- **Error handling** - Gracefully handles corrupted PDFs and permission issues

## Making it Executable (Optional)

```bash
chmod +x pdf_search.py
./pdf_search.py "search term"
```

Or add a symlink to your PATH:

```bash
ln -s /media/tony/Drive2/Programs/pdf_search/pdf_search.py ~/bin/pdf_search
```
