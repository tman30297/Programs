#!/usr/bin/env python3
"""
System Dashboard - Unified view of system metrics
Shows: CPU, Memory, Disk, Network, Top Processes, System Info
"""

import os
import sys
import time
import argparse
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple

# Try to import optional modules
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class Colors:
    """ANSI color codes"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    
    # Background
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'

def get_cpu_usage() -> Tuple[float, List[float], float]:
    """Get CPU usage (user, system, idle)"""
    if PSUTIL_AVAILABLE:
        # First call initializes, second call gets actual value
        psutil.cpu_percent(interval=None)
        time.sleep(0.1)
        total = psutil.cpu_percent(interval=0.1)
        per_cpu = psutil.cpu_percent(interval=0.1, percpu=True)
        return total, per_cpu, 100 - total
    
    try:
        with open('/proc/stat', 'r') as f:
            line = f.readline()
            fields = line.split()
            user, nice, system, idle = map(int, fields[1:5])
            total = user + nice + system + idle
            idle_pct = (idle / total) * 100
            active_pct = 100 - idle_pct
            return active_pct, [active_pct / 3] * 3, idle_pct
    except:
        return 0, [0], 100

def get_memory_info() -> Dict:
    """Get memory information"""
    if PSUTIL_AVAILABLE:
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'percent': mem.percent,
            'swap_total': swap.total,
            'swap_used': swap.used,
            'swap_percent': swap.percent
        }
    
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
        
        def get_kb(key):
            for line in lines:
                if line.startswith(key):
                    return int(line.split()[1]) * 1024
            return 0
        
        total = get_kb('MemTotal:')
        available = get_kb('MemAvailable:')
        if available == 0:
            free = get_kb('MemFree:')
            buffers = get_kb('Buffers:')
            cached = get_kb('Cached:')
            available = free + buffers + cached
        
        used = total - available
        return {
            'total': total,
            'available': available,
            'used': used,
            'percent': (used / total) * 100 if total else 0,
            'swap_total': get_kb('SwapTotal:'),
            'swap_used': get_kb('SwapUsed:'),
            'swap_percent': 0
        }
    except:
        return {'total': 0, 'available': 0, 'used': 0, 'percent': 0, 'swap_total': 0, 'swap_used': 0, 'swap_percent': 0}

def get_disk_usage() -> List[Dict]:
    """Get disk usage for mounted volumes"""
    if PSUTIL_AVAILABLE:
        partitions = psutil.disk_partitions()
        result = []
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                # Skip snap, tmpfs, devtmpfs, and small filesystems
                if any(x in partition.mountpoint for x in ['/snap', '/run', '/dev', '/sys']) and usage.total < 1024*1024*1024:
                    continue
                result.append({
                    'device': partition.device,
                    'mount': partition.mountpoint,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                })
            except:
                pass
        return result
    
    # Fallback: use df command
    try:
        result = []
        df_output = subprocess.check_output(['df', '-BG'], text=True)
        lines = df_output.strip().split('\n')[1:]  # Skip header
        for line in lines:
            fields = line.split()
            if len(fields) >= 6:
                device = fields[0]
                mount = fields[5] if len(fields) > 5 else ''
                if mount.startswith('/'):
                    try:
                        total = int(fields[1].replace('G', '')) * (1024**3)
                        used = int(fields[2].replace('G', '')) * (1024**3)
                        free = int(fields[3].replace('G', '')) * (1024**3)
                        percent = int(fields[4].replace('%', ''))
                        result.append({
                            'device': device,
                            'mount': mount,
                            'total': total,
                            'used': used,
                            'free': free,
                            'percent': percent
                        })
                    except:
                        pass
        return result
    except:
        return []

def get_network_stats() -> Dict:
    """Get network I/O statistics"""
    if PSUTIL_AVAILABLE:
        net = psutil.net_io_counters()
        return {
            'bytes_sent': net.bytes_sent,
            'bytes_recv': net.bytes_recv,
            'packets_sent': net.packets_sent,
            'packets_recv': net.packets_recv,
            'errin': net.errin,
            'errout': net.errout,
            'dropin': net.dropin,
            'dropout': net.dropout
        }
    
    # Fallback
    try:
        with open('/proc/net/dev', 'r') as f:
            lines = f.readlines()[2:]  # Skip headers
        
        total_recv = 0
        total_sent = 0
        for line in lines:
            fields = line.split()
            if len(fields) >= 11:
                iface = fields[0].replace(':', '')
                if iface not in ['lo', 'docker0', 'veth']:
                    try:
                        total_recv += int(fields[1])
                        total_sent += int(fields[9])
                    except:
                        pass
        
        return {
            'bytes_sent': total_sent,
            'bytes_recv': total_recv,
            'packets_sent': 0,
            'packets_recv': 0,
            'errin': 0,
            'errout': 0,
            'dropin': 0,
            'dropout': 0
        }
    except:
        return {'bytes_sent': 0, 'bytes_recv': 0, 'packets_sent': 0, 'packets_recv': 0, 'errin': 0, 'errout': 0, 'dropin': 0, 'dropout': 0}

def get_top_processes(n: int = 5) -> List[Dict]:
    """Get top processes by CPU/Memory"""
    if PSUTIL_AVAILABLE:
        # First call initializes CPU tracking for all processes
        for p in psutil.process_iter(['pid', 'cpu_percent']):
            try:
                p.cpu_percent(interval=None)
            except:
                pass
        
        # Wait a bit for CPU measurement
        time.sleep(0.2)
        
        # Now get actual values
        processes = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                info = p.info
                info['cpu_percent'] = info.get('cpu_percent') or 0
                info['memory_percent'] = info.get('memory_percent') or 0
                processes.append(info)
            except:
                pass
        
        # Sort by CPU
        by_cpu = sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:n]
        return by_cpu
    
    # Fallback: use ps command
    try:
        ps_output = subprocess.check_output(
            ['ps', 'aux', '--sort=-%cpu'],
            text=True
        ).strip().split('\n')[1:n+1]
        
        processes = []
        for line in ps_output:
            fields = line.split()
            if len(fields) >= 11:
                processes.append({
                    'pid': fields[1],
                    'name': fields[10][:20] if len(fields) > 10 else '?',
                    'cpu_percent': float(fields[2]),
                    'memory_percent': float(fields[3]),
                    'status': fields[7] if len(fields) > 7 else '?'
                })
        return processes
    except:
        return []

def get_battery_info() -> Dict:
    """Get battery status"""
    if PSUTIL_AVAILABLE:
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percent': battery.percent,
                    'charging': battery.is_plugged_in,
                    'time_left': battery.secsleft if battery.secsleft > 0 else None
                }
        except:
            pass
    
    # Try reading from /sys
    try:
        with open('/sys/class/power_supply/BAT0/capacity', 'r') as f:
            percent = int(f.read().strip())
        
        charging = False
        try:
            with open('/sys/class/power_supply/BAT0/status', 'r') as f:
                status = f.read().strip().lower()
                charging = 'charging' in status or 'plugged' in status
        except:
            pass
        
        return {'percent': percent, 'charging': charging, 'time_left': None}
    except:
        return {'percent': None, 'charging': None, 'time_left': None}

def get_load_average() -> Tuple[float, float, float]:
    """Get system load average"""
    try:
        load = os.getloadavg()
        return load
    except:
        return (0, 0, 0)

def format_bytes(bytes_val: int) -> str:
    """Format bytes to human readable string"""
    if bytes_val is None:
        return "N/A"
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024:
            return f"{bytes_val:.1f}{unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f}PB"

def get_color_for_percent(percent: float) -> str:
    """Get color based on percentage"""
    if percent < 50:
        return Colors.GREEN
    elif percent < 75:
        return Colors.YELLOW
    elif percent < 90:
        return Colors.RED
    else:
        return Colors.BOLD + Colors.RED

def draw_bar(percent: float, width: int = 20) -> str:
    """Draw a progress bar"""
    filled = int(percent / 100 * width)
    bar = '█' * filled + '░' * (width - filled)
    color = get_color_for_percent(percent)
    return f"{color}{bar}{Colors.RESET}"

def print_header(title: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}┌{'─' * 50}┐{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}│ {title:^46} │{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}└{'─' * 50}┘{Colors.RESET}")

def print_metric(name: str, value: str, bar: str = None, extra: str = None):
    """Print a metric row"""
    if bar:
        print(f"  {name:20} {value:>15}  {bar}")
    else:
        print(f"  {name:20} {value:>15}")

def get_uptime() -> str:
    """Get system uptime"""
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.read().split()[0])
        
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    except:
        return "Unknown"

def get_hostname() -> str:
    """Get hostname"""
    try:
        return subprocess.check_output(['hostname'], text=True).strip()
    except:
        return "Unknown"

def main():
    parser = argparse.ArgumentParser(description='System Dashboard')
    parser.add_argument('-i', '--interval', type=int, default=0, help='Refresh interval in seconds (0 = once)')
    parser.add_argument('-n', '--num-proc', type=int, default=5, help='Number of top processes to show')
    parser.add_argument('--no-color', action='store_true', help='Disable colors')
    args = parser.parse_args()

    if args.no_color:
        for attr in dir(Colors):
            if not attr.startswith('_'):
                setattr(Colors, attr, '')

    def display_dashboard():
        # Clear screen
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Header
        hostname = get_hostname()
        uptime = get_uptime()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"{Colors.BOLD}{Colors.BLUE}╔{'═' * 56}╗{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}║ {f'System Dashboard - {hostname}':^52} ║{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}║ {'Uptime: ' + uptime:^52} ║{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}║ {now:^52} ║{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}╚{'═' * 56}╝{Colors.RESET}")
        
        # CPU Section
        cpu_usage, cpu_per_core, _ = get_cpu_usage()
        print_header("CPU")
        print_metric("Usage", f"{cpu_usage:.1f}%", draw_bar(cpu_usage))
        
        if PSUTIL_AVAILABLE and len(cpu_per_core) > 1:
            cores_bar = ' '.join([draw_bar(c, 4) for c in cpu_per_core])
            print(f"  {'Per Core':20} {cores_bar:>30}")
        
        load1, load5, load15 = get_load_average()
        cpu_count = os.cpu_count() or 1
        load_color = Colors.GREEN if load1 < cpu_count else Colors.YELLOW if load1 < cpu_count * 2 else Colors.RED
        print(f"  {'Load Average':20} {load1:.2f} / {load5:.2f} / {load15:.2f}")
        
        # Memory Section
        mem = get_memory_info()
        print_header("Memory")
        print_metric("Used", f"{format_bytes(mem['used'])} / {format_bytes(mem['total'])}", 
                    draw_bar(mem['percent']))
        print_metric("Available", f"{format_bytes(mem['available'])}")
        
        if mem['swap_total'] > 0:
            print_metric("Swap", f"{format_bytes(mem['swap_used'])} / {format_bytes(mem['swap_total'])}",
                        draw_bar(mem['swap_percent']))
        
        # Disk Section
        disks = get_disk_usage()
        if disks:
            print_header("Disk")
            for disk in disks:
                mount = disk['mount'][:20]
                print_metric(f"{mount}", 
                           f"{format_bytes(disk['used'])} / {format_bytes(disk['total'])}",
                           draw_bar(disk['percent']))
                print(f"     {'Free: ' + format_bytes(disk['free']):>40}")
        
        # Network Section
        net = get_network_stats()
        print_header("Network")
        print_metric("Received", format_bytes(net['bytes_recv']))
        print_metric("Sent", format_bytes(net['bytes_sent']))
        
        if net['errin'] > 0 or net['errout'] > 0:
            print_metric("Errors", f"In: {net['errin']}, Out: {net['errout']}")
        
        # Battery Section
        battery = get_battery_info()
        if battery['percent'] is not None:
            print_header("Battery")
            batt_icon = "" if battery['charging'] else ""
            batt_color = Colors.GREEN if battery['percent'] > 20 else Colors.RED
            print(f"  {'Status':20} {batt_icon} {'Charging' if battery['charging'] else 'Discharging'}")
            print(f"  {'Level':20} {batt_color}{battery['percent']}%{Colors.RESET} {draw_bar(battery['percent'])}")
        
        # Top Processes
        processes = get_top_processes(args.num_proc)
        if processes:
            print_header(f"Top {args.num_proc} Processes")
            print(f"  {'PID':>8} {'Name':<22} {'CPU%':>8} {'Mem%':>8} {'Status'}")
            print(f"  {'-'*8} {'-'*22} {'-'*8} {'-'*8} {'-'*6}")
            for p in processes:
                pid = str(p.get('pid', ''))[:8]
                name = str(p.get('name', ''))[:22]
                cpu = p.get('cpu_percent', 0)
                mem = p.get('memory_percent', 0)
                status = str(p.get('status', ''))[:6]
                
                cpu_color = get_color_for_percent(cpu) if cpu > 0 else Colors.DIM
                print(f"  {pid:>8} {name:<22} {cpu_color}{cpu:>7.1f}%{Colors.RESET} {mem:>7.1f}%  {status}")
        
        print(f"\n{Colors.DIM}Press Ctrl+C to exit{Colors.RESET}")

    if args.interval > 0:
        try:
            while True:
                display_dashboard()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n\n👋 Dashboard closed.")
    else:
        display_dashboard()
        print()

if __name__ == '__main__':
    main()
