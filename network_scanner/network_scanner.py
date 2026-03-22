#!/usr/bin/env python3
"""
Enhanced Network Scanner
Scans local subnet for active hosts with OS detection and port scanning.

Usage:
    python network_scanner.py [subnet]          - Basic scan
    python network_scanner.py [subnet] -os      - With OS detection
    python network_scanner.py [subnet] -p       - With port scan
    python network_scanner.py [subnet] -full    - Full scan (all features)
    python network_scanner.py -j output.json    - Export results to JSON
"""

import subprocess
import socket
import ipaddress
import sys
import concurrent.futures
import argparse
import json
from datetime import datetime
from collections import defaultdict

# Configuration
DEFAULT_SUBNET = "192.168.1.0/24"

# Common ports to scan
COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    993: "IMAPS",
    995: "POP3S",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    8080: "HTTP-Alt",
    8443: "HTTPS-Alt",
}

# More thorough port list for full scan
FULL_PORT_RANGE = list(range(1, 1001)) + [1433, 3306, 3389, 5432, 5900, 6379, 8080, 8443, 27017]


def ping_host(ip):
    """Ping a single host using nmap -sn and return True if online."""
    try:
        result = subprocess.run(
            ["nmap", "-sn", "-PR", "--max-retries", "1", "-R", str(ip)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=3
        )
        output = result.stdout.decode()
        return "Host is up" in output or "1 host up" in output, str(ip), output
    except Exception as e:
        return False, str(ip), ""


def detect_os(ip):
    """Attempt to detect the operating system of a host."""
    try:
        # Use nmap OS detection (-O) with service version detection (-sV)
        result = subprocess.run(
            ["nmap", "-O", "-sV", "--max-retries", "2", "-R", str(ip)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=15
        )
        output = result.stdout.decode()
        
        os_info = "Unknown"
        
        # Parse OS matches
        if "OS details:" in output:
            match = output.split("OS details:")[-1].split("\n")[0].strip()
            os_info = match
        elif "Running:" in output:
            match = output.split("Running:")[-1].split("\n")[0].strip()
            os_info = match
        elif "OS guesses:" in output:
            match = output.split("OS guesses:")[-1].split("\n")[0].strip()
            os_info = match
        
        # Try to get device type too
        device_type = "Unknown"
        if "Device type" in output:
            for line in output.split("\n"):
                if "Device type" in line:
                    device_type = line.split("Device type:")[-1].strip()
                    break
        
        return os_info, device_type
    except Exception as e:
        return "Unknown", "Unknown"


def scan_ports(ip, ports=None, quick=True):
    """Scan ports on a specific IP."""
    if ports is None:
        ports = list(COMMON_PORTS.keys()) if quick else FULL_PORT_RANGE
    
    open_ports = []
    
    try:
        port_list = ",".join(str(p) for p in ports)
        result = subprocess.run(
            ["nmap", "-sS", "-sV", "-p", port_list, "--max-retries", "1", str(ip)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=30 if quick else 120
        )
        output = result.stdout.decode()
        
        # Parse open ports
        for line in output.split("\n"):
            if "/tcp" in line or "/udp" in line:
                if "open" in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        port_proto = parts[0].split("/")[0]
                        port = int(port_proto)
                        service = parts[2] if len(parts) > 2 else "unknown"
                        
                        # Try to get version info
                        version = ""
                        if len(parts) > 3 and parts[3] != "unrecognized":
                            version = " ".join(parts[3:6])  # First few version words
                        
                        open_ports.append({
                            'port': port,
                            'service': service,
                            'version': version[:30] if version else "",
                            'proto': parts[0].split("/")[1] if "/" in parts[0] else "tcp"
                        })
        
    except Exception as e:
        pass
    
    return open_ports


def get_hostname(ip):
    """Try to resolve hostname for an IP."""
    try:
        hostname, _, _ = socket.gethostbyaddr(str(ip))
        return hostname
    except socket.herror:
        return None


def get_mac_vendor(mac):
    """Get vendor info from MAC address (simplified)."""
    # Common OUI prefixes
    oui_prefix = mac.replace(":", "").upper()[:6]
    
    vendors = {
        "000C29": "VMware",
        "005056": "VMware",
        "001A2B": "VirtualBox",
        "080027": "VirtualBox",
        "001C42": "Parallels",
        "525400": "QEMU/KVM",
        "B827EB": "Raspberry Pi",
        "DC:A6:32": "Raspberry Pi",
        "E4:5F:01": "Raspberry Pi",
        "F0:18:98": "Apple",
        "3C:06:30": "Apple",
        "A4:83:E7": "Apple",
        "00:50:56": "VMware",
        "00:0C:29": "VMware",
        "00:1C:42": "Parallels",
        "00155D": "Microsoft Hyper-V",
        "00:15:5D": "Microsoft Hyper-V",
    }
    
    # Check first 6 chars (without colons)
    for prefix, vendor in vendors.items():
        if oui_prefix.startswith(prefix.replace(":", "")):
            return vendor
    
    return "Unknown"


def scan_mac(ip):
    """Get MAC address for an IP on local network."""
    try:
        # Use ARP to find MAC
        result = subprocess.run(
            ["arp", "-n", str(ip)],
            capture_output=True, text=True, timeout=5
        )
        
        # Parse MAC address
        match = result.stdout.search(r'([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}')
        if match:
            mac = match.group()
            vendor = get_mac_vendor(mac)
            return mac, vendor
    except:
        pass
    
    return None, None


def scan_single_host(ip_str, detect_os_flag=False, scan_ports_flag=False, quick=True):
    """Scan a single host and return detailed info."""
    is_online, ip, ping_output = ping_host(ip_str)
    
    if not is_online:
        return None
    
    hostname = get_hostname(ip)
    mac, vendor = scan_mac(ip)
    
    info = {
        'ip': ip,
        'hostname': hostname or "Unknown",
        'mac': mac,
        'vendor': vendor,
        'os': None,
        'device_type': None,
        'ports': []
    }
    
    # OS detection
    if detect_os_flag:
        os_info, device_type = detect_os(ip)
        info['os'] = os_info
        info['device_type'] = device_type
    
    # Port scanning
    if scan_ports_flag:
        info['ports'] = scan_ports(ip, quick=quick)
    
    return info


def scan_network(subnet=DEFAULT_SUBNET, detect_os_flag=False, scan_ports_flag=False, 
                 quick_scan=True, max_workers=20):
    """Scan the given subnet for active hosts."""
    print(f"\n{'='*60}")
    print("  ENHANCED NETWORK SCANNER")
    print('='*60)
    print(f"  Target: {subnet}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    flags = []
    if detect_os_flag:
        flags.append("OS")
    if scan_ports_flag:
        flags.append("Ports")
    if flags:
        print(f"  Features: {', '.join(flags)}")
    
    print('-' * 60)
    
    network = ipaddress.ip_network(subnet, strict=False)
    hosts = list(network.hosts())
    
    online_hosts = []
    
    # Phase 1: Discovery (ping scan)
    print(f"  [1/2] Discovering hosts on {subnet}...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(ping_host, hosts))
    
    discovered = [(ip, output) for is_online, ip, output in results if is_online]
    print(f"  Found {len(discovered)} active host(s)")
    
    if not discovered:
        print("  No hosts found.")
        return []
    
    # Phase 2: Detailed scan (optional)
    if detect_os_flag or scan_ports_flag:
        print(f"  [2/2] Gathering detailed info...")
        
        for ip, _ in discovered:
            info = scan_single_host(
                ip, 
                detect_os_flag=detect_os_flag,
                scan_ports_flag=scan_ports_flag,
                quick=quick_scan
            )
            if info:
                online_hosts.append(info)
                
                # Print as we find
                vendor_str = f" ({info['vendor']})" if info['vendor'] != "Unknown" else ""
                os_str = f" | {info['os']}" if info['os'] and info['os'] != "Unknown" else ""
                
                port_str = ""
                if info['ports']:
                    port_str = f" | {', '.join(str(p['port']) for p in info['ports'][:5])}"
                    if len(info['ports']) > 5:
                        port_str += f"+{len(info['ports'])-5}"
                
                print(f"    {info['ip']:<16} {info['hostname']:<25}{vendor_str}{os_str}{port_str}")
    else:
        # Just show basic info
        for ip, _ in discovered:
            hostname = get_hostname(ip)
            mac, vendor = scan_mac(ip)
            
            info = {
                'ip': ip,
                'hostname': hostname or "Unknown",
                'mac': mac,
                'vendor': vendor,
                'os': None,
                'device_type': None,
                'ports': []
            }
            online_hosts.append(info)
            
            vendor_str = f" ({vendor})" if vendor != "Unknown" else ""
            print(f"    {info['ip']:<16} {info['hostname']:<25}{vendor_str}")
    
    print('-' * 60)
    print(f"  Scan complete! Found {len(online_hosts)} active host(s)")
    print(f"  Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return online_hosts


def print_detailed_report(hosts):
    """Print a detailed report of all scanned hosts."""
    print(f"\n{'='*60}")
    print("  DETAILED SCAN REPORT")
    print('='*60)
    
    for host in hosts:
        print(f"\n  [{host['ip']}]")
        print(f"    Hostname: {host['hostname']}")
        if host['mac']:
            print(f"    MAC: {host['mac']} ({host['vendor']})")
        if host['os'] and host['os'] != "Unknown":
            print(f"    OS: {host['os']}")
        if host['device_type'] and host['device_type'] != "Unknown":
            print(f"    Type: {host['device_type']}")
        
        if host['ports']:
            print(f"    Open Ports:")
            for p in host['ports']:
                ver = f" ({p['version']})" if p['version'] else ""
                print(f"      - {p['port']}/{p['proto']}: {p['service']}{ver}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Enhanced Network Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python network_scanner.py                              Scan default subnet
  python network_scanner.py 192.168.1.0/24              Custom subnet
  python network_scanner.py -os                          With OS detection
  python network_scanner.py -p                           With port scan
  python network_scanner.py -full                        Full scan (OS + ports)
  python network_scanner.py -p -j results.json           Port scan + save JSON
  python network_scanner.py -full -j output.json        Full scan + JSON export
        '''
    )
    
    parser.add_argument('subnet', nargs='?', default=DEFAULT_SUBNET,
                        help='Subnet to scan (e.g., 192.168.1.0/24)')
    parser.add_argument('-o', '--os', action='store_true',
                        help='Enable OS detection')
    parser.add_argument('-p', '--ports', action='store_true',
                        help='Enable port scanning')
    parser.add_argument('--no-quick', action='store_true',
                        help='Full port scan (slower, more thorough)')
    parser.add_argument('-f', '--full', action='store_true',
                        help='Full scan (OS detection + port scan)')
    parser.add_argument('-r', '--report', action='store_true',
                        help='Print detailed report at end')
    parser.add_argument('-t', '--threads', type=int, default=20,
                        help='Number of concurrent threads (default: 20)')
    parser.add_argument('-j', '--json', metavar='FILE',
                        help='Export results to JSON file')
    
    args = parser.parse_args()
    
    # Determine flags
    detect_os_flag = args.os or args.full
    scan_ports_flag = args.ports or args.full
    quick_scan = not args.no_quick
    
    hosts = scan_network(
        subnet=args.subnet,
        detect_os_flag=detect_os_flag,
        scan_ports_flag=scan_ports_flag,
        quick_scan=quick_scan,
        max_workers=args.threads
    )
    
    # Export to JSON if requested
    if args.json and hosts:
        export_to_json(hosts, args.json)
    
    if args.report and hosts:
        print_detailed_report(hosts)


def export_to_json(hosts, filename):
    """Export scan results to JSON file."""
    import json
    
    output = {
        "scan_time": datetime.now().isoformat(),
        "total_hosts": len(hosts),
        "hosts": hosts
    }
    
    try:
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\n[+] Results exported to {filename}")
    except Exception as e:
        print(f"\n[!] Failed to export JSON: {e}")
