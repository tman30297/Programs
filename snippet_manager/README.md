# Snippet Manager

CLI tool to store, search, and retrieve code snippets.

## Requirements

```bash
pip install pyperclip
```

## Usage

```bash
# Add snippet
snippet_manager.py add "git undo" "git reset --soft HEAD~1" -t git -l bash

# List snippets
snippet_manager.py list

# Filter by tag
snippet_manager.py list -t git

# Show snippet
snippet_manager.py show 1

# Copy to clipboard
snippet_manager.py copy 1

# Search
snippet_manager.py search docker

# Delete
snippet_manager.py delete 1
```

## Options

| Command | Description |
|---------|-------------|
| `add` | Add snippet |
| `list` | List snippets |
| `show` | Show content |
| `copy` | Copy to clipboard |
| `delete` | Delete snippet |
| `search` | Search snippets |
| `edit` | Edit snippet |

Data stored in `~/.quicksnip/snippets.json`
