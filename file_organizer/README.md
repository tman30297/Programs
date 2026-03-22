# File Organizer

Automatically sort files into folders by type.

## Usage

```bash
# Organize current directory
python file_organizer.py

# Organize specific directory
python file_organizer.py /path/to/directory

# Preview (dry run)
python file_organizer.py --dry-run

# Undo last organization
python file_organizer.py --undo

# Show history
python file_organizer.py --stats
```

## Categories

| Category | Extensions |
|----------|-----------|
| Images | jpg, png, gif, svg, webp, psd, etc. |
| Videos | mp4, mkv, avi, mov, etc. |
| Audio | mp3, wav, flac, aac, etc. |
| Documents | pdf, doc, docx, xls, txt, md, etc. |
| Archives | zip, rar, 7z, tar, gz |
| Code | py, js, html, css, java, go, rs, etc. |
| Executables | exe, msi, deb, rpm, etc. |
| Design | sketch, fig, xd, indd, etc. |

Notes:
- Stores history in `~/.file_organizer_history.json`
- Handles name collisions automatically
- Prompts for confirmation before moving files
