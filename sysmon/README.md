# System Monitor

A CLI tool to monitor system resources.

## Requirements

None (uses built-in Linux filesystems)

## Run

```bash
# Single snapshot
python sysmon.py

# Continuous monitoring
python sysmon.py --watch

# Custom interval (seconds)
python sysmon.py --watch --interval 5
```

## Features

- CPU usage with progress bar
- RAM usage (used/total)
- Disk usage (main drive)
- Drive2 (SSD) usage
- GPU usage (NVIDIA via nvidia-smi)
- Disk I/O (read/write throughput)
