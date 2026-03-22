#!/usr/bin/env python3
"""
Enhanced Network Analyzer Tool for Ethical Hacking Education
Combines DNS query monitoring, packet analysis, and traffic statistics.

Features:
  - Device discovery on local network
  - DNS query monitoring (real-time + historical)
  - Packet capture and analysis (tcpdump + scapy fallback)
  - Traffic statistics and top talkers
  - Export to JSON/CSV
  - GeoIP lookup for external IPs
"""

import argparse
import csv
import json
import os
import re
import socket
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
import signal


# ============================================================================
# Device Discovery Functions
# ============================================================================

def scan_network_devices():
    """Scan local network for connected devices."""
    print("\n" + "="*70)
    print("DISCOVERED DEVICES")
    print("="*70)
    
    devices = []
    
    # Get local network range
    try:
        result = subprocess.run(['ip', 'route', 'show', 'default'], 
                              capture_output=True, text=True, timeout=5)
        gateway_match = re.search(r'via\s+(\d+\.\d+\.\d+\.\d+)', result.stdout)
        
        if not gateway_match:
            print("   Could not determine network gateway.")
            return []
        
        gateway_ip = gateway_match.group(1)
        
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, timeout=5)
        local_ip = result.stdout.strip().split()[0] if result.stdout.strip() else None
        
        if not local_ip:
            print("   Could not determine local IP.")
            return []
        
        network_prefix = '.'.join(local_ip.split('.')[:-1])
        
    except Exception as e:
        print(f"   Error determining network: {e}")
        return []
    
    # Try ARP scan first
    try:
        result = subprocess.run(['arp', '-a'], capture_output=True, text=True, timeout=10)
        
        for line in result.stdout.split('\n'):
            match = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+at\s+([0-9a-f:]+)', line, re.IGNORECASE)
            if match:
                ip = match.group(1)
                if ip != 'ff:ff:ff:ff:ff:ff' and ip != gateway_ip:
                    devices.append({'ip': ip, 'mac': match.group(2)})
    except Exception:
        pass
    
    # Fallback to nmap if ARP didn't work
    if len(devices) < 2:
        try:
            result = subprocess.run(
                ['nmap', '-sn', '-PR', f'{network_prefix}.1-254', '-oG', '-'],
                capture_output=True, text=True, timeout=30
            )
            
            for line in result.stdout.split('\n'):
                match = re.search(r'Host:\s+(\d+\.\d+\.\d+\.\d+).*Status:\s+Up', line)
                if match:
                    ip = match.group(1)
                    if not any(d['ip'] == ip for d in devices):
                        devices.append({'ip': ip, 'mac': None})
        except Exception:
            pass
    
    # Get hostnames and device types
    for device in devices:
        ip = device['ip']
        hostname = ip
        
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except:
            try:
                result = subprocess.run(
                    ['nmap', '-sn', '-R', '--dns-server', '8.8.8.8', ip],
                    capture_output=True, text=True, timeout=5
                )
                match = re.search(r'Nmap scan report for\s+(\S+)', result.stdout)
                if match:
                    potential = match.group(1)
                    if not re.match(r'^\d+\.\d+\.\d+\.\d+$', potential):
                        hostname = potential
            except:
                pass
        
        device['hostname'] = hostname
        device['type'] = determine_device_type(hostname)
    
    devices.sort(key=lambda x: [int(o) for o in x['ip'].split('.')])
    
    if devices:
        print(f"{'IP':<18} {'Hostname':<26} {'Type':<15}")
        print("-" * 60)
        for dev in devices:
            print(f"{dev['ip']:<18} {dev['hostname']:<26} {dev['type']:<15}")
        print(f"\nTotal devices found: {len(devices)}")
    else:
        print("   No devices found on network.")
    
    return devices


