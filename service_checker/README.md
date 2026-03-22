# Service Checker

A command-line tool for checking if common services are running on a target host by scanning ports.

## Description

Quick Service Checker scans a target IP or hostname for open ports corresponding to common services. It supports quick scans (few common ports), full scans (20+ ports), and custom port specifications. Results show which services are available.

## Usage

```bash
# Scan common ports
python service_checker.py 192.168.1.1

# Verbose output (show closed ports too)
python service_checker.py localhost -v

# Quick scan (fewer common ports)
python service_checker.py 192.168.1.1 --quick

# Custom ports
python service_checker.py 192.168.1.1 -p 22,80,443,3306,5432

# Custom timeout
python service_checker.py 192.168.1.1 -t 3
```

### Options

| Option | Description |
|--------|-------------|
| `host` | Target IP or hostname (required) |
| `-v, --verbose` | Show all ports (not just open ones) |
| `-q, --quick` | Quick scan (fewer common ports: 22, 80, 443, 3389, 8080) |
| `-t, --timeout` | Connection timeout in seconds (default: 1) |
| `-p, --ports` | Custom ports as comma-separated list |

### Default Ports Scanned

FTP (21), SSH (22), Telnet (23), SMTP (25), DNS (53), HTTP (80), POP3 (110), IMAP (143), HTTPS (443), SMB (445), IMAPS (993), POP3S (995), MySQL (3306), RDP (3389), PostgreSQL (5432), VNC (5900), Redis (6379), HTTP-Alt (8080), HTTPS-Alt (8443), Elasticsearch (9200), MongoDB (27017)

## Requirements

- Python 3.x
- No external dependencies (uses standard library only)
