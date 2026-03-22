# GPU Monitor

Real-time NVIDIA GPU monitoring.

## Requirements

```bash
pip install nvidia-ml-py3
```

## Usage

```bash
# Single snapshot
python gpu_monitor.py

# Continuous monitoring
python gpu_monitor.py -c

# Update interval
python gpu_monitor.py -c -i 2

# Export to CSV
python gpu_monitor.py -e stats.csv -d 60

# Check GPU availability
python gpu_monitor.py --check
```

## Options

| Flag | Description |
|------|-------------|
| `-c, --continuous` | Continuous monitoring |
| `-i, --interval` | Update interval (default: 1s) |
| `-e, --export` | Export to CSV |
| `-d, --duration` | CSV export duration (default: 60s) |
| `-t, --interval-export` | Export interval |
| `--check` | Check GPU availability |

## Displays

- GPU utilization
- Memory used/total
- Temperature
- Power draw/limit
- Fan speed
