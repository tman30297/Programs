# Network Dashboard

Real-time network monitoring dashboard with device scanning.

## Requirements

```bash
pip install flask psutil
```

## Usage

```bash
python network_dashboard.py
```

Then open **http://localhost:5000**

## Features

### ⚡ Speed Test
- Real-time download/upload speed monitoring
- Click "Test Speed" to measure current speeds

### 📊 Network Statistics
- Total data downloaded/uploaded
- Packets sent/received
- Error counters

### 🔗 Active Connections
- Shows all established connections
- Local/remote addresses
- Process name for each connection

### 📱 Device Scanner
- Scan your local network for active devices
- Shows IP, hostname, last seen time
- Uses ping sweep (192.168.x.1-254)

## Auto-Refresh

Dashboard auto-refreshes every 5 seconds. Use buttons for manual actions.

## Notes

- Requires network scan permission
- Speed test measures actual transfer (not internet speed)
- Device scan may take 30-60 seconds
