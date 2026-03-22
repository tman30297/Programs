#!/usr/bin/env python3
"""
Quick Service Checker - Check if common services are running on a host
Usage: python service_checker.py <ip> [options]

Examples:
    python service_checker.py 192.168.1.1              Check common ports
    python service_checker.py localhost -v              Verbose output
    python service_checker.py 192.168.1.1 --quick     Quick scan (fewer ports)
"""

import socket
import argparse
import concurrent.futures
from datetime import datetime

# Common services with their default ports
COMMON_SERVICES = {
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
    6379: "Redis",
    8080: "HTTP-Alt",
    8443: "HTTPS-Alt",
    9200: "Elasticsearch",
    27017: "MongoDB"
}

# Quick scan - fewer ports
QUICK_SERVICES = {
    22: "SSH",
    80: "HTTP",
    443: "HTTPS",
    3389: "RDP",
    8080: "HTTP-Alt"
}


def check_port(ip, port, timeout=1):
    """Check if a port is open on the target IP."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False


def check_service(ip, port, service_name, timeout=1):
    """Check a single service."""
    is_open = check_port(ip, port, timeout)
    return {
        'port': port,
        'service': service_name,
        'status': 'open' if is_open else 'closed'
    }


def main():
    parser = argparse.ArgumentParser(
        description='Quick Service Checker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python service_checker.py 192.168.1.1
  python service_checker.py localhost -v
  python service_checker.py 192.168.1.1 --quick
        '''
    )
    
    parser.add_argument('host', help='Target IP or hostname')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show all ports (not just open ones)')
    parser.add_argument('-q', '--quick', action='store_true',
                        help='Quick scan (fewer common ports)')
    parser.add_argument('-t', '--timeout', type=int, default=1,
                        help='Connection timeout (default: 1s)')
    parser.add_argument('-p', '--ports', type=str,
                        help='Custom ports (comma-separated, e.g., 22,80,443)')
    
    args = parser.parse_args()
    
    # Resolve hostname
    try:
        ip = socket.gethostbyname(args.host)
    except socket.gaierror:
        print(f"Error: Could not resolve {args.host}")
        return
    
    # Determine which services to check
    if args.ports:
        # Custom ports
        services = {}
        for port_str in args.ports.split(','):
            try:
                port = int(port_str.strip())
                services[port] = socket.getservbyport(port) if port < 65536 else f"port-{port}"
            except:
                services[port] = f"port-{port}"
    elif args.quick:
        services = QUICK_SERVICES
    else:
        services = COMMON_SERVICES
    
    print(f"\n{'='*55}")
    print("  QUICK SERVICE CHECKER")
    print(f"{'='*55}")
    print(f"Target: {args.host} ({ip})")
    print(f"Scanning {len(services)} port(s)...")
    print(f"{'='*55}\n")
    
    # Check ports in parallel
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {
            executor.submit(check_service, ip, port, service_name, args.timeout): (port, service_name)
            for port, service_name in services.items()
        }
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
    
    # Sort by port
    results.sort(key=lambda x: x['port'])
    
    # Display results
    open_count = 0
    for r in results:
        if r['status'] == 'open':
            open_count += 1
            print(f"  [OPEN] {r['port']:>5}/tcp  {r['service']}")
        elif args.verbose:
            print(f"  [CLOSED] {r['port']:>5}/tcp  {r['service']}")
    
    print(f"\n{'='*55}")
    print(f"Scan complete: {open_count} open port(s) found")
    print(f"{'='*55}")


if __name__ == '__main__':
    main()