def determine_device_type(hostname):
    """Determine device type based on hostname patterns."""
    hostname_lower = hostname.lower()
    
    patterns = [
        (['roku', 'tv', 'hisense', 'tcl', 'samsung tv', 'lg tv', 'chromecast', 'firetv'], "TV"),
        (['iphone', 'ipad', 'android', 'phone', 'mobile', 'pixel', 'galaxy'], "Phone/Tablet"),
        (['linux', 'pc', 'desktop', 'macbook', 'imac', 'workstation', 'server'], "Computer"),
        (['tuya', 'ipc', 'camera', 'nvr', 'dvr', 'webcam', 'nest', 'ring', 'doorbell'], "IoT Camera"),
        (['printer', 'hp', 'canon', 'epson', 'brother'], "Printer"),
        (['playstation', 'xbox', 'nintendo', 'switch'], "Gaming"),
        (['speaker', 'echo', 'homepod', 'sonos', 'soundbar'], "Smart Speaker"),
        (['router', 'gateway', 'netgear', 'tp-link', 'asus'], "Router"),
    ]
    
    for keywords, device_type in patterns:
        if any(p in hostname_lower for p in keywords):
            return device_type
    
    return "Unknown"


# ============================================================================
# DNS Query Functions
# ============================================================================

def get_realtime_dns_queries(duration=5):
    """Monitor DNS queries in real-time using tcpdump."""
    try:
        cmd = ['tcpdump', '-i', 'any', '-c', '100', '-n', 'port', '53', '-l']
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        queries = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            line = proc.stdout.readline()
            if not line:
                break
            
            match = re.search(r'(\d+:\d+:\d+\.\d+).*IP\s+(\d+\.\d+\.\d+\.\d+)\.\d+.*\?\s*(\S+)\.', line)
            if match:
                queries.append({
                    'timestamp': match.group(1),
                    'source_ip': match.group(2),
                    'domain': match.group(3).rstrip('.')
                })
        
        proc.terminate()
        return queries
        
    except FileNotFoundError:
        print("   tcpdump not found.")
        return []
    except Exception as e:
        return []


def parse_syslog_dns():
    """Parse /var/log/syslog for DNS queries."""
    dns_queries = []
    
    log_files = ['/var/log/syslog', '/var/log/messages']
    log_data = ""
    
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                log_data = ''.join(lines[-2000:])
                break
        except:
            continue
    
    if not log_data:
        return dns_queries
    
    patterns = [
        r'(\w+\s+\d+\s+\d+:\d+:\d+).*query\[A\]\s+(\S+)\s+from\s+(\d+\.\d+\.\d+\.\d+)',
    ]
    
    for line in log_data.split('\n'):
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 3:
                    timestamp = groups[0]
                    possible_ip = groups[2] if re.match(r'\d+\.\d+\.\d+\.\d+', groups[2]) else groups[1]
                    possible_domain = groups[1] if possible_ip == groups[2] else groups[2]
                    
                    if re.match(r'\d+\.\d+\.\d+\.\d+', possible_ip):
                        dns_queries.append({
                            'timestamp': timestamp,
                            'source_ip': possible_ip,
                            'domain': possible_domain
                        })
                        break
    
    return dns_queries[-50:]


def display_dns_queries(queries, output_file=None):
    """Display DNS query results."""
    print("\n" + "="*70)
    print("DNS QUERY MONITOR")
    print("="*70)
    
    if not queries:
        print("No DNS queries found.")
        return
    
    print(f"{'Timestamp':<15} {'Source IP':<18} {'Queried Domain':<35}")
    print("-"*70)
    
    for q in queries:
        print(f"{q['timestamp']:<15} {q['source_ip']:<18} {q['domain'][:35]:<35}")
    
    # Summary
    domains = [q['domain'] for q in queries]
    ips = [q['source_ip'] for q in queries]
    tlds = [d.split('.')[-1] if '.' in d else '' for d in domains]
    
    print("\n--- Summary ---")
    print(f"Total DNS queries: {len(queries)}")
    print(f"Unique domains: {len(set(domains))}")
    print(f"Unique source IPs: {len(set(ips))}")
    print(f"Top TLDs: {Counter(tlds).most_common(5)}")
    print(f"Top domains: {Counter(domains).most_common(5)}")


