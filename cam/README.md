# Command Alias Manager (CAM)

Define powerful shell aliases with variable placeholders.

## Usage

```bash
# Interactive menu
cam

# List aliases
cam list

# Add alias
cam add mygit "git commit -m {message}"

# Run alias
cam run mygit --message "Fixed bug"

# Edit alias
cam edit mygit

# Delete alias
cam delete mygit

# Search
cam search git

# Export/Import
cam export aliases.json
cam import aliases.json
```

## Features

- Aliases with `{variable}` placeholders
- Prompts for variable values at runtime
- Command-line args support: `--var value`
- Categories for organization
- Usage history
- Import/export JSON
