# System Cleanup

Cleans temporary files, caches, and helps free up disk space.

## Features

- **Temp files** - Cleans `/tmp`, `~/.cache`, files older than 24 hours
- **Browser cache** - Chrome, Firefox, Edge cache cleanup
- **Python cache** - Removes `__pycache__`, `.pyc`, `.pyo` files
- **Log files** - Cleans old `.log` files (configurable age)
- **Downloads** - Removes old installers from Downloads folder
- **Thumbnails** - Clears thumbnail cache

## Usage

```bash
# Preview what would be cleaned (dry run)
python system_cleanup.py --dry-run

# Clean temp files and browser cache
python system_cleanup.py --temp --browser

# Clean everything
python system_cleanup.py --all

# Show disk usage
python system_cleanup.py --size

# Clean logs older than 14 days
python system_cleanup.py --logs --older-than 14
```

## Options

| Flag | Description |
|------|-------------|
| `-n, --dry-run` | Preview without deleting |
| `-t, --temp` | Clean temp files |
| `-b, --browser` | Clean browser cache |
| `-p, --python` | Clean Python cache |
| `-l, --logs` | Clean old log files |
| `-d, --downloads` | Clean Downloads folder |
| `--thumbnails` | Clean thumbnail cache |
| `-a, --all` | Clean everything |
| `-s, --show-size` | Show disk usage |
| `--older-than N` | Delete files older than N days (default: 7) |
