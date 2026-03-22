#!/usr/bin/env python3
"""
Network Dashboard - Monitor your network at a glance
Shows: Device Scanner, Speed Test, Port Monitor, Connections

Usage:
    python network_dashboard.py
Then open http://localhost:5050
"""

from flask import Flask, jsonify, render_template_string
import psutil
import socket
import time
import threading
import subprocess
import re
import json
import os

app = Flask(__name__)

# Store scanned devices
devices = []
last_scan_time = 0
scan_in_progress = False

def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_default_gateway():
    """Get default gateway IP"""
    try:
        result = subprocess.run(['ip', 'route'], capture_output=True, text=True, timeout=5)
        for line in result.stdout.split('\n'):
            if 'default' in line:
                return line.split()[2]
    except:
        pass
    return None

def get_subnet():
    """Calculate subnet from local IP"""
    local_ip = get_local_ip()
    if '.' in local_ip:
        return '.'.join(local_ip.split('.')[:-1])
    return "192.168.1"

def ping_host(ip):
    """Ping a single host"""
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '1', ip],
            capture_output=True, timeout=2
        )
        return result.returncode == 0
    except:
        return False

def get_hostname(ip):
    """Get hostname from IP"""
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except:
        return ""

def get_mac_address(ip):
    """Get MAC address from ARP cache"""
    try:
        # Try to get from ARP cache first
        result = subprocess.run(['arp', '-n', ip], capture_output=True, text=True, timeout=3)
        match = re.search(r'([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}', result.stdout)
        if match:
            return match.group(0).upper()
    except:
        pass
    return "Unknown"

def get_vendor(mac):
    """Get vendor from MAC address prefix"""
    # Common OUI prefixes
    vendors = {
        '00:50:56': 'VMware',
        '00:0C:29': 'VMware',
        '00:1C:42': 'Parallels',
        '08:00:27': 'VirtualBox',
        '52:54:00': 'QEMU',
        'B8:27:EB': 'Raspberry Pi',
        'DC:A6:32': 'Raspberry Pi',
        'E4:5F:01': 'Raspberry Pi',
        '00:17:88': 'Philips Hue',
        '00:1A:22': 'Cisco',
        '00:1E:68': 'Cisco',
        '00:25:B3': 'HP',
        '00:26:B9': 'Dell',
        '3C:97:0E': 'Wistron',
        '00:1C:C4': 'Dell',
        '18:03:73': 'Dell',
        '34:17:EB': 'Dell',
        '00:1D:09': 'Dell',
        '00:1E:C9': 'Dell',
        '00:24:E8': 'Dell',
        '00:1A:A0': 'Dell',
        '28:C6:3F': 'Intel',
        '3C:D9:2B': 'HP',
        '00:50:B6': 'Linksys',
        '00:1F:33': 'Netgear',
        '00:22:6B': 'Netgear',
        'C4:04:15': 'Netgear',
        'C0:3F:0E': 'Netgear',
        '00:1E:2A': 'Belkin',
        '00:22:EE': 'ASUSTek',
        '00:1D:60': 'ASUSTek',
        '00:25:22': 'ASUSTek',
        'AC:22:0B': 'ASUSTek',
        'F4:F2:6D': 'Apple',
        '3C:06:30': 'Apple',
        'A4:D1:8C': 'Apple',
        'F0:18:98': 'Apple',
        '00:26:BB': 'Apple',
        '00:1F:F3': 'Apple',
        'DC:2B:2A': 'Apple',
        '00:26:08': 'Apple',
        '8C:8590': 'Apple',
        'F8:FF:C2': 'Apple',
        '00:3E:E1': 'Apple',
        '9C:04:73': 'Samsung',
        '00:1D:F6': 'Samsung',
        '00:21:19': 'Samsung',
        '00:23:39': 'Samsung',
        '00:24:90': 'Samsung',
        '00:21:4C': 'Samsung',
        '38:94:ED': 'Samsung',
        '40:B0:34': 'Samsung',
        '50:01:BB': 'Samsung',
        '58:C3:8B': 'Cisco-Linksys',
        '00:23:69': 'Cisco-Linksys',
        'E0:46:9A': 'Cisco-Linksys',
        '00:24:B2': 'Netgear',
        '00:1B:2F': 'Netgear',
        '44:94:FC': 'Netgear',
        '9C:D3:6D': 'Netgear',
        '00:1E:2A': 'D-Link',
        '00:1C:F0': 'D-Link',
        '00:22:B0': 'D-Link',
        '14:D6:4D': 'D-Link',
        '1C:7E:E5': 'D-Link',
        '78:54:2E': 'Google',
        'F4:F5:D8': 'Google',
        '94:EB:2C': 'Google',
        '00:1A:11': 'Google',
        '54:60:09': 'Google',
        'F0:27:2D': 'Amazon',
        '34:D2:70': 'Amazon',
        '38:F7:3D': 'Amazon',
        '50:DC:E7': 'Amazon',
        '68:37:E9': 'Amazon',
        '68:54:FD': 'Amazon',
        '74:C2:46': 'Amazon',
        '84:D6:D0': 'Amazon',
        'A0:02:DC': 'Amazon',
        'AC:63:BE': 'Amazon',
        '0C:47:C9': 'Amazon',
        'F0:81:73': 'Amazon',
        '00:BB:3A': 'Amazon',
        '08:9E:08': 'Amazon',
        '20:3E:CA': 'Amazon',
        '4C:EF:C0': 'Amazon',
        '68:54:FD': 'Amazon',
        '70:B5:E8': 'Amazon',
        '74:75:48': 'Amazon',
        '78:E1:03': 'Amazon',
        '8C:C8:CD': 'Amazon',
        'A0:9B:0D': 'Amazon',
        'AC:63:BE': 'Amazon',
        'B4:7C:9C': 'Amazon',
        'CC:9E:A2': 'Amazon',
        'F0:27:2D': 'Amazon',
        'F0:81:73': 'Amazon',
        'FC:65:DE': 'Amazon',
    }
    
    if mac and len(mac) >= 8:
        prefix = mac[:8].upper()
        return vendors.get(prefix, "Unknown")
    return "Unknown"

