# Bookmarks Manager

Organize, deduplicate, and export browser bookmarks. Supports Chrome, Firefox, Edge, Brave.

## Usage

```bash
# Auto-detect and load all browser bookmarks
python bookmarks_manager.py

# Specific browser
python bookmarks_manager.py --browser chrome

# Show statistics
python bookmarks_manager.py --stats

# List folders
python bookmarks_manager.py --list

# Search bookmarks
python bookmarks_manager.py --search python

# Remove duplicates
python bookmarks_manager.py --dedupe

# Export to HTML
python bookmarks_manager.py --export bookmarks.html
```

## Options

| Flag | Description |
|------|-------------|
| `-b, --browser` | chrome, firefox, edge, brave |
| `-l, --list` | List all folders |
| `-s, --stats` | Show statistics |
| `-q, --search` | Search bookmarks |
| `-d, --dedupe` | Remove duplicates |
| `-e, --export` | Export to file |
| `-f, --format` | html or json |
