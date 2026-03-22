# LinkVault

CLI Bookmark Manager with Tags - store, organize, search, and retrieve bookmarks from the terminal.

## Usage

```bash
# Add a bookmark
python linkvault.py add https://github.com GitHub -t code dev

# List all bookmarks
python linkvault.py list

# Filter by tag
python linkvault.py list -t python

# Search bookmarks
python linkvault.py list -s docker

# Open bookmark in browser
python linkvault.py open 1

# Delete bookmark
python linkvault.py delete 1

# List all tags
python linkvault.py tags

# Export bookmarks
python linkvault.py export bookmarks.json

# Import bookmarks
python linkvault.py import bookmarks.json
```

## Features

- Add bookmarks with title and tags
- Filter by tag or search
- Open bookmarks directly in browser
- Import/export JSON format
- Tracks last accessed time
- Stores data in `~/.linkvault.json`
