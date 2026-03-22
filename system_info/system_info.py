#!/usr/bin/env python3
"""
System Info Gatherer
Gathers comprehensive system information and displays it in a readable format.
"""

import platform
import os
import socket
import psutil
import json
from datetime import datetime

def get_system_info():
    """Collect all system information."""
    info = {}
    
    # Basic OS Info
    info['os'] = {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'hostname': socket.gethostname(),
        'fqdn': socket.getfqdn(),
    }
    
    # CPU Info
    info['cpu'] = {
        'physical_cores': psutil.cpu_count(logical=False),
        'logical_cores': psutil.cpu_count(logical=True),
        'max_frequency': psutil.cpu_freq().max if psutil.cpu_freq() else 'N/A',
        'current_frequency': psutil.cpu_freq().current if psutil.cpu_freq() else 'N/A',
        'cpu_usage_percent': psutil.cpu_percent(interval=1),
        'per_cpu_usage': psutil.cpu_percent(interval=1, percpu=True),
    }
    
    # Memory Info
    mem = psutil.virtual_memory()
    info['memory'] = {
        'total_gb': round(mem.total / (1024**3), 2),
        'available_gb': round(mem.available / (1024**3), 2),
        'used_gb': round(mem.used / (1024**3), 2),
        'percent_used': mem.percent,
    }
    
    # Swap Memory
    swap = psutil.swap_memory()
    info['swap'] = {
        'total_gb': round(swap.total / (1024**3), 2),
        'used_gb': round(swap.used / (1024**3), 2),
        'percent_used': swap.percent,
    }
    
    # Disk Info
    partitions = psutil.disk_partitions()
    info['disk'] = {}
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            info['disk'][partition.device] = {
                'mountpoint': partition.mountpoint,
                'filesystem': partition.fstype,
                'total_gb': round(usage.total / (1024**3), 2),
                'used_gb': round(usage.used / (1024**3), 2),
                'free_gb': round(usage.free / (1024**3), 2),
                'percent_used': usage.percent,
            }
        except PermissionError:
            continue
    
    # Network Info
    info['network'] = {
        'interfaces': {},
    }
    addrs = psutil.net_if_addrs()
    for interface, addresses in addrs.items():
        info['network']['interfaces'][interface] = []
        for addr in addresses:
            if addr.family == socket.AF_INET:
                info['network']['interfaces'][interface].append({
                    'type': 'IPv4',
                    'address': addr.address,
                    'netmask': addr.netmask,
                })
            elif addr.family == socket.AF_INET6:
                info['network']['interfaces'][interface].append({
                    'type': 'IPv6',
                    'address': addr.address,
                })
    
    # Boot Time
    info['boot_time'] = datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')
    info['uptime'] = str(datetime.now() - datetime.fromtimestamp(psutil.boot_time()))
    
    # Battery (if available)
    if hasattr(psutil, 'sensors_battery'):
        battery = psutil.sensors_battery()
        if battery:
            info['battery'] = {
                'percent': battery.percent,
                'plugged_in': battery.power_plugged,
                'time_left': str(battery.secsleft) if battery.secsleft != psutil.POWER_TIME_UNLIMITED else 'N/A',
            }
    
    # Load Average (Linux only)
    if hasattr(os, 'getloadavg'):
        load_avg = os.getloadavg()
        info['load_average'] = {
            '1min': round(load_avg[0], 2),
            '5min': round(load_avg[1], 2),
            '15min': round(load_avg[2], 2),
        }
    
    return info

def print_system_info():
    """Print system info in a readable format."""
    info = get_system_info()
    
    print("=" * 60)
    print("        SYSTEM INFORMATION GATHERER")
    print("=" * 60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # OS Info
    print("📟 OPERATING SYSTEM")
    print("-" * 40)
    print(f"  System:     {info['os']['system']}")
    print(f"  Release:    {info['os']['release']}")
    print(f"  Version:    {info['os']['version']}")
    print(f"  Machine:    {info['os']['machine']}")
    print(f"  Hostname:   {info['os']['hostname']}")
    print(f"  Uptime:     {info['uptime']}")
    print()
    
    # CPU Info
    print("⚙️  CPU")
    print("-" * 40)
    print(f"  Physical Cores:  {info['cpu']['physical_cores']}")
    print(f"  Logical Cores:  {info['cpu']['logical_cores']}")
    print(f"  Current Usage:  {info['cpu']['cpu_usage_percent']}%")
    if info.get('load_average'):
        print(f"  Load Average:   {info['load_average']['1min']}, {info['load_average']['5min']}, {info['load_average']['15min']}")
    print()
    
    # Memory
    print("💾 MEMORY")
    print("-" * 40)
    print(f"  Total:     {info['memory']['total_gb']} GB")
    print(f"  Available: {info['memory']['available_gb']} GB")
    print(f"  Used:      {info['memory']['used_gb']} GB ({info['memory']['percent_used']}%)")
    print(f"  Swap:      {info['swap']['total_gb']} GB ({info['swap']['percent_used']}%)")
    print()
    
    # Disk
    print("💿 DISK")
    print("-" * 40)
    for device, disk_info in info['disk'].items():
        print(f"  {device}")
        print(f"    Mount:     {disk_info['mountpoint']}")
        print(f"    Total:     {disk_info['total_gb']} GB")
        print(f"    Used:      {disk_info['used_gb']} GB ({disk_info['percent_used']}%)")
        print(f"    Free:      {disk_info['free_gb']} GB")
    print()
    
    # Network
    print("🌐 NETWORK")
    print("-" * 40)
    for interface, addresses in info['network']['interfaces'].items():
        if addresses:
            print(f"  {interface}:")
            for addr in addresses:
                print(f"    {addr['type']}: {addr['address']}")
    print()
    
    # Battery
    if info.get('battery'):
        print("🔋 BATTERY")
        print("-" * 40)
        print(f"  Charge:    {info['battery']['percent']}%")
        print(f"  Plugged:   {info['battery']['plugged_in']}")
        print()
    
    print("=" * 60)

def export_json():
    """Export system info as JSON."""
    info = get_system_info()
    print(json.dumps(info, indent=2, default=str))

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--json':
        export_json()
    else:
        print_system_info()
