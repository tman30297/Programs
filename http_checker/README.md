# HTTP Checker

A command-line tool for checking HTTP/HTTPS server status, response times, and availability.

## Description

HTTP Server Checker verifies the status of web servers by making HTTP/HTTPS requests. It reports status codes, response times, server headers, and supports checking multiple URLs in parallel. Can read URLs from a file or command line arguments.

## Usage

```bash
# Check a single URL
python http_checker.py https://google.com

# Check multiple URLs
python http_checker.py google.com facebook.com twitter.com

# Verbose output (show server info)
python http_checker.py google.com -v

# Check URLs from a file (one per line, lines starting with # are ignored)
python http_checker.py urls.txt

# Custom timeout
python http_checker.py google.com -t 10

# Adjust concurrency (parallel checks)
python http_checker.py urls.txt -c 10

# Use HTTP instead of HTTPS
python http_checker.py example.com --no-https
```

### Options

| Option | Description |
|--------|-------------|
| `targets` | URLs or hosts to check (required, supports multiple) |
| `-v, --verbose` | Show verbose output including server headers |
| `-t, --timeout` | Request timeout in seconds (default: 5) |
| `-c, --concurrency` | Number of concurrent checks (default: 5) |
| `--no-https` | Use HTTP instead of HTTPS |

### File Format

Create a text file with one URL per line:
```
https://google.com
https://github.com
https://stackoverflow.com
# Comments start with #
```

## Requirements

- Python 3.x
- No external dependencies (uses standard library only)