# ============================================================================
# Packet Capture Functions
# ============================================================================

def capture_packets_tcpdump(duration=5):
    """Capture packet metadata using tcpdump with enhanced analysis."""
    try:
        cmd = ['tcpdump', '-i', 'any', '-c', '200', '-n', '-q', '-l']
        
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        packets_data = {
            'protocols': Counter(),
            'ip_pairs': Counter(),
            'packet_sizes': [],
            'total_bytes': 0,
            'ports': Counter(),
            'total_packets': 0
        }
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            line = proc.stdout.readline()
            if not line:
                break
            
            line = line.strip()
            packets_data['total_packets'] += 1
            
            # Protocol detection
            if 'TCP' in line:
                packets_data['protocols']['TCP'] += 1
            elif 'UDP' in line:
                packets_data['protocols']['UDP'] += 1
            elif 'ICMP' in line:
                packets_data['protocols']['ICMP'] += 1
            else:
                packets_data['protocols']['Other'] += 1
            
            # Extract IPs
            ip_matches = re.findall(r'\b(\d+\.\d+\.\d+\.\d+)\b', line)
            if len(ip_matches) >= 2:
                pair = tuple(sorted(ip_matches[:2]))
                packets_data['ip_pairs'][pair] += 1
            
            # Extract ports for TCP/UDP
            port_matches = re.findall(r'\.(\d+):|\s(\d+)\s', line)
            for pm in port_matches:
                for p in pm:
                    if p and p.isdigit():
                        port = int(p)
                        if port < 65536:
                            packets_data['ports'][port] += 1
            
            # Try to get packet size
            size_match = re.search(r'length\s*(\d+)', line)
            if size_match:
                size = int(size_match.group(1))
                packets_data['packet_sizes'].append(size)
                packets_data['total_bytes'] += size
        
        proc.terminate()
        
        return packets_data
        
    except FileNotFoundError:
        print("   tcpdump not found.")
        return None
    except Exception as e:
        return None


def capture_packets_scapy(duration=5):
    """Capture packet metadata using scapy (fallback)."""
    try:
        from scapy.all import sniff, IP, TCP, UDP, ICMP
        
        packets_data = {
            'protocols': Counter(),
            'ip_pairs': Counter(),
            'packet_sizes': [],
            'total_bytes': 0,
            'ports': Counter(),
            'total_packets': 0
        }
        
        def process_packet(pkt):
            if IP in pkt:
                packets_data['total_packets'] += 1
                
                src = pkt[IP].src
                dst = pkt[IP].dst
                size = len(pkt)
                
                packets_data['packet_sizes'].append(size)
                packets_data['total_bytes'] += size
                
                if TCP in pkt:
                    packets_data['protocols']['TCP'] += 1
                    packets_data['ports'][pkt[TCP].sport] += 1
                    packets_data['ports'][pkt[TCP].dport] += 1
                elif UDP in pkt:
                    packets_data['protocols']['UDP'] += 1
                    packets_data['ports'][pkt[UDP].sport] += 1
                    packets_data['ports'][pkt[UDP].dport] += 1
                elif ICMP in pkt:
                    packets_data['protocols']['ICMP'] += 1
                else:
                    packets_data['protocols']['Other'] += 1
                
                pair = tuple(sorted([src, dst]))
                packets_data['ip_pairs'][pair] += 1
        
        sniff(prn=process_packet, timeout=duration, store=False)
        
        return packets_data
        
    except ImportError:
        print("   scapy not installed.")
        return None
    except Exception as e:
        return None


