# brain_all - Unified Search Tool

> Search Brain, PDFs, and Memory from one command or web GUI

## Overview

`brain_all` is a unified search tool that searches across all your knowledge sources:
- **Brain** - Notes, voice memos, YouTube transcripts
- **PDFs** - Your PDF library (Python, Rust, IoT, etc.)
- **Memory** - Daily log files

## Installation

The script is already installed at:
```
/media/tony/Drive2/Programs/brain_all.py
```

## Usage

### Command Line

```bash
# Basic search (all sources)
python3 /media/tony/Drive2/Programs/brain_all.py "search term"

# Search specific sources
python3 /media/tony/Drive2/Programs/brain_all.py "ESP32" --sources brain
python3 /media/tony/Drive2/Programs/brain_all.py "Python" --sources brain,pdf
python3 /media/tony/Drive2/Programs/brain_all.py "Rust" --sources memory

# Smart search (Brain first, auto-fallback to PDFs)
python3 /media/tony/Drive2/Programs/brain_all.py "async" --smart

# AI summary of results
python3 /media/tony/Drive2/Programs/brain_all.py "Python async" --summarize

# Limit results
python3 /media/tony/Drive2/Programs/brain_all.py "ESP32" --limit 3

# Output as JSON
python3 /media/tony/Drive2/Programs/brain_all.py "python" --json
```

### Web GUI

```bash
python3 /media/tony/Drive2/Programs/brain_all.py --gui
```

Then open in browser:
- **Local:** http://localhost:8768/brain_all_gui.html

The GUI has:
- Search box
- Options: Smart Search, AI Summary
- Checkboxes: Brain, PDFs, Memory
- Dark theme UI

## Options

| Option | Description |
|--------|-------------|
| `query` | Search term (required) |
| `--sources` | Comma-separated: brain,pdf,memory (default: all) |
| `--smart` | Brain first, fallback to PDFs if no results |
| `--summarize` | Get AI summary of results |
| `--limit N` | Max results per source (default: 5) |
| `--gui` | Launch web GUI |
| `--json` | Output as JSON |

## Features

### 1. Parallel Search
Searches all sources simultaneously and returns merged results.

### 2. Smart Search
- First searches Brain (notes, transcripts)
- If no results, automatically searches PDFs
- Useful for broad topics

### 3. AI Summary
- Uses Brain's AI to summarize all results
- Provides quick overview without reading everything

### 4. Web GUI
- User-friendly interface
- Toggle sources on/off
- Dark theme
- Works on phone/desktop

## What It Searches

### Brain
- Notes in `/media/tony/Drive2/Brain/notes/`
- Transcripts in `/media/tony/Drive2/Brain/transcripts/`
- Uses QMD for semantic search

### PDFs
- `/media/tony/Drive2/python3/` - Python books
- `/media/tony/Drive2/Rust/` - Rust books
- `/media/tony/Drive2/IOT/` - IoT/ESP32/Arduino
- `/media/tony/Drive2/Full_Stack_Dev/` - Web dev
- `/media/tony/Drive2/Robot_OS/` - Robotics
- `/media/tony/Drive2/Android/` - Android

### Memory
- Daily logs in `/home/tony/.openclaw/workspace/memory/`
- Uses grep for keyword search

## Architecture

```
brain_all.py
├── search_brain()     - Calls brain.py multi
├── search_pdfs()      - Calls pdf_search.py
├── search_memory()    - Greps memory files
├── smart_search()     - Brain → PDF fallback
├── summarize_results() - AI summary via brain.py chat
└── run_gui()         - Web server + HTML UI
```

## Adding as Alias

Add to `~/.bashrc` for easier access:
```bash
alias brain-all="python3 /media/tony/Drive2/Programs/brain_all.py"
alias brain-gui="python3 /media/tony/Drive2/Programs/brain_all.py --gui"
```

Then run:
```bash
brain-all "ESP32"
brain-gui
```

## Examples

```bash
# Find everything about ESP32
brain-all "ESP32"

# Research Python async
brain-all "Python async" --summarize

# Quick check
brain-all "Arduino"

# Just PDFs
brain-all "Kubernetes" --sources pdf
```

## Troubleshooting

### Port in use
If port 8768 is already in use, the script will fail. You can:
1. Kill existing process: `pkill -f brain_all.py`
2. Or edit the port in the script (change `port = 8768`)

### No results
- Check the search term spelling
- Try different keywords
- Make sure sources are checked

### GUI not loading
- Try a different port in the script
- Check firewall settings

## Future Enhancements

- [ ] Unified web UI combining all tools
- [ ] Auto-research cron job
- [ ] Knowledge graph + PDF links
- [ ] Mobile-friendly UI

## Created

- **Date:** 2026-03-18
- **By:** Bob (AI Assistant)
- **For:** Tony
- **Part of:** Cross-Tool Integration Project

## See Also

- [Cross-Tool Integration Doc](../Other/cross_tool_integration.md)
- [Brain Documentation](../Programs/brain/README.md)
- [PDF Search](../Programs/pdf_search/README.md)