def get_device_type(hostname, vendor, ip):
    """Guess device type from hostname/vendor"""
    hostname_lower = hostname.lower() if hostname else ""
    
    # Check hostname patterns
    if 'router' in hostname_lower or 'gateway' in hostname_lower:
        return "Router"
    if 'printer' in hostname_lower or 'hp-' in hostname_lower or 'canon' in hostname_lower:
        return "Printer"
    if 'iphone' in hostname_lower or 'ipad' in hostname_lower or 'android' in hostname_lower:
        return "Mobile"
    if 'macbook' in hostname_lower or 'laptop' in hostname_lower or 'desktop' in hostname_lower:
        return "Computer"
    if 'raspberry' in hostname_lower or 'pi-' in hostname_lower:
        return "Raspberry Pi"
    if 'nest' in hostname_lower or 'hue' in hostname_lower or 'smart' in hostname_lower:
        return "Smart Home"
    if 'shield' in hostname_lower or 'firetv' in hostname_lower or 'roku' in hostname_lower or 'appletv' in hostname_lower:
        return "Streaming"
    if 'xbox' in hostname_lower or 'playstation' in hostname_lower or 'nintendo' in hostname_lower:
        return "Gaming"
    if 'cam' in hostname_lower or 'nvr' in hostname_lower or 'frigate' in hostname_lower:
        return "Camera"
    if 'phone' in hostname_lower:
        return "Phone"
    
    # Check vendor
    vendor_lower = vendor.lower() if vendor else ""
    if 'apple' in vendor_lower:
        return "Apple Device"
    if 'samsung' in vendor_lower:
        return "Samsung Device"
    if 'intel' in vendor_lower:
        return "Computer"
    if 'cisco' in vendor_lower or 'netgear' in vendor_lower or 'linksys' in vendor_lower:
        return "Network Device"
    if 'dell' in vendor_lower or 'hp' in vendor_lower:
        return "Computer"
    if 'raspberry' in vendor_lower:
        return "Raspberry Pi"
    if 'amazon' in vendor_lower:
        return "Amazon Device"
    if 'google' in vendor_lower:
        return "Google Device"
    
    return "Device"

