# Clipboard Manager

Store, search, and manage clipboard history.

## Requirements

```bash
pip install pyperclip
```

## Usage

```bash
# Save current clipboard
clipboard_manager.py save

# List history
clipboard_manager.py list

# Search
clipboard_manager.py search "term"

# Copy from history
clipboard_manager.py copy 1

# Favorite a clip
clipboard_manager.py fav 1

# Delete
clipboard_manager.py delete 1

# Clear all
clipboard_manager.py clear
```

## Features

- Saves clipboard to SQLite
- Search history
- Favorites
- Re-copy from history

Data stored in `~/.clipboard_manager.db`
