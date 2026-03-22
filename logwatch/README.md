# Log Watch

Real-time log file monitor with filtering and colorization.

## Usage

```bash
# Watch a log file
logwatch.py /var/log/syslog

# Filter by pattern
logwatch.py /var/log/syslog --pattern ERROR

# Grep-like filter
logwatch.py /var/log/syslog --grep "failed"

# Show last N lines first
logwatch.py /var/log/syslog --lines 50
```

## Features

- Real-time tail
- Pattern filtering
- Color-coded log levels
- ANSI color support (--no-color to disable)