def scan_network():
    """Scan entire local network"""
    global devices, last_scan_time, scan_in_progress
    
    if scan_in_progress:
        return
    
    scan_in_progress = True
    devices = []
    subnet = get_subnet()
    gateway = get_default_gateway()
    
    print(f"🔍 Scanning network {subnet}.0/24...")
    print(f"   Gateway: {gateway}")
    
    # First, get all known IPs from ARP cache
    arp_devices = {}
    try:
        result = subprocess.run(['arp', '-a'], capture_output=True, text=True, timeout=10)
        for line in result.stdout.split('\n'):
            # Match ARP entries
            match = re.search(r'\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+([0-9a-fA-F:]+)', line)
            if match:
                ip = match.group(1)
                mac = match.group(2).upper()
                arp_devices[ip] = mac
    except:
        pass
    
    # Also scan using netdiscover style approach
    # Try common gateway and high-numbered IPs first
    priority_ips = []
    if gateway:
        priority_ips.append(gateway)
    
    # Add common IP ranges
    for i in [1, 254, 100, 200]:
        ip = f"{subnet}.{i}"
        if ip != gateway:
            priority_ips.append(ip)
    
    # Scan priority IPs first
    for ip in priority_ips:
        if ping_host(ip):
            hostname = get_hostname(ip)
            mac = arp_devices.get(ip, get_mac_address(ip))
            vendor = get_vendor(mac)
            device_type = get_device_type(hostname, vendor, ip)
            
            devices.append({
                'ip': ip,
                'hostname': hostname or "Unknown",
                'mac': mac,
                'vendor': vendor,
                'type': device_type,
                'last_seen': time.strftime("%H:%M:%S"),
                'status': 'online'
            })
    
    # Then scan remaining IPs (threaded for speed)
    def scan_range(start, end):
        local_devices = []
        for i in range(start, end):
            if i in [int(gateway.split('.')[-1]) if gateway else 0]:
                continue  # Skip gateway
            
            ip = f"{subnet}.{i}"
            if ping_host(ip):
                hostname = get_hostname(ip)
                mac = arp_devices.get(ip, get_mac_address(ip))
                vendor = get_vendor(mac)
                device_type = get_device_type(hostname, vendor, ip)
                
                local_devices.append({
                    'ip': ip,
                    'hostname': hostname or "Unknown",
                    'mac': mac,
                    'vendor': vendor,
                    'type': device_type,
                    'last_seen': time.strftime("%H:%M:%S"),
                    'status': 'online'
                })
        return local_devices
    
    # Scan in parallel threads
    threads = []
    ranges = [(2, 50), (50, 100), (100, 150), (150, 200), (200, 255)]
    
    for start, end in ranges:
        t = threading.Thread(target=lambda s=start, e=end: devices.extend(scan_range(s, e)))
        t.start()
        threads.append(t)
    
    # Wait for all threads
    for t in threads:
        t.join()
    
    # Sort by IP
    devices.sort(key=lambda x: [int(o) for o in x['ip'].split('.')])
    
    last_scan_time = time.time()
    scan_in_progress = False
    print(f"✅ Scan complete! Found {len(devices)} devices")

def get_network_stats():
    """Get current network statistics"""
    net = psutil.net_io_counters()
    return {
        'bytes_sent': net.bytes_sent,
        'bytes_recv': net.bytes_recv,
        'packets_sent': net.packets_sent,
        'packets_recv': net.packets_recv,
        'errin': net.errin,
        'errout': net.errout,
        'dropin': net.dropin,
        'dropout': net.dropout,
    }

def get_connections():
    """Get active network connections"""
    connections = []
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'ESTABLISHED':
                try:
                    local = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "?"
                    remote = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "?"
                    try:
                        proc = psutil.Process(conn.pid).name() if conn.pid else ""
                    except:
                        proc = ""
                    connections.append({
                        'local': local,
                        'remote': remote,
                        'status': conn.status,
                        'process': proc[:30] if proc else "",
                        'pid': conn.pid
                    })
                except:
                    pass
    except:
        pass
    return connections[:50]

def get_speed():
    """Get network speed by measuring over 1 second"""
    start = psutil.net_io_counters()
    time.sleep(1)
    end = psutil.net_io_counters()
    
    return {
        'download_mbps': (end.bytes_recv - start.bytes_recv) * 8 / 1024 / 1024,
        'upload_mbps': (end.bytes_sent - start.bytes_sent) * 8 / 1024 / 1024,
    }