def display_packet_summary(data, output_file=None):
    """Display enhanced packet analysis results."""
    print("\n" + "="*70)
    print("PACKET SNIFFER SUMMARY")
    print("="*70)
    
    if not data or data['total_packets'] == 0:
        print("No packet data captured.")
        return
    
    print(f"\nTotal Packets: {data['total_packets']}")
    print(f"Total Data: {data['total_bytes']:,} bytes ({data['total_bytes']/1024:.1f} KB)")
    
    # Protocol distribution
    print("\n--- Protocol Distribution ---")
    for proto, count in data['protocols'].most_common():
        pct = (count / data['total_packets'] * 100) if data['total_packets'] > 0 else 0
        bar = '█' * int(pct / 2)
        print(f"  {proto:<10} {count:>6} ({pct:>5.1f}%) {bar}")
    
    # Packet size stats
    if data['packet_sizes']:
        sizes = data['packet_sizes']
        avg_size = sum(sizes) / len(sizes)
        min_size = min(sizes)
        max_size = max(sizes)
        
        # Calculate percentiles
        sorted_sizes = sorted(sizes)
        p50 = sorted_sizes[len(sorted_sizes)//2]
        p95 = sorted_sizes[int(len(sorted_sizes)*0.95)]
        
        print(f"\n--- Packet Size Statistics ---")
        print(f"  Min: {min_size} bytes | Max: {max_size} bytes | Avg: {avg_size:.1f} bytes")
        print(f"  Median (P50): {p50} bytes | P95: {p95} bytes")
    
    # Top ports
    print("\n--- Top Ports (by packet count) ---")
    common_ports = {
        22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS", 80: "HTTP",
        110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB", 993: "IMAPS",
        995: "POP3S", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL",
        8080: "HTTP-Alt", 8443: "HTTPS-Alt"
    }
    
    for port, count in data['ports'].most_common(10):
        service = common_ports.get(port, "Unknown")
        print(f"  {port:<6} ({service:<12}) - {count} packets")
    
    # Top talkers
    print("\n--- Top Talkers (IP Pairs) ---")
    if data['ip_pairs']:
        print(f"{'Rank':<6} {'Source':<18} {'Dest':<18} {'Packets':<10}")
        print("-" * 52)
        for i, (pair, count) in enumerate(data['ip_pairs'].most_common(10), 1):
            src, dst = pair
            print(f"{i:<6} {src:<18} {dst:<18} {count:<10}")
    else:
        print("No IP pairs captured.")


# ============================================================================
# Export Functions
# ============================================================================

def export_to_json(data, filename):
    """Export analysis data to JSON file."""
    # Convert Counter objects to dicts for JSON serialization
    export_data = {}
    
    if 'dns_queries' in data:
        export_data['dns_queries'] = data['dns_queries']
    
    if 'packets' in data and data['packets']:
        pkt = data['packets']
        export_data['packets'] = {
            'total_packets': pkt['total_packets'],
            'total_bytes': pkt['total_bytes'],
            'protocols': dict(pkt['protocols']),
            'ip_pairs': {f"{k[0]}<->{k[1]}": v for k, v in pkt['ip_pairs'].most_common(20)},
            'ports': dict(pkt['ports'].most_common(20)),
            'packet_sizes': {
                'count': len(pkt['packet_sizes']),
                'min': min(pkt['packet_sizes']) if pkt['packet_sizes'] else 0,
                'max': max(pkt['packet_sizes']) if pkt['packet_sizes'] else 0,
                'avg': sum(pkt['packet_sizes']) / len(pkt['packet_sizes']) if pkt['packet_sizes'] else 0
            }
        }
    
    with open(filename, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"  Exported to: {filename}")


def export_to_csv(data, filename):
    """Export DNS queries to CSV file."""
    if 'dns_queries' not in data or not data['dns_queries']:
        print("  No DNS queries to export.")
        return
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'source_ip', 'domain'])
        
        for q in data['dns_queries']:
            writer.writerow([q['timestamp'], q['source_ip'], q['domain']])
    
    print(f"  Exported to: {filename}")


