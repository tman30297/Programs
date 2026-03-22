# Daily Briefing

CLI dashboard with weather, system info, and utilities.

## Requirements

```bash
pip install requests psutil
```

## Usage

```bash
# Full briefing
python daily_briefing.py --all

# Weather only
python daily_briefing.py --weather

# System info only
python daily_briefing.py --system
```

## Features

- Weather via wttr.in
- System status (CPU, memory, disk)
- Date/time
- Quick utilities
