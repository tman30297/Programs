#!/usr/bin/env python3
"""
Daily Briefing - A CLI dashboard showing weather, system info, and utilities
Usage: python daily_briefing.py [--weather] [--system] [--all]
"""

import argparse
import datetime
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Try to import optional dependencies
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class Colors:
    """ANSI color codes"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    GRAY = '\033[90m'


def get_weather(location: str = "auto") -> dict:
    """Get weather from wttr.in (no API key needed)"""
    try:
        import urllib.request
        url = f"https://wttr.in/{location}?format=j1"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            current = data['current_condition'][0]
            return {
                'location': data['nearest_area'][0]['areaName'][0]['value'],
                'temp': current['temp_C'][0],
                'condition': current['weatherDesc'][0]['value'],
                'humidity': current['humidity'][0],
                'wind': current['windspeedKmph'][0],
            }
    except Exception as e:
        return {'error': str(e)}


def get_system_info() -> dict:
    """Gather system information"""
    info = {}
    
    # Uptime
    try:
        with open('/proc/uptime') as f:
            uptime_seconds = float(f.read().split()[0])
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            mins = int((uptime_seconds % 3600) // 60)
            info['uptime'] = f"{days}d {hours}h {mins}m"
    except:
        info['uptime'] = "Unknown"
    
    # Memory
    try:
        with open('/proc/meminfo') as f:
            mem = {}
            for line in f:
                parts = line.split()
                if len(parts) >= 2:
                    mem[parts[0].rstrip(':')] = int(parts[1])
            total = mem.get('MemTotal', 0) / 1024 / 1024
            avail = mem.get('MemAvailable', 0) / 1024 / 1024
            used = total - avail
            info['memory'] = {
                'total': f"{total:.1f} GB",
                'used': f"{used:.1f} GB",
                'percent': int(used / total * 100) if total > 0 else 0
            }
    except:
        info['memory'] = {'error': 'Could not read'}
    
    # CPU load
    try:
        load1, load5, load15 = os.getloadavg()
        info['load'] = f"{load1:.2f} (1m), {load5:.2f} (5m), {load15:.2f} (15m)"
    except:
        info['load'] = "Unknown"
    
    # Disk usage
    try:
        import shutil
        usage = shutil.disk_usage('/')
        total = usage.total / (1024**3)
        used = usage.used / (1024**3)
        info['disk'] = {
            'total': f"{total:.1f} GB",
            'used': f"{used:.1f} GB",
            'percent': int(used / total * 100)
        }
    except:
        info['disk'] = {'error': 'Could not read'}
    
    # Battery (if available)
    try:
        battery_path = Path('/sys/class/power_supply/BAT0/capacity')
        if battery_path.exists():
            info['battery'] = battery_path.read_text().strip() + '%'
    except:
        pass
    
    return info


def get_network_info() -> dict:
    """Get network connections and status"""
    info = {}
    
    # Check internet connectivity
    try:
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        info['internet'] = True
    except:
        info['internet'] = False
    
    # Local IP
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        info['local_ip'] = s.getsockname()[0]
        s.close()
    except:
        info['local_ip'] = "Unknown"
    
    return info


def get_datetime_info() -> dict:
    """Get current date/time info"""
    now = datetime.datetime.now()
    return {
        'datetime': now.strftime("%Y-%m-%d %H:%M:%S"),
        'date': now.strftime("%A, %B %d, %Y"),
        'time': now.strftime("%H:%M:%S"),
        'timezone': datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo,
    }


def print_header(text: str):
    """Print a section header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^50}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 50}{Colors.RESET}")


def print_weather(weather: dict):
    """Print weather information"""
    if 'error' in weather:
        print(f"  {Colors.YELLOW}Weather unavailable: {weather['error']}{Colors.RESET}")
        return
    
    print(f"  {Colors.BOLD}Location:{Colors.RESET} {weather.get('location', 'Unknown')}")
    print(f"  {Colors.BOLD}Temperature:{Colors.RESET} {weather.get('temp', '?')}°C")
    print(f"  {Colors.BOLD}Condition:{Colors.RESET} {weather.get('condition', 'Unknown')}")
    print(f"  {Colors.BOLD}Humidity:{Colors.RESET} {weather.get('humidity', '?')}%")
    print(f"  {Colors.BOLD}Wind:{Colors.RESET} {weather.get('wind', '?')} km/h")


