#!/usr/bin/env python3
"""
Quick Port Scanner - A lightweight, fast port scanner
Uses Python's socket and concurrent.futures for parallel scanning.

Usage:
    python quick_port_scanner.py <ip> [ports] [options]
    
Examples:
    python quick_port_scanner.py 192.168.1.1                  # Scan common ports
    python quick_port_scanner.py 192.168.1.1 -p 80,443       # Scan specific ports
    python quick_port_scanner.py 192.168.1.1 -r 1-1000        # Scan port range
    python quick_port_scanner.py 192.168.1.1 --all            # Scan all ports (slow)
    python quick_port_scanner.py 192.168.1.1 -t 50            # 50 concurrent threads
"""

import argparse
import socket
import sys
import concurrent.futures
from datetime import datetime

# Common ports and their services
COMMON_PORTS = {
    20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 67: "DHCP", 68: "DHCP", 69: "TFTP", 80: "HTTP",
    110: "POP3", 119: "NNTP", 123: "NTP", 135: "RPC", 137: "NetBIOS",
    138: "NetBIOS", 139: "NetBIOS", 143: "IMAP", 161: "SNMP", 162: "SNMP-Trap",
    389: "LDAP", 443: "HTTPS", 445: "SMB", 465: "SMTPS", 514: "Syslog",
    587: "SMTP", 636: "LDAPS", 993: "IMAPS", 995: "POP3S", 1080: "SOCKS",
    1433: "MSSQL", 1521: "Oracle", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL",
    5900: "VNC", 5901: "VNC-1", 6379: "Redis", 8080: "HTTP-Alt", 8443: "HTTPS-Alt",
    8888: "HTTP-Alt", 9000: "SonarQube", 9200: "Elasticsearch", 27017: "MongoDB"
}


def scan_port(ip, port, timeout=1):
    """Scan a single port on the target IP."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        
        if result == 0:
            # Try to get service name
            try:
                service = socket.getservbyport(port)
            except:
                service = COMMON_PORTS.get(port, "Unknown")
            
            return {'port': port, 'status': 'open', 'service': service}
    except socket.timeout:
        pass
    except socket.error:
        pass
    
    return None


def resolve_hostname(host):
    """Resolve hostname to IP address."""
    try:
        return socket.gethostbyname(host)
    except socket.gaierror:
        print(f"Error: Could not resolve hostname '{host}'")
        sys.exit(1)


def parse_ports(port_spec):
    """Parse port specification string."""
    ports = set()
    
    for part in port_spec.split(','):
        part = part.strip()
        
        if '-' in part:
            # Range (e.g., "1-1000")
            start, end = part.split('-')
            ports.update(range(int(start), int(end) + 1))
        else:
            # Single port or comma-separated
            try:
                ports.add(int(part))
            except ValueError:
                pass
    
    return sorted(ports)


def scan_target(ip, ports, threads=50, timeout=1):
    """Scan multiple ports on a target IP."""
    print(f"\nScanning {ip}...")
    print(f"Ports: {len(ports)} | Threads: {threads} | Timeout: {timeout}s")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print("-" * 50)
    
    open_ports = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        # Submit all scan tasks
        futures = {executor.submit(scan_port, ip, port, timeout): port for port in ports}
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                open_ports.append(result)
                print(f"  [OPEN] Port {result['port']:>5} - {result['service']}")
    
    print("-" * 50)
    print(f"Scan complete! Found {len(open_ports)} open port(s)")
    print(f"Finished: {datetime.now().strftime('%H:%M:%S')}")
    
    return open_ports


def main():
    parser = argparse.ArgumentParser(
        description='Quick Port Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Port specification:
  - Comma-separated: 80,443,8080
  - Range: 1-1000
  - Common: (uses predefined common ports)
  
Examples:
  python quick_port_scanner.py 192.168.1.1
  python quick_port_scanner.py 192.168.1.1 -p 22,80,443
  python quick_port_scanner.py 192.168.1.1 -r 1-1000
  python quick_port_scanner.py example.com -t 100 --timeout 0.5
        '''
    )
    
    parser.add_argument('target', help='Target IP or hostname')
    parser.add_argument('-p', '--ports', type=str,
                        help='Ports to scan (default: common ports)')
    parser.add_argument('-r', '--range', type=str,
                        help='Port range (e.g., 1-1000)')
    parser.add_argument('-a', '--all', action='store_true',
                        help='Scan all 65535 ports (slow)')
    parser.add_argument('-t', '--threads', type=int, default=50,
                        help='Number of concurrent threads (default: 50)')
    parser.add_argument('--timeout', type=float, default=1.0,
                        help='Connection timeout in seconds (default: 1)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show verbose output')
    
    args = parser.parse_args()
    
    # Resolve hostname
    ip = resolve_hostname(args.target)
    print(f"\n{'='*50}")
    print(f"  QUICK PORT SCANNER")
    print(f"{'='*50}")
    print(f"Target: {args.target} ({ip})")
    
    # Determine ports to scan
    if args.all:
        ports = list(range(1, 65536))
    elif args.range:
        ports = parse_ports(args.range)
    elif args.ports:
        ports = parse_ports(args.ports)
    else:
        ports = sorted(COMMON_PORTS.keys())
    
    # Scan
    open_ports = scan_target(ip, ports, args.threads, args.timeout)
    
    # Summary
    if open_ports:
        print(f"\nSummary:")
        for p in open_ports:
            print(f"  {p['port']:>5}/tcp  {p['service']}")


if __name__ == '__main__':
    main()