# ============================================================================
# Main Execution
# ============================================================================

def check_root():
    """Check if script is running with sudo/root privileges."""
    if os.geteuid() != 0:
        print("⚠️  WARNING: This script works best with sudo/root privileges.")
        print("   Run with: sudo python net_analyzer.py [options]")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Enhanced Network Analyzer for Ethical Hacking Education',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  sudo python net_analyzer.py              Single scan (all)
  sudo python net_analyzer.py --watch     Real-time monitoring
  sudo python net_analyzer.py --dns-only  DNS queries only
  sudo python net_analyzer.py --pcap-only  Packets only
  sudo python net_analyzer.py -o output   Save to JSON
  sudo python net_analyzer.py --csv dns.csv  Export DNS to CSV
        '''
    )
    
    parser.add_argument('--watch', '-w', action='store_true',
                        help='Real-time monitoring mode')
    parser.add_argument('--dns-only', '-d', action='store_true',
                        help='Show DNS queries only')
    parser.add_argument('--pcap-only', '-p', action='store_true',
                        help='Show packet analysis only')
    parser.add_argument('--output', '-o', type=str,
                        help='Save output to JSON file')
    parser.add_argument('--csv', type=str,
                        help='Export DNS queries to CSV file')
    parser.add_argument('--duration', type=int, default=5,
                        help='Capture duration in seconds (default: 5)')
    
    args = parser.parse_args()
    
    is_root = check_root()
    
    if not is_root:
        print("\n⚠️  Continuing without root - some features may be limited.\n")
    
    # Data storage for export
    analysis_data = {}
    
    # Scan for network devices
    devices = scan_network_devices()
    
    dns_only = args.dns_only
    pcap_only = args.pcap_only
    
    if not dns_only and not pcap_only:
        dns_only = True
        pcap_only = True
    
    if args.watch:
        print("\n📡 Real-time Monitoring Mode (Ctrl+C to stop)")
        print(f"   Duration per cycle: {args.duration}s\n")
        
        try:
            cycle = 1
            while True:
                print(f"\n{'='*70}")
                print(f"CYCLE {cycle} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*70)
                
                if dns_only:
                    queries = get_realtime_dns_queries(args.duration)
                    if not queries:
                        queries = parse_syslog_dns()
                    display_dns_queries(queries)
                    if args.output:
                        analysis_data['dns_queries'] = queries
                
                if pcap_only:
                    packet_data = capture_packets_tcpdump(args.duration)
                    if not packet_data:
                        packet_data = capture_packets_scapy(args.duration)
                    display_packet_summary(packet_data)
                    if args.output:
                        analysis_data['packets'] = packet_data
                
                # Export if requested
                if args.output and cycle == 1:
                    export_to_json(analysis_data, args.output)
                if args.csv and cycle == 1:
                    export_to_csv(analysis_data, args.csv)
                
                cycle += 1
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Stopped by user")
            
    else:
        print("\n📊 Snapshot Mode\n")
        
        if dns_only:
            print("--- Capturing DNS Queries ---")
            queries = get_realtime_dns_queries(args.duration)
            if not queries:
                queries = parse_syslog_dns()
            display_dns_queries(queries)
            analysis_data['dns_queries'] = queries
        
        if pcap_only:
            print("\n--- Capturing Packets ---")
            packet_data = capture_packets_tcpdump(args.duration)
            if not packet_data:
                packet_data = capture_packets_scapy(args.duration)
            display_packet_summary(packet_data)
            analysis_data['packets'] = packet_data
    
    # Export final results
    if args.output:
        export_to_json(analysis_data, args.output)
    if args.csv:
        export_to_csv(analysis_data, args.csv)
    
    if args.output or args.csv:
        print(f"\n✅ Results saved")
    
    print("\n✨ Analysis complete!")


if __name__ == '__main__':
    main()
