#!/usr/bin/env python3
"""
System Monitor - Real-time CPU, Memory, Disk, and GPU monitoring
Usage: python3 system_monitor.py [--interval SECONDS] [--gpu]
"""

import argparse
import os
import time
import subprocess
import sys
from datetime import datetime

# Try to import psutil, install if missing
try:
    import psutil
except ImportError:
    print("Installing psutil...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
    import psutil


def get_gpu_stats():
    """Get NVIDIA GPU stats using nvidia-smi"""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu,temperature.gpu,memory.used,memory.total",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            line = result.stdout.strip()
            if line:
                util, temp, mem_used, mem_total = line.split(",")
                return {
                    "available": True,
                    "utilization": int(util.strip()),
                    "temperature": int(temp.strip()),
                    "memory_used": int(mem_used.strip()),
                    "memory_total": int(mem_total.strip())
                }
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        pass
    return {"available": False}


def get_battery_info():
    """Get battery status if available"""
    try:
        battery = psutil.sensors_battery()
        if battery:
            return {
                "percent": battery.percent,
                "charging": battery.power_plugged
            }
    except Exception:
        pass
    return None


def format_bytes(bytes_val):
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024:
            return f"{bytes_val:.1f}{unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f}PB"


def get_disk_usage(path="/"):
    """Get disk usage for a path"""
    try:
        usage = psutil.disk_usage(path)
        return {
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": usage.percent
        }
    except Exception:
        return None


def get_top_processes(limit=5):
    """Get top processes by CPU usage"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            pinfo = proc.info
            if pinfo['cpu_percent'] is not None:
                processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
    return processes[:limit]


def clear_screen():
    """Clear terminal screen"""
    if sys.stdout.isatty():
        os.system('cls' if os.name == 'nt' else 'clear')


def main():
    parser = argparse.ArgumentParser(description="System Monitor Dashboard")
    parser.add_argument("--interval", type=int, default=2, help="Update interval in seconds")
    parser.add_argument("--gpu", action="store_true", help="Show GPU stats")
    parser.add_argument("--no-color", action="store_true", help="Disable colors")
    args = parser.parse_args()

    # ANSI colors
    if args.no_color or not sys.stdout.isatty():
        RESET = GREEN = YELLOW = RED = BLUE = CYAN = ""
    else:
        RESET = "\033[0m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        RED = "\033[91m"
        BLUE = "\033[94m"
        CYAN = "\033[96m"

    print(f"{CYAN}System Monitor Dashboard{RESET}")
    print("Press Ctrl+C to exit\n")

    # Initialize CPU monitoring (first call returns 0, subsequent calls are accurate)
    psutil.cpu_percent(interval=None, percpu=False)

    try:
        while True:
            # Get system stats
            cpu_percent = psutil.cpu_percent(interval=None, percpu=False)
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            disk = get_disk_usage("/")
            battery = get_battery_info()
            
            # Get GPU stats if requested
            gpu_stats = get_gpu_stats() if args.gpu else {"available": False}

            # Build output
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # CPU line
            if cpu_percent > 80:
                cpu_color = RED
            elif cpu_percent > 50:
                cpu_color = YELLOW
            else:
                cpu_color = GREEN
            
            lines = [
                f"📅 {timestamp}",
                f"{'─' * 50}",
                f"🖥️  CPU: {cpu_color}{cpu_percent}%{RESET} ({cpu_count} cores)",
            ]

            # Memory line
            mem_percent = memory.percent
            if mem_percent > 80:
                mem_color = RED
            elif mem_percent > 50:
                mem_color = YELLOW
            else:
                mem_color = GREEN
            
            lines.append(f"💾 RAM:  {mem_color}{mem_percent}%{RESET} ({format_bytes(memory.used)} / {format_bytes(memory.total)})")

            # Disk line
            if disk:
                disk_percent = disk['percent']
                if disk_percent > 90:
                    disk_color = RED
                elif disk_percent > 70:
                    disk_color = YELLOW
                else:
                    disk_color = GREEN
                
                lines.append(f"💿 Disk: {disk_color}{disk_percent}%{RESET} ({format_bytes(disk['used'])} / {format_bytes(disk['total'])})")

            # GPU line
            if gpu_stats.get("available"):
                gpu_util = gpu_stats["utilization"]
                gpu_temp = gpu_stats["temperature"]
                gpu_mem = gpu_stats["memory_used"]
                gpu_mem_total = gpu_stats["memory_total"]
                
                if gpu_util > 80:
                    gpu_color = RED
                elif gpu_util > 50:
                    gpu_color = YELLOW
                else:
                    gpu_color = GREEN
                
                lines.append(f"🎮 GPU:  {gpu_color}{gpu_util}%{RESET} | {gpu_temp}°C | {format_bytes(gpu_mem * 1024**2)} / {format_bytes(gpu_mem_total * 1024**2)}")

            # Battery line
            if battery:
                bat_symbol = "⚡" if battery["charging"] else "🔋"
                lines.append(f"{bat_symbol} Battery: {battery['percent']}%{' (charging)' if battery['charging'] else ''}")

            lines.append(f"{'─' * 50}")
            lines.append(f"{BLUE}Top Processes (by CPU):{RESET}")
            
            for i, proc in enumerate(get_top_processes(5), 1):
                cpu_val = proc['cpu_percent'] or 0
                mem_val = proc['memory_percent'] or 0
                lines.append(f"  {i}. {proc['name'][:30]:30} CPU: {cpu_val:5.1f}%  MEM: {mem_val:5.1f}%")

            # Print
            clear_screen()
            print("\n".join(lines))
            
            time.sleep(args.interval)

    except KeyboardInterrupt:
        print(f"\n{GREEN}Monitoring stopped.{RESET}")
        sys.exit(0)


if __name__ == "__main__":
    main()
