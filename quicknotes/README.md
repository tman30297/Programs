# Quick Notes

Fast note-taking with tagging and search, stored in SQLite.

## Usage

```bash
# Add a note
python quicknotes.py --add "Meeting notes" "Discussed project timeline" --tags work,meeting

# List all notes
python quicknotes.py --list

# Search notes
python quicknotes.py --search python

# Filter by tag
python quicknotes.py --tag work

# Show note by ID
python quicknotes.py --show 1

# Delete note
python quicknotes.py --delete 1

# List all tags
python quicknotes.py --tags-list
```

## Options

| Flag | Description |
|------|-------------|
| `--add` | Add note (title + content) |
| `--tags` | Tags (comma-separated) |
| `--list` | List all notes |
| `--search` | Search in titles/content |
| `--tag` | Filter by tag |
| `--show` | Show note by ID |
| `--delete` | Delete note by ID |
| `--tags-list` | List all tags |

## Storage

Notes stored in `~/.quicknotes.db` (SQLite)
