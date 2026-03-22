# System Dashboard

Unified view of system metrics in terminal.

## Requirements

```bash
pip install psutil
```

## Usage

```bash
# Show dashboard once
python system_dashboard.py

# Continuous refresh (2 seconds)
python system_dashboard.py -i 2

# Show more processes
python system_dashboard.py -n 10

# No colors
python system_dashboard.py --no-color
```

## Features

- CPU usage (total + per-core)
- Memory + Swap usage
- Disk usage (mounted volumes)
- Network I/O
- Battery status
- Top processes by CPU
- Load average
- System uptime
- Auto-refresh option
