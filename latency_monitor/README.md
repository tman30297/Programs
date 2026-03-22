# Latency Monitor

A command-line tool for monitoring network latency to hosts over time using ping.

## Description

Network Latency Monitor pings target hosts and tracks latency statistics including min, max, average, median, and packet loss. Supports both single checks and continuous watch mode with optional file logging.

## Usage

```bash
# Single ping check
python latency_monitor.py 8.8.8.8

# Watch mode (continuous monitoring)
python latency_monitor.py google.com -w

# Custom number of pings per check
python latency_monitor.py 192.168.1.1 -c 10

# Custom interval between checks
python latency_monitor.py 8.8.8.8 -w -i 5

# Save results to file
python latency_monitor.py google.com -w -o results.txt
```

### Options

| Option | Description |
|--------|-------------|
| `host` | Target host or IP address (required) |
| `-c, --count` | Number of pings per check (default: 4) |
| `-w, --watch` | Continuous monitoring mode |
| `-i, --interval` | Interval between checks in watch mode (default: 3s) |
| `-t, --timeout` | Ping timeout in seconds (default: 2) |
| `-o, --output` | Save results to file |

## Requirements

- Python 3.x
- `ping` command-line tool (installed by default on most systems)
- No additional Python dependencies (uses standard library only)
