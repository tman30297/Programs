#!/usr/bin/env python3
"""
Network Latency Monitor - Track ping latency to hosts over time
Usage: python latency_monitor.py <host> [options]

Examples:
    python latency_monitor.py 8.8.8.8              Monitor Google DNS
    python latency_monitor.py google.com -w        Watch mode
    python latency_monitor.py 192.168.1.1 -c 10    Ping 10 times and exit
"""

import argparse
import subprocess
import time
import statistics
import sys
from datetime import datetime
import re


def ping_host(host, count=1, timeout=2):
    """Ping a host and return latency in ms, or None if failed."""
    try:
        result = subprocess.run(
            ['ping', '-c', str(count), '-W', str(timeout), host],
            capture_output=True, text=True, timeout=timeout + 1
        )
        
        # Parse output for latency
        # Example: "time=12.3 ms" or "time=1.23 ms"
        match = re.search(r'time[=<](\d+\.?\d*)\s*ms', result.stdout)
        if match:
            return float(match.group(1))
        
        return None
    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None


def ping_with_stats(host, count=4, timeout=2):
    """Ping multiple times and return statistics."""
    latencies = []
    
    for _ in range(count):
        latency = ping_host(host, count=1, timeout=timeout)
        if latency is not None:
            latencies.append(latency)
        time.sleep(0.5)  # Brief delay between pings
    
    if not latencies:
        return None
    
    return {
        'min': min(latencies),
        'max': max(latencies),
        'avg': statistics.mean(latencies),
        'median': statistics.median(latencies),
        'stdev': statistics.stdev(latencies) if len(latencies) > 1 else 0,
        'lost': count - len(latencies),
        'sent': count
    }


def format_latency(latency):
    """Format latency for display."""
    if latency is None:
        return "---"
    return f"{latency:>6.2f}"


def main():
    parser = argparse.ArgumentParser(
        description='Network Latency Monitor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python latency_monitor.py 8.8.8.8
  python latency_monitor.py google.com -w
  python latency_monitor.py 192.168.1.1 -c 5 --timeout 5
        '''
    )
    
    parser.add_argument('host', help='Target host or IP')
    parser.add_argument('-c', '--count', type=int, default=4,
                        help='Number of pings per check (default: 4)')
    parser.add_argument('-w', '--watch', action='store_true',
                        help='Continuous monitoring mode')
    parser.add_argument('-i', '--interval', type=int, default=3,
                        help='Interval between checks in watch mode (default: 3s)')
    parser.add_argument('-t', '--timeout', type=int, default=2,
                        help='Ping timeout in seconds (default: 2)')
    parser.add_argument('-o', '--output', type=str,
                        help='Save results to file')
    
    args = parser.parse_args()
    
    print(f"\n{'='*55}")
    print(f"  NETWORK LATENCY MONITOR")
    print(f"{'='*55}")
    print(f"Target: {args.host}")
    print(f"Pings per check: {args.count}")
    print(f"Timeout: {args.timeout}s")
    if args.watch:
        print(f"Watch mode: Yes (interval: {args.interval}s)")
    print(f"{'='*55}\n")
    
    history = []
    output_file = None
    
    if args.output:
        output_file = open(args.output, 'w')
        output_file.write(f"Latency Monitor - {datetime.now()}\n")
        output_file.write(f"Target: {args.host}\n")
        output_file.write("-" * 55 + "\n")
    
    def write_output(stats, timestamp):
        line = f"{timestamp} | min: {stats['min']:.2f}ms | max: {stats['max']:.2f}ms | avg: {stats['avg']:.2f}ms | lost: {stats['lost']}/{stats['sent']}\n"
        print(f"  {line.strip()}")
        if output_file:
            output_file.write(line)
    
    try:
        if args.watch:
            print(f"{'Time':<12} {'Min':<10} {'Max':<10} {'Avg':<10} {'Med':<10} {'Loss'}")
            print("-" * 60)
            
            while True:
                timestamp = datetime.now().strftime('%H:%M:%S')
                stats = ping_with_stats(args.host, args.count, args.timeout)
                
                if stats:
                    history.append(stats['avg'])
                    write_output(stats, timestamp)
                else:
                    print(f"  {timestamp} | No response (timeout)")
                    if output_file:
                        output_file.write(f"{timestamp} | No response\n")
                
                time.sleep(args.interval)
                
        else:
            # Single check
            print(f"Pinging {args.host}...")
            stats = ping_with_stats(args.host, args.count, args.timeout)
            
            if stats:
                print(f"\n--- {args.host} ping statistics ---")
                print(f"{stats['sent']} packets transmitted, {stats['sent'] - stats['lost']} received, "
                      f"{(stats['lost']/stats['sent']*100):.1f}% packet loss")
                print(f"round-trip min/avg/max/stddev = "
                      f"{stats['min']:.3f}/{stats['avg']:.3f}/{stats['max']:.3f}/{stats['stdev']:.3f} ms")
                
                history.append(stats['avg'])
                
                if output_file:
                    output_file.write(f"Result: min={stats['min']:.2f}ms avg={stats['avg']:.2f}ms max={stats['max']:.2f}ms\n")
            else:
                print("No response received")
                
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    
    if output_file:
        output_file.close()
    
    # Summary
    if len(history) > 1:
        print(f"\n--- Session Summary ---")
        print(f"Checks: {len(history)}")
        print(f"Min latency: {min(history):.2f} ms")
        print(f"Max latency: {max(history):.2f} ms")
        print(f"Avg latency: {statistics.mean(history):.2f} ms")


if __name__ == '__main__':
    main()
