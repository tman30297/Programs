# 🔗 LinkVault - CLI Bookmark Manager

A command-line bookmark manager with tagging, search, and export/import capabilities.

## Features

- 📥 Add bookmarks with title and tags
- 🏷️ Tag-based organization
- 🔍 Search through titles, URLs, and tags
- 🌐 Open bookmarks directly in your browser
- 📤 Export/import bookmarks (JSON format)
- 💾 Persistent storage in `~/.linkvault.json`

## Usage

```bash
# Add a bookmark
linkvault add <url> <title> -t tag1 tag2 tag3

# List all bookmarks
linkvault list

# Filter by tag
linkvault list -t <tag>

# Search bookmarks
linkvault list -s <search_term>

# Open bookmark in browser
linkvault open <id>

# Delete a bookmark
linkvault delete <id>

# List all tags
linkvault tags

# Export bookmarks
linkvault export bookmarks.json

# Import bookmarks
linkvault import bookmarks.json
```

## Examples

```bash
# Add a bookmark with tags
linkvault add https://github.com "GitHub" -t code dev tools

# Find all code-related bookmarks
linkvault list -t code

# Search for "python"
linkvault list -s python

# Open bookmark #1 in browser
linkvault open 1
```

## Data Location

Bookmarks are stored in `~/.linkvault.json`
