# System Monitor

Real-time CPU, Memory, Disk, and GPU monitoring.

## Requirements

```bash
pip install psutil
```

## Usage

```bash
# Single snapshot
python system_monitor.py

# Continuous monitoring
python system_monitor.py --interval 2

# Include GPU stats
python system_monitor.py --gpu
```

## Displays

- CPU usage
- Memory usage
- Disk usage
- GPU stats (if NVIDIA)
