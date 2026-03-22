# Network Analyzer - Usage Guide

A network analysis tool for ethical hacking education. Monitors DNS queries and analyzes network traffic.

## Requirements

```bash
sudo apt install tcpdump nmap arp-scan
```

## Basic Commands

```bash
# Run with sudo (required for packet capture)
sudo python /media/tony/Drive2/Programs/net_analyzer.py
```

## Options

| Flag | Description |
|------|-------------|
| `-h, --help` | Show help message |
| `-w, --watch` | Real-time monitoring mode |
| `-d, --dns-only` | Show DNS queries only |
| `-p, --pcap-only` | Show packet analysis only |
| `-o, --output FILE` | Save output to file |
| `-D, --duration SEC` | Capture duration in seconds (default: 5) |
| `-i, --interface IFACE` | Network interface (default: any) |

## Examples

### 1. Single Scan (All)
```bash
sudo python /media/tony/Drive2/Programs/net_analyzer.py
```
Shows:
- Discovered devices on network
- DNS queries
- Packet summary

### 2. Real-Time Monitoring
```bash
sudo python /media/tony/Drive2/Programs/net_analyzer.py --watch
```
Continuously monitors and displays updates.

### 3. DNS Queries Only
```bash
sudo python /media/tony/Drive2/Programs/net_analyzer.py --dns-only
```
Shows only DNS queries from devices.

### 4. Packet Analysis Only
```bash
sudo python /media/tony/Drive2/Programs/net_analyzer.py --pcap-only
```
Shows protocol distribution and top talkers.

### 5. Save to File
```bash
sudo python /media/tony/Drive2/Programs/net_analyzer.py -o network_log.txt
```

### 6. Custom Duration
```bash
sudo python /media/tony/Drive2/Programs/net_analyzer.py --duration 10
```
Capture for 10 seconds instead of default 5.

### 7. Specific Interface
```bash
sudo python /media/tony/Drive2/Programs/net_analyzer.py -i eth0
```

## Features

### Device Discovery
Automatically scans network and identifies device types:
- **TV** - Roku, Hisense, Samsung, Chromecast, Fire TV
- **Phone/Tablet** - iPhone, Android, Galaxy, Pixel
- **Computer** - Linux, MacBook, PC, Desktop
- **IoT Camera** - TUYA, IPC, Nest, Ring
- **Printer** - HP, Canon, Epson
- **Gaming** - PlayStation, Xbox, Nintendo
- **Smart Speaker** - Echo, HomePod, Google Home

### DNS Query Monitor
Shows which devices are querying which domains:
```
Timestamp    Source IP        Queried Domain         
----------------------------------------------------
20:30:45    192.168.1.133   google.com
20:30:46    192.168.1.135   netflix.com
```

### Packet Analyzer
Shows:
- Protocol distribution (TCP/UDP/ICMP)
- Top talkers (IP pairs with most traffic)
- Total packets captured

## Troubleshooting

### "tcpdump not found"
```bash
sudo apt install tcpdump
```

### "nmap not found"
```bash
sudo apt install nmap
```

### Permission Denied
Must run with `sudo` for packet capture:
```bash
sudo python /media/tony/Drive2/Programs/net_analyzer.py
```

## Educational Use Only

This tool is for:
- Network security testing on your own network
- Learning about network protocols
- Monitoring your own devices

Do not use on networks without permission.
