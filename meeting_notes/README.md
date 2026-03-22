# Meeting Notes

CLI tool for organizing meeting notes.

## Usage

```bash
# Add a note
meeting_notes.py add "Standup" -c "Discussed project timeline" -t standup

# List all notes
meeting_notes.py list

# Filter by tag
meeting_notes.py list -t standup

# Search notes
meeting_notes.py list -s timeline

# View a note
meeting_notes.py view "Standup"

# Delete a note
meeting_notes.py delete "Standup"

# Export to markdown
meeting_notes.py export -o ./notes/
```

## Options

| Command | Description |
|---------|-------------|
| `add` | Add new note |
| `list` | List notes |
| `view` | View note |
| `delete` | Delete note |
| `export` | Export to markdown |

Notes stored in `~/.meeting_notes/` as JSON files.
