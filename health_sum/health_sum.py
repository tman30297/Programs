#!/usr/bin/env python3
"""
Quick System Health Summary
A fast overview of system status at a glance.
"""

import subprocess
import os
import re

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    except:
        return "N/A"

def get_cpu():
    # Quick CPU usage
    usage = run_cmd("top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1")
    if usage == "N/A":
        return "N/A"
    return f"{usage}%"

def get_mem():
    # Memory usage
    mem = run_cmd("free -h | awk '/^Mem:/ {print $3\"/\"$2}'")
    return mem if mem else "N/A"

def get_disk():
    # Root disk usage
    disk = run_cmd("df -h / | awk 'NR==2 {print $3\"/\"$2 \" (\"$5\")\"}'")
    return disk if disk else "N/A"

def get_load():
    # Load average
    load = run_cmd("uptime | awk -F'load average:' '{print $2}'")
    return load.strip() if load else "N/A"

def get_gpu():
    # NVIDIA GPU
    gpu = run_cmd("nvidia-smi --query-gpu=utilization.gpu,temperature.gpu --format=csv,noheader,nounits")
    if gpu and gpu != "N/A":
        util, temp = gpu.split(",")
        return f"{util.strip()}%, {temp.strip()}°C"
    return "N/A"

def get_net():
    # Network I/O (approx from ifconfig)
    rx = run_cmd("cat /sys/class/net/*/statistics/rx_bytes 2>/dev/null | awk '{s+=$1} END {print s}'")
    tx = run_cmd("cat /sys/class/net/*/statistics/tx_bytes 2>/dev/null | awk '{s+=$1} END {print s}'")
    if rx != "N/A" and tx != "N/A":
        def fmt(b):
            for unit in ['B', 'KB', 'MB', 'GB']:
                if b < 1024:
                    return f"{b:.1f}{unit}"
                b /= 1024
            return f"{b:.1f}TB"
        return f"↓{fmt(float(rx))} ↑{fmt(float(tx))}"
    return "N/A"

def get_uptime():
    return run_cmd("uptime -p 2>/dev/null || uptime")

def main():
    print("=" * 45)
    print("       📊 SYSTEM HEALTH SUMMARY")
    print("=" * 45)
    print(f"  🖥️  CPU:       {get_cpu()}")
    print(f"  💾 Memory:    {get_mem()}")
    print(f"  💿 Disk:      {get_disk()}")
    print(f"  🎮 GPU:       {get_gpu()}")
    print(f"  📶 Network:   {get_net()}")
    print(f"  ⚡ Load:      {get_load()}")
    print(f"  ⏱️  Uptime:   {get_uptime()}")
    print("=" * 45)

    # OpenClaw status
    print("\n  🦴 OpenClaw Services:")
    gateway = run_cmd("openclaw gateway status 2>/dev/null | head -1")
    print(f"     Gateway: {gateway if gateway else 'N/A'}")
    
    print()

if __name__ == "__main__":
    main()
