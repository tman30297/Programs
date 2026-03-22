# Network Scanner

Scan local network for active devices.

## Requirements

```bash
sudo apt install nmap
```

## Run

```bash
# Default subnet (192.168.1.0/24)
python network_scanner.py

# Custom subnet
python network_scanner.py 10.0.0.0/24
```

## Features

- Ping sweep of local network
- Resolves hostnames
- Shows online devices with IP and hostname
