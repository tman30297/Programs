# Quick Port Scanner

A lightweight, fast port scanner written in Python using socket and concurrent.futures for parallel scanning.

## What It Does

- Scans target IP addresses or hostnames for open ports
- Supports scanning common ports, specific ports, port ranges, or all 65535 ports
- Uses multithreading for fast parallel scanning
- Identifies common services by port number
- Configurable timeout and thread count

## How to Run

```bash
cd /media/tony/Drive2/Programs/port_scanner
python quick_port_scanner.py <target> [options]
```

### Examples

```bash
# Scan common ports on localhost
python quick_port_scanner.py 127.0.0.1

# Scan specific ports
python quick_port_scanner.py 192.168.1.1 -p 80,443,8080

# Scan a port range
python quick_port_scanner.py 192.168.1.1 -r 1-1000

# Scan all ports (slow)
python quick_port_scanner.py 192.168.1.1 --all

# More threads for faster scanning
python quick_port_scanner.py 192.168.1.1 -t 100 --timeout 0.5
```

## Requirements

- Python 3.x
- No external dependencies (uses standard library only)

## Options

| Option | Description |
|--------|-------------|
| `target` | Target IP address or hostname (required) |
| `-p, --ports` | Comma-separated ports (e.g., 80,443) |
| `-r, --range` | Port range (e.g., 1-1000) |
| `-a, --all` | Scan all 65535 ports |
| `-t, --threads` | Number of concurrent threads (default: 50) |
| `--timeout` | Connection timeout in seconds (default: 1) |
| `-v, --verbose` | Verbose output |

## Notes

- Requires appropriate permissions for network scanning
- Use responsibly and only on systems you have permission to scan
