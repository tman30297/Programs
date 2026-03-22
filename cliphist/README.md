# ClipHist - Clipboard History Manager

A simple CLI tool to save, search, and manage your clipboard history.

## Installation

```bash
# Add to your PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$PATH:/media/tony/Drive2/Programs/cliphist"

# Or create symlink
sudo ln -s /media/tony/Drive2/Programs/cliphist/cliphist.py /usr/local/bin/cliphist
```

## Usage

```bash
# Show recent history
cliphist

# Add text to history
cliphist add "Important text to save"

# List history (20 most recent)
cliphist list

# Search history
cliphist list --search github

# Copy entry back to clipboard (requires pyperclip)
cliphist copy 1
pip install pyperclip  # Install for clipboard functionality

# Clear all history
cliphist clear
```

## Features

- Saves clipboard history to `~/.cliphist/history.json`
- Deduplication (won't add same text twice in a row)
- Search through history
- Up to 1000 entries stored
- Timestamps on all entries

## Optional: Auto-capture clipboard

Add to your shell config to auto-save clipboard selections:

```bash
# In ~/.bashrc or ~/.zshrc
cliphist() {
    if [ $# -eq 0 ]; then
        python3 /media/tony/Drive2/Programs/cliphist/cliphist.py "$@"
    else
        case "$1" in
            add) python3 /media/tony/Drive2/Programs/cliphist/cliphist.py "$@";;
            copy) python3 /media/tony/Drive2/Programs/cliphist/cliphist.py "$@";;
            clear) python3 /media/tony/Drive2/Programs/cliphist/cliphist.py "$@";;
            list|--search|-s|-n) python3 /media/tony/Drive2/Programs/cliphist/cliphist.py "$@";;
            *) python3 /media/tony/Drive2/Programs/cliphist/cliphist.py add "$1";;
        esac
    fi
}
```

## Requirements

- Python 3.6+
- pyperclip (optional, for copy-to-clipboard feature)
