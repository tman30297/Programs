# PyQt Network Scanner

A desktop GUI application for scanning networks and detecting active hosts with open ports.

## Description

PyQt Network Scanner provides a graphical interface for network scanning operations. It discovers live hosts within an IP range and optionally scans for open ports. The application runs scans in background threads to keep the UI responsive and displays results in a sortable table.

## Usage

```bash
# Run the application
python pyqt_network_scanner.py
```

### Features

- **IP Range Scanning**: Enter any CIDR notation (e.g., 192.168.1.0/24)
- **Scan Types**:
  - Quick Scan (ping only - discover live hosts)
  - Common Ports (predefined list of common services)
  - Top 20 Ports (most commonly used ports)
  - Custom Ports (specify your own comma-separated list)
- **Real-time Progress**: Progress bar shows scan status
- **Results Table**: Shows IP, hostname, status, open ports, and services
- **Stop/Clear**: Ability to stop ongoing scans and clear results

### Scan Type Details

| Scan Type | Description |
|-----------|-------------|
| Quick Scan | Discovers live hosts via TCP connect to port 80 |
| Common Ports | Scans for 20 common services (SSH, HTTP, MySQL, etc.) |
| Top 20 Ports | Scans top 20 ports used in network scanning |
| Custom Ports | User-specified ports (e.g., 22,80,443,3389) |

## Requirements

- Python 3.x
- PyQt5 (`pip install PyQt5`)
