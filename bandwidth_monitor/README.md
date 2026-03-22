# Bandwidth Monitor

A command-line tool for monitoring network interface bandwidth usage in real-time.

## Description

Network Bandwidth Monitor tracks network traffic on system interfaces by reading from `/proc/net/dev`. It displays RX (receive) and TX (transmit) rates, helping you monitor network usage across all interfaces or a specific one.

## Usage

```bash
# Monitor all interfaces (one-time)
python bandwidth_monitor.py

# Monitor a specific interface
python bandwidth_monitor.py eth0

# Watch mode (continuous monitoring)
python bandwidth_monitor.py -w

# Custom interval (in seconds)
python bandwidth_monitor.py -w -i 5

# Combine options
python bandwidth_monitor.py wlan0 -w -i 3
```

### Options

| Option | Description |
|--------|-------------|
| `interface` | Network interface to monitor (e.g., eth0, wlan0) |
| `-w, --watch` | Continuous monitoring mode |
| `-i, --interval` | Update interval in seconds (default: 2) |

## Requirements

- Python 3.x
- Linux operating system (uses `/proc/net/dev`)
- No external dependencies (uses standard library only)
