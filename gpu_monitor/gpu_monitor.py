#!/usr/bin/env python3
"""
GPU Monitor - Real-time NVIDIA GPU monitoring tool
Shows usage, memory, temperature, power draw, and utilization stats
"""

import subprocess
import time
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Try to import nvidia-ml-py3, fall back to nvidia-smi if not available
try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False


def parse_float(value, default=None):
    """Parse float from string, handling N/A values"""
    try:
        val = value.strip()
        if val == '[N/A]' or val == 'N/A' or not val:
            return default
        return float(val)
    except (ValueError, AttributeError):
        return default


class GPUMonitor:
    def __init__(self, use_smi_fallback=True):
        self.use_smi_fallback = use_smi_fallback
        self.handle = None
        self.using_pynvml = False
        
        if PYNVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self.handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                self.using_pynvml = True
            except Exception as e:
                print(f"Warning: pynvml init failed: {e}")
                self.using_pynvml = False
    
    def get_stats_pynvml(self):
        """Get stats using pynvml library"""
        try:
            util = pynvml.nvmlDeviceGetUtilizationRates(self.handle)
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
            temp = pynvml.nvmlDeviceGetTemperature(self.handle, pynvml.NVML_TEMPERATURE_GPU)
            power = pynvml.nvmlDeviceGetPowerUsage(self.handle) / 1000.0  # milliwatts to watts
            power_limit = pynvml.nvmlDeviceGetPowerManagementLimit(self.handle) / 1000.0
            
            return {
                'gpu_util': util.gpu,
                'mem_util': util.memory,
                'mem_used': mem_info.used / (1024**3),  # GB
                'mem_total': mem_info.total / (1024**3),  # GB
                'mem_free': mem_info.free / (1024**3),  # GB
                'temperature': temp,
                'power_draw': power,
                'power_limit': power_limit,
                'fan_speed': self._get_fan_speed(),
            }
        except Exception as e:
            return None
    
    def _get_fan_speed(self):
        """Get fan speed percentage"""
        try:
            return pynvml.nvmlDeviceGetFanSpeed(self.handle)
        except:
            return None
    
    def get_stats_smi(self):
        """Get stats using nvidia-smi CLI"""
        try:
            result = subprocess.run([
                'nvidia-smi', '--query-gpu=index,name,utilization.gpu,utilization.memory,'
                'memory.used,memory.total,memory.free,temperature.gpu,'
                'power.draw,power.limit,fan.speed',
                '--format=csv,noheader,nounits'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                return None
            
            parts = result.stdout.strip().split(',')
            if len(parts) >= 11:
                return {
                    'gpu_util': parse_float(parts[2]),
                    'mem_util': parse_float(parts[3]),
                    'mem_used': (parse_float(parts[4]) or 0) / 1024,  # MB to GB
                    'mem_total': (parse_float(parts[5]) or 0) / 1024,
                    'mem_free': (parse_float(parts[6]) or 0) / 1024,
                    'temperature': parse_float(parts[7]),
                    'power_draw': parse_float(parts[8]),
                    'power_limit': parse_float(parts[9]),
                    'fan_speed': parse_float(parts[10]),
                }
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError) as e:
            return None
        return None
    
    def get_stats(self):
        """Get GPU stats using best available method"""
        if self.using_pynvml:
            stats = self.get_stats_pynvml()
            if stats:
                return stats
        
        if self.use_smi_fallback:
            return self.get_stats_smi()
        
        return None
    
    def get_gpu_name(self):
        """Get GPU name"""
        if self.using_pynvml:
            try:
                name = pynvml.nvmlDeviceGetName(self.handle)
                if isinstance(name, bytes):
                    name = name.decode('utf-8')
                return name
            except:
                pass
        
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                                    capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return "Unknown GPU"
    
    def close(self):
        """Cleanup"""
        if PYNVML_AVAILABLE:
            try:
                pynvml.nvmlShutdown()
            except:
                pass


def format_bar(value, length=10):
    """Create a text progress bar"""
    filled = int(length * value / 100)
    return "█" * filled + "░" * (length - filled)


def format_temp(temp):
    """Format temperature with color indicator"""
    if temp is None:
        return "N/A"
    if temp >= 85:
        return f"🔥 {temp}°C"
    elif temp >= 70:
        return f"⚠️ {temp}°C"
    return f"{temp}°C"


def format_power(power, limit):
    """Format power draw"""
    if power is None or limit is None:
        return "N/A"
    percent = (power / limit) * 100 if limit > 0 else 0
    return f"{power:.0f}W / {limit:.0f}W ({percent:.0f}%)"


def display_once(monitor):
    """Display single snapshot"""
    stats = monitor.get_stats()
    gpu_name = monitor.get_gpu_name()
    
    print(f"\n{'═' * 50}")
    print(f"  🎮 {gpu_name}")
    print(f"{'═' * 50}")
    
    if stats is None:
        print("  ❌ No GPU detected or nvidia-smi not available")
        print(f"{'═' * 50}")
        return False
    
    # GPU Utilization
    gpu_bar = format_bar(stats['gpu_util'])
    print(f"  GPU Usage:    [{gpu_bar}] {stats['gpu_util']:5.1f}%")
    
    # Memory
    mem_bar = format_bar((stats['mem_used'] / stats['mem_total']) * 100)
    print(f"  Memory:       [{mem_bar}] {stats['mem_used']:.1f}GB / {stats['mem_total']:.1f}GB")
    
    # Temperature
    print(f"  Temperature:  {format_temp(stats['temperature'])}")
    
    # Power
    print(f"  Power:        {format_power(stats['power_draw'], stats['power_limit'])}")
    
    # Fan
    if stats['fan_speed'] is not None:
        fan_bar = format_bar(stats['fan_speed'])
        print(f"  Fan:          [{fan_bar}] {stats['fan_speed']:.0f}%")
    
    print(f"{'═' * 50}")
    return True


def display_continuous(monitor, interval=1):
    """Display continuous monitoring"""
    print("\n📊 GPU Monitor - Press Ctrl+C to exit\n")
    
    try:
        while True:
            # Get cursor position and clear screen (simple approach)
            stats = monitor.get_stats()
            gpu_name = monitor.get_gpu_name()
            
            # Clear previous lines (approximate)
            print("\033[8F", end="")  # Move cursor up 8 lines
            print("\033[J", end="")   # Clear to end of screen
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"  {timestamp} | {gpu_name}")
            print(f"  {'─' * 46}")
            
            if stats is None:
                print("  ❌ GPU not available")
            else:
                # GPU
                gpu_bar = format_bar(stats['gpu_util'], 15)
                print(f"  GPU     [{gpu_bar}] {stats['gpu_util']:5.1f}%")
                
                # Memory
                mem_pct = (stats['mem_used'] / stats['mem_total']) * 100
                mem_bar = format_bar(mem_pct, 15)
                print(f"  Memory  [{mem_bar}] {stats['mem_used']:5.1f} / {stats['mem_total']:.1f} GB ({mem_pct:.0f}%)")
                
                # Temp
                temp_icon = "🔥" if stats['temperature'] >= 85 else "⚠️" if stats['temperature'] >= 70 else "🌡️"
                print(f"  Temp    {temp_icon} {stats['temperature']}°C")
                
                # Power
                if stats['power_draw'] and stats['power_limit']:
                    print(f"  Power   ⚡ {stats['power_draw']:.0f}W / {stats['power_limit']:.0f}W")
                
                # Fan
                if stats['fan_speed'] is not None:
                    print(f"  Fan     🌀 {stats['fan_speed']:.0f}%")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\n👋 Exiting GPU monitor")