# Perform initial scan in background
threading.Thread(target=scan_network, daemon=True).start()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Network Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: #1a1a2e; 
            color: #eee;
            padding: 20px;
        }
        h1 { 
            text-align: center; 
            color: #00d4ff; 
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #888;
            margin-bottom: 20px;
            font-size: 0.9em;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            max-width: 1600px;
            margin: 0 auto;
        }
        .card {
            background: #16213e;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .card h2 {
            color: #00d4ff;
            border-bottom: 2px solid #00d4ff;
            padding-bottom: 10px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .stat {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #2a2a4a;
        }
        .stat-label { color: #888; }
        .stat-value { 
            color: #00ff88; 
            font-weight: bold;
        }
        .speed-display {
            text-align: center;
            padding: 20px;
        }
        .speed-value {
            font-size: 3em;
            color: #00ff88;
        }
        .speed-unit { color: #888; }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 10px 8px;
            text-align: left;
            border-bottom: 1px solid #2a2a4a;
            font-size: 0.9em;
        }
        th { color: #00d4ff; }
        tr:hover { background: #2a2a4a; }
        .btn {
            background: #00d4ff;
            color: #1a1a2e;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            margin: 5px;
        }
        .btn:hover { background: #00a3cc; }
        .btn-small {
            padding: 5px 10px;
            font-size: 0.8em;
        }
        .refresh-info {
            text-align: center;
            color: #666;
            margin-top: 10px;
            font-size: 0.85em;
        }
        .device-type {
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.75em;
            background: #2a2a4a;
        }
        .type-router { background: #4a2a6a; color: #d4aaff; }
        .type-camera { background: #3a4a2a; color: #aaffaa; }
        .type-phone { background: #2a3a4a; color: #aaaaff; }
        .type-mobile { background: #2a3a4a; color: #aaaaff; }
        .type-computer { background: #3a2a4a; color: #ffaaff; }
        .type-smart { background: #4a4a2a; color: #ffaaaa; }
        .type-streaming { background: #2a4a4a; color: #aaffff; }
        .type-unknown { background: #2a2a2a; color: #888; }
        .scanning {
            color: #00d4ff;
            animation: pulse 1s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
    </style>
</head>
<body>
    <h1>🌐 Network Dashboard</h1>
    <p class="subtitle">Local IP: {{ local_ip }} | Gateway: {{ gateway }}</p>
    
    <div class="grid">
        <!-- Speed Test -->
        <div class="card">
            <h2>⚡ Network Speed</h2>
            <div class="speed-display">
                <div>
                    <span class="speed-value" id="download">{{ "%.1f"|format(speed.download_mbps) }}</span>
                    <span class="speed-unit">Mbps ↓</span>
                </div>
                <div style="margin-top:10px;">
                    <span class="speed-value" id="upload">{{ "%.1f"|format(speed.upload_mbps) }}</span>
                    <span class="speed-unit">Mbps ↑</span>
                </div>
                <button class="btn" onclick="refreshSpeed()">↻ Test Speed</button>
            </div>
        </div>
        
        <!-- Network Stats -->
        <div class="card">
            <h2>📊 Statistics</h2>
            <div class="stat">
                <span class="stat-label">Total Downloaded</span>
                <span class="stat-value">{{ "%.2f"|format(stats.bytes_recv / 1024 / 1024 / 1024) }} GB</span>
            </div>
            <div class="stat">
                <span class="stat-label">Total Uploaded</span>
                <span class="stat-value">{{ "%.2f"|format(stats.bytes_sent / 1024 / 1024 / 1024) }} GB</span>
            </div>
            <div class="stat">
                <span class="stat-label">Packets Received</span>
                <span class="stat-value">{{ "{:,}".format(stats.packets_recv) }}</span>
            </div>
            <div class="stat">
                <span class="stat-label">Packets Sent</span>
                <span class="stat-value">{{ "{:,}".format(stats.packets_sent) }}</span>
            </div>
            <div class="stat">
                <span class="stat-label">Errors In</span>
                <span class="stat-value">{{ stats.errin }}</span>
            </div>
            <div class="stat">
                <span class="stat-label">Errors Out</span>
                <span class="stat-value">{{ stats.errout }}</span>
            </div>
        </div>
        
        <!-- Active Connections -->
        <div class="card">
            <h2>🔗 Active Connections</h2>
            <div style="max-height: 300px; overflow-y: auto;">
                <table>
                    <tr>
                        <th>Local</th>
                        <th>Remote</th>
                        <th>Process</th>
                    </tr>
                    {% for conn in connections[:25] %}
                    <tr>
                        <td>{{ conn.local }}</td>
                        <td>{{ conn.remote }}</td>
                        <td>{{ conn.process }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>
        
        <!-- Device Scanner -->
        <div class="card" style="grid-column: 1 / -1;">
            <h2>
                📱 Network Devices
                <button class="btn btn-small" onclick="scanNetwork()">🔍 Scan Network</button>
            </h2>
            <div id="scan-status"></div>
            <div style="max-height: 500px; overflow-y: auto;">
                <table>
                    <tr>
                        <th>IP Address</th>
                        <th>Hostname</th>
                        <th>MAC Address</th>
                        <th>Vendor</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>Last Seen</th>
                    </tr>
                    {% for device in devices %}
                    <tr>
                        <td>{{ device.ip }}</td>
                        <td>{{ device.hostname }}</td>
                        <td>{{ device.mac }}</td>
                        <td>{{ device.vendor }}</td>
                        <td><span class="device-type type-{{ device.type|lower|replace(' ', '-') }}">{{ device.type }}</span></td>
                        <td style="color: #00ff88;">● {{ device.status }}</td>
                        <td>{{ device.last_seen }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            {% if devices %}
            <p class="refresh-info">Found {{ devices|length }} devices | Last scan: {{ last_scan }} | Local: {{ local_ip }}</p>
            {% else %}
            <p class="refresh-info" id="no-devices">Click "Scan Network" to discover devices</p>
            {% endif %}
        </div>
    </div>
    
    <script>
        function refreshSpeed() {
            fetch('/api/speed')
                .then(r => r.json())
                .then(d => {
                    document.getElementById('download').textContent = d.download_mbps.toFixed(1);
                    document.getElementById('upload').textContent = d.upload_mbps.toFixed(1);
                });
        }
        
        function scanNetwork() {
            const status = document.getElementById('scan-status');
            status.innerHTML = '<p class="scanning">🔍 Scanning network... (this may take up to 60 seconds)</p>';
            fetch('/api/scan')
                .then(r => r.json())
                .then(d => {
                    status.innerHTML = '<p style="color:#00ff88">✅ Scan complete! Found ' + d.count + ' devices</p>';
                    setTimeout(() => location.reload(), 1000);
                })
                .catch(e => {
                    status.innerHTML = '<p style="color:#ff4444">❌ Scan failed</p>';
                });
        }
        
        // Auto-refresh every 10 seconds for stats
        setInterval(refreshSpeed, 10000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    stats = get_network_stats()
    speed = get_speed()
    connections = get_connections()
    
    global last_scan_time
    last_scan = time.strftime("%H:%M:%S", time.localtime(last_scan_time)) if last_scan_time else "Never"
    
    return render_template_string(HTML_TEMPLATE, 
                                  stats=stats,
                                  speed=speed,
                                  connections=connections,
                                  devices=devices,
                                  last_scan=last_scan,
                                  local_ip=get_local_ip(),
                                  gateway=get_default_gateway() or "Unknown")

@app.route('/api/speed')
def api_speed():
    return jsonify(get_speed())

@app.route('/api/scan')
def api_scan():
    if not scan_in_progress:
        thread = threading.Thread(target=scan_network)
        thread.start()
    return jsonify({'count': len(devices), 'status': 'scanning' if scan_in_progress else 'done'})

@app.route('/api/connections')
def api_connections():
    return jsonify(get_connections())

@app.route('/api/stats')
def api_stats():
    return jsonify(get_network_stats())

if __name__ == '__main__':
    local_ip = get_local_ip()
    gateway = get_default_gateway()
    print(f"🌐 Network Dashboard starting...")
    print(f"   Local IP: {local_ip}")
    print(f"   Gateway: {gateway}")
    print(f"   Subnet: {get_subnet()}.0/24")
    print(f"Open http://localhost:5050")
    app.run(host='0.0.0.0', port=5050, debug=False, threaded=True)
