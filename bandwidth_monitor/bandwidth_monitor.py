#!/usr/bin/env python3
"""
Network Bandwidth Monitor - Track network interface bandwidth usage
Usage: python bandwidth_monitor.py [interface] [options]

Examples:
    python bandwidth_monitor.py              Monitor all interfaces
    python bandwidth_monitor.py eth0        Monitor specific interface
    python bandwidth_monitor.py -w          Watch mode
    python bandwidth_monitor.py -i 5        5 second interval
"""

import argparse
import os
import time
import sys


def get_interface_stats():
    """Get network stats for all interfaces."""
    stats = {}
    
    try:
        with open('/proc/net/dev', 'r') as f:
            lines = f.readlines()
        
        # Skip header lines
        for line in lines[2:]:
            parts = line.split()
            if len(parts) >= 10:
                iface = parts[0].rstrip(':')
                # Skip loopback
                if iface != 'lo':
                    stats[iface] = {
                        'rx_bytes': int(parts[1]),
                        'rx_packets': int(parts[2]),
                        'rx_errors': int(parts[3]),
                        'tx_bytes': int(parts[9]),
                        'tx_packets': int(parts[10]),
                        'tx_errors': int(parts[11])
                    }
    except Exception as e:
        pass
    
    return stats


def format_bytes(bytes_val):
    """Format bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024:
            return f"{bytes_val:.1f}{unit}"
        bytes_val /= 1024
    return f"{bytes_val:.2f}PB"


def format_rate(bytes_per_sec):
    """Format bytes per second."""
    if bytes_per_sec < 1024:
        return f"{bytes_per_sec:.0f} B/s"
    elif bytes_per_sec < 1024 * 1024:
        return f"{bytes_per_sec/1024:.1f} KB/s"
    elif bytes_per_sec < 1024 * 1024 * 1024:
        return f"{bytes_per_sec/(1024*1024):.2f} MB/s"
    else:
        return f"{bytes_per_sec/(1024*1024*1024):.2f} GB/s"


def calculate_rates(old_stats, new_stats, interval):
    """Calculate transfer rates."""
    rates = {}
    
    for iface in new_stats:
        if iface in old_stats:
            rx_bytes = new_stats[iface]['rx_bytes'] - old_stats[iface]['rx_bytes']
            tx_bytes = new_stats[iface]['tx_bytes'] - old_stats[iface]['tx_bytes']
            
            rx_rate = rx_bytes / interval if interval > 0 else 0
            tx_rate = tx_bytes / interval if interval > 0 else 0
            
            rates[iface] = {
                'rx_rate': rx_rate,
                'tx_rate': tx_rate,
                'total_rate': rx_rate + tx_rate,
                'rx_total': new_stats[iface]['rx_bytes'],
                'tx_total': new_stats[iface]['tx_bytes']
            }
        else:
            rates[iface] = {
                'rx_rate': 0,
                'tx_rate': 0,
                'total_rate': 0,
                'rx_total': new_stats[iface]['rx_bytes'],
                'tx_total': new_stats[iface]['tx_bytes']
            }
    
    return rates


def main():
    parser = argparse.ArgumentParser(
        description='Network Bandwidth Monitor'
    )
    
    parser.add_argument('interface', nargs='?', help='Network interface to monitor')
    parser.add_argument('-w', '--watch', action='store_true',
                        help='Continuous monitoring')
    parser.add_argument('-i', '--interval', type=int, default=2,
                        help='Update interval in seconds (default: 2)')
    
    args = parser.parse_args()
    
    print(f"\n{'='*70}")
    print("  NETWORK BANDWIDTH MONITOR")
    print(f"{'='*70}")
    print(f"Interface: {args.interface if args.interface else 'all'}")
    print(f"Interval: {args.interval}s")
    print(f"{'='*70}\n")
    
    old_stats = None
    
    try:
        first = True
        
        while True:
            # Get current stats
            new_stats = get_interface_stats()
            
            if old_stats is not None:
                # Calculate rates
                rates = calculate_rates(old_stats, new_stats, args.interval)
                
                print(f"\n[{time.strftime('%H:%M:%S')}]")
                print(f"{'Interface':<12} {'↓ RX Rate':<15} {'↑ TX Rate':<15} {'Total':<15}")
                print("-" * 60)
                
                for iface, data in sorted(rates.items()):
                    # Filter by interface if specified
                    if args.interface and iface != args.interface:
                        continue
                    
                    rx_rate = format_rate(data['rx_rate'])
                    tx_rate = format_rate(data['tx_rate'])
                    total_rate = format_rate(data['total_rate'])
                    
                    print(f"{iface:<12} {rx_rate:<15} {tx_rate:<15} {total_rate:<15}")
                
                # Summary
                total_rx = sum(d['rx_rate'] for d in rates.values())
                total_tx = sum(d['tx_rate'] for d in rates.values())
                
                if not args.interface:
                    print("-" * 60)
                    print(f"{'TOTAL':<12} {format_rate(total_rx):<15} {format_rate(total_tx):<15} {format_rate(total_rx + total_tx):<15}")
            else:
                if first:
                    # Show initial state on first iteration
                    rates = {}
                    for iface, data in new_stats.items():
                        if args.interface and iface != args.interface:
                            continue
                        rates[iface] = {
                            'rx_rate': 0,
                            'tx_rate': 0,
                            'total_rate': 0,
                            'rx_total': data['rx_bytes'],
                            'tx_total': data['tx_bytes']
                        }
                    
                    if rates:
                        print(f"\n[{time.strftime('%H:%M:%S')}] (Initial state)")
                        print(f"{'Interface':<12} {'Total RX':<15} {'Total TX':<15}")
                        print("-" * 45)
                        for iface, data in sorted(rates.items()):
                            print(f"{iface:<12} {format_bytes(data['rx_total']):<15} {format_bytes(data['tx_total']):<15}")
                    first = False
            
            old_stats = new_stats
            
            if not args.watch:
                break
            
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print("\n\nStopped")


if __name__ == '__main__':
    main()
