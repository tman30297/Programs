# Quick Launcher

Spotlight/Alfred-like command launcher.

## Features

- File search (recent + by name)
- Quick calculations
- Web search
- Clipboard history
- Custom shortcuts
- System commands

## Usage

```bash
# Run launcher (interactive)
python quicklauncher.py

# Add shortcut
python quicklauncher.py shortcut add "gh" "cd ~/GitHub"

# Search files
python quicklauncher.py files "report"

# Web search
python quicklauncher.py web "python tutorials"
```

Data stored in `~/.quicklauncher/`