def print_system(sys_info: dict):
    """Print system information"""
    print(f"  {Colors.BOLD}Uptime:{Colors.RESET} {sys_info.get('uptime', 'Unknown')}")
    print(f"  {Colors.BOLD}Load:{Colors.RESET} {sys_info.get('load', 'Unknown')}")
    
    if 'memory' in sys_info and isinstance(sys_info['memory'], dict):
        mem = sys_info['memory']
        if 'error' not in mem:
            color = Colors.GREEN if mem['percent'] < 70 else Colors.YELLOW if mem['percent'] < 90 else Colors.RED
            print(f"  {Colors.BOLD}Memory:{Colors.RESET} {mem['used']} / {mem['total']} ({color}{mem['percent']}%{Colors.RESET})")
    
    if 'disk' in sys_info and isinstance(sys_info['disk'], dict):
        disk = sys_info['disk']
        if 'error' not in disk:
            color = Colors.GREEN if disk['percent'] < 70 else Colors.YELLOW if disk['percent'] < 90 else Colors.RED
            print(f"  {Colors.BOLD}Disk:{Colors.RESET} {disk['used']} / {disk['total']} ({color}{disk['percent']}%{Colors.RESET})")
    
    if 'battery' in sys_info:
        print(f"  {Colors.BOLD}Battery:{Colors.RESET} {sys_info['battery']}")


def print_network(net_info: dict):
    """Print network information"""
    status = f"{Colors.GREEN}Connected{Colors.RESET}" if net_info.get('internet') else f"{Colors.RED}Disconnected{Colors.RESET}"
    print(f"  {Colors.BOLD}Internet:{Colors.RESET} {status}")
    print(f"  {Colors.BOLD}Local IP:{Colors.RESET} {net_info.get('local_ip', 'Unknown')}")


def print_datetime(dt_info: dict):
    """Print date/time information"""
    print(f"  {Colors.BOLD}Date:{Colors.RESET} {dt_info.get('date', 'Unknown')}")
    print(f"  {Colors.BOLD}Time:{Colors.RESET} {dt_info.get('time', 'Unknown')}")


def quick_tools():
    """Show quick utility tools"""
    print_header("Quick Tools")
    
    tools = [
        ("1", "Weather (default location)", "--weather"),
        ("2", "System Info", "--system"),
        ("3", "Network Status", "--network"),
        ("4", "Full Briefing", "--all"),
        ("q", "Quit", "quit"),
    ]
    
    print(f"  {Colors.GRAY}Available options:{Colors.RESET}")
    for key, desc, _ in tools:
        print(f"    {Colors.BOLD}{key}{Colors.RESET}: {desc}")
    print()


def main():
    parser = argparse.ArgumentParser(description='Daily Briefing CLI Dashboard')
    parser.add_argument('--weather', '-w', action='store_true', help='Show weather')
    parser.add_argument('--system', '-s', action='store_true', help='Show system info')
    parser.add_argument('--network', '-n', action='store_true', help='Show network info')
    parser.add_argument('--all', '-a', action='store_true', help='Show all info')
    parser.add_argument('--location', '-l', default='', help='Weather location (default: auto)')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    
    args = parser.parse_args()
    
    # If no args, show all
    show_all = not (args.weather or args.system or args.network)
    
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}📋 Daily Briefing{Colors.RESET}")
    print(f"{Colors.GRAY}Generated at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    
    if args.all or show_all:
        # Date/Time
        print_header("Date & Time")
        dt_info = get_datetime_info()
        print_datetime(dt_info)
        
        # Weather
        print_header("Weather")
        weather = get_weather(args.location)
        print_weather(weather)
        
        # System
        print_header("System Info")
        sys_info = get_system_info()
        print_system(sys_info)
        
        # Network
        print_header("Network")
        net_info = get_network_info()
        print_network(net_info)
        
    else:
        if args.weather:
            print_header("Weather")
            weather = get_weather(args.location)
            print_weather(weather)
        
        if args.system:
            print_header("System Info")
            sys_info = get_system_info()
            print_system(sys_info)
        
        if args.network:
            print_header("Network")
            net_info = get_network_info()
            print_network(net_info)
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}✓ Briefing complete!{Colors.RESET}\n")


if __name__ == '__main__':
    main()
