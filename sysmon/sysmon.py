#!/usr/bin/env python3
"""
System Monitor - A CLI tool to monitor system resources
Shows CPU, RAM, and GPU usage with colored output
"""
import argparse
import os
import subprocess
import sys
import time
from datetime import datetime

# Try to import psutil, fallback to basic methods if not available
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'


def get_color(percentage: float) -> str:
    """Return color based on usage percentage"""
    if percentage < 50:
        return Colors.GREEN
    elif percentage < 75:
        return Colors.YELLOW
    else:
        return Colors.RED


def get_cpu_usage() -> float:
    """Get CPU usage percentage"""
    if HAS_PSUTIL:
        return psutil.cpu_percent(interval=0.5)
    else:
        # Fallback using /proc/stat on Linux
        try:
            with open('/proc/stat', 'r') as f:
                line = f.readline()
            values = line.split()[1:8]
            idle = int(values[3]) + int(values[4])
            total = sum(int(x) for x in values)
            return round((1 - idle / total) * 100, 1)
        except:
            return 0.0


def get_ram_usage() -> tuple:
    """Get RAM usage (used, total, percentage)"""
    if HAS_PSUTIL:
        mem = psutil.virtual_memory()
        return mem.used, mem.total, mem.percent
    else:
        # Fallback using free command
        try:
            result = subprocess.run(
                ['free', '-b'], capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                values = lines[1].split()[1:3]
                used = int(values[0])
                total = int(values[1])
                percent = round((used / total) * 100, 1)
                return used, total, percent
        except:
            pass
        return 0, 1, 0.0


def get_gpu_usage() -> tuple:
    """Get GPU usage (name, used_mb, total_mb, percentage, temp) using nvidia-smi"""
    try:
        result = subprocess.run(
            [
                'nvidia-smi',
                '--query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu',
                '--format=csv,noheader,nounits'
            ],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split(',')
            if len(parts) >= 5:
                name = parts[0].strip()
                used_mb = int(parts[1].strip())
                total_mb = int(parts[2].strip())
                percent = int(parts[3].strip())
                temp = int(parts[4].strip())
                return name, used_mb, total_mb, percent, temp
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None, 0, 0, 0, 0


def format_bytes(bytes_val: int) -> str:
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} PB"


def print_bar(value: float, length: int = 20) -> str:
    """Print a progress bar"""
    filled = int((value / 100) * length)
    bar = '█' * filled + '░' * (length - filled)
    return f"[{bar}]"


def print_header(title: str):
    """Print a section header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*50}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title:^50}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*50}{Colors.RESET}")


def print_system_info(compact: bool = False):
    """Print system information"""
    if compact:
        # Single line output
        cpu = get_cpu_usage()
        _, ram_total, ram_percent = get_ram_usage()
        
        gpu_name, gpu_used, gpu_total, gpu_percent, gpu_temp = get_gpu_usage()
        
        cpu_color = get_color(cpu)
        ram_color = get_color(ram_percent)
        gpu_color = get_color(gpu_percent) if gpu_name else Colors.BLUE
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        parts = [
            f"{timestamp}",
            f"CPU:{cpu_color}{cpu:>5.1f}%{Colors.RESET}",
            f"RAM:{ram_color}{ram_percent:>5.1f}%{Colors.RESET}"
        ]
        
        if gpu_name:
            parts.append(f"GPU:{gpu_color}{gpu_percent:>3d}%{Colors.RESET}")
            if gpu_temp > 0:
                temp_color = Colors.GREEN if gpu_temp < 70 else Colors.YELLOW if gpu_temp < 85 else Colors.RED
                parts.append(f"{temp_color}{gpu_temp}°C{Colors.RESET}")
        
        print(' | '.join(parts))
    else:
        # Detailed output
        print_header("SYSTEM MONITOR")
        print(f"{Colors.BOLD}Time:{Colors.RESET} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # CPU
        cpu = get_cpu_usage()
        cpu_color = get_color(cpu)
        print_header("CPU")
        print(f"  Usage: {cpu_color}{cpu:>6.1f}%{Colors.RESET} {print_bar(cpu)}")
        
        # RAM
        ram_used, ram_total, ram_percent = get_ram_usage()
        ram_color = get_color(ram_percent)
        print_header("MEMORY")
        print(f"  Used:  {Colors.CYAN}{format_bytes(ram_used):>10}{Colors.RESET}")
        print(f"  Total: {Colors.CYAN}{format_bytes(ram_total):>10}{Colors.RESET}")
        print(f"  Usage: {ram_color}{ram_percent:>6.1f}%{Colors.RESET} {print_bar(ram_percent)}")
        
        # GPU
        gpu_name, gpu_used, gpu_total, gpu_percent, gpu_temp = get_gpu_usage()
        if gpu_name:
            gpu_color = get_color(gpu_percent)
            print_header("GPU")
            print(f"  Name:  {Colors.MAGENTA}{gpu_name}{Colors.RESET}")
            print(f"  Used:  {Colors.CYAN}{format_bytes(gpu_used * 1024 * 1024):>10}{Colors.RESET}")
            print(f"  Total: {Colors.CYAN}{format_bytes(gpu_total * 1024 * 1024):>10}{Colors.RESET}")
            print(f"  Usage: {gpu_color}{gpu_percent:>6d}%{Colors.RESET} {print_bar(gpu_percent)}")
            if gpu_temp > 0:
                temp_color = Colors.GREEN if gpu_temp < 70 else Colors.YELLOW if gpu_temp < 85 else Colors.RED
                print(f"  Temp:  {temp_color}{gpu_temp}°C{Colors.RESET}")
        else:
            print_header("GPU")
            print(f"  {Colors.YELLOW}No NVIDIA GPU detected (nvidia-smi not available){Colors.RESET}")


def monitor_loop(interval: int = 2, compact: bool = False):
    """Continuous monitoring loop"""
    try:
        while True:
            # Clear screen for compact mode
            if compact:
                print_system_info(compact=True)
            else:
                os.system('clear' if os.name == 'posix' else 'cls')
                print_system_info(compact=False)
            
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\n{Colors.GREEN}✓ Monitoring stopped{Colors.RESET}")


def main():
    parser = argparse.ArgumentParser(
        description='System Monitor - Track CPU, RAM, and GPU usage',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sysmon                 # Show detailed system info once
  sysmon -c              # Compact single-line output
  sysmon -w              # Watch mode (continuous monitoring)
  sysmon -w -i 5         # Watch mode with 5 second interval
        """
    )
    parser.add_argument(
        '-c', '--compact',
        action='store_true',
        help='Compact single-line output'
    )
    parser.add_argument(
        '-w', '--watch',
        action='store_true',
        help='Continuous monitoring mode'
    )
    parser.add_argument(
        '-i', '--interval',
        type=int,
        default=2,
        help='Refresh interval in seconds (default: 2)'
    )
    parser.add_argument(
        '-v', '--version',
        action='store_true',
        help='Show version info'
    )
    
    args = parser.parse_args()
    
    if args.version:
        print("System Monitor v1.0.0")
        print(f"psutil available: {HAS_PSUTIL}")
        sys.exit(0)
    
    if args.watch:
        monitor_loop(interval=args.interval, compact=args.compact)
    else:
        print_system_info(compact=args.compact)


if __name__ == '__main__':
    main()