def export_csv(monitor, output_file, duration=60, interval=5):
    """Export stats to CSV for a duration"""
    import csv
    
    output_path = Path(output_file).expanduser()
    
    print(f"📈 Recording GPU stats to {output_path} for {duration} seconds...")
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'gpu_util', 'mem_util', 'mem_used_gb', 'mem_total_gb', 
                        'temperature', 'power_watts', 'fan_speed'])
        
        start_time = time.time()
        while time.time() - start_time < duration:
            stats = monitor.get_stats()
            if stats:
                writer.writerow([
                    datetime.now().isoformat(),
                    stats.get('gpu_util', 0),
                    stats.get('mem_util', 0),
                    round(stats.get('mem_used', 0), 2),
                    round(stats.get('mem_total', 0), 2),
                    stats.get('temperature', 0),
                    round(stats.get('power_draw', 0), 1),
                    stats.get('fan_speed', 0) or 0
                ])
                f.flush()
            
            print(f"  Recorded... {int(duration - (time.time() - start_time))}s remaining", end='\r')
            time.sleep(interval)
    
    print(f"\n✅ Done! Saved to {output_path}")


def check_gpu_available():
    """Check if NVIDIA GPU is available"""
    try:
        result = subprocess.run(['nvidia-smi', '-L'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return True
    except:
        pass
    return False


def main():
    parser = argparse.ArgumentParser(description="GPU Monitor - Real-time NVIDIA GPU stats")
    parser.add_argument("-c", "--continuous", action="store_true", help="Continuous monitoring mode")
    parser.add_argument("-i", "--interval", type=float, default=1.0, help="Update interval in seconds (default: 1)")
    parser.add_argument("-e", "--export", type=str, metavar="FILE", help="Export stats to CSV file")
    parser.add_argument("-d", "--duration", type=int, default=60, help="Duration for CSV export (seconds)")
    parser.add_argument("-t", "--interval-export", type=int, default=5, help="Export interval in seconds")
    parser.add_argument("--check", action="store_true", help="Check if GPU is available and exit")
    args = parser.parse_args()
    
    # Check GPU availability first
    if args.check:
        if check_gpu_available():
            print("✅ NVIDIA GPU detected")
            try:
                result = subprocess.run(['nvidia-smi', '-L'], capture_output=True, text=True)
                print(result.stdout.strip())
            except:
                pass
            sys.exit(0)
        else:
            print("❌ No NVIDIA GPU detected or nvidia-smi not available")
            sys.exit(1)
    
    # Check for GPU
    if not check_gpu_available():
        print("❌ Error: No NVIDIA GPU detected or nvidia-smi not available")
        print("   Make sure NVIDIA drivers are installed")
        sys.exit(1)
    
    monitor = GPUMonitor()
    
    try:
        if args.export:
            export_csv(monitor, args.export, args.duration, args.interval_export)
        elif args.continuous:
            display_continuous(monitor, args.interval)
        else:
            display_once(monitor)
    finally:
        monitor.close()


if __name__ == "__main__":
    main()
