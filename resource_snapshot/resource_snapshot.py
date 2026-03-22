#!/usr/bin/env python3
"""
Resource Snapshot Tool - Capture and compare system resource snapshots.
Usage:
    python resource_snapshot.py --take              # Take a snapshot
    python resource_snapshot.py --list             # List all snapshots
    python resource_snapshot.py --compare ID1 ID2  # Compare two snapshots
    python resource_snapshot.py --watch            # Continuous monitoring
    python resource_snapshot.py --latest           # Show latest snapshot
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# System imports
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import GPUtil
    HAS_GPUtil = True
except ImportError:
    HAS_GPUtil = False


SNAPSHOT_DIR = Path.home() / ".resource_snapshots"
SNAPSHOT_FILE = SNAPSHOT_DIR / "snapshots.json"


def ensure_dir():
    SNAPSHOT_DIR.mkdir(exist_ok=True)
    if not SNAPSHOT_FILE.exists():
        SNAPSHOT_FILE.write_text("[]")


def get_cpu_info():
    """Gather CPU information."""
    info = {
        "percent": psutil.cpu_percent(interval=0.1),
        "per_cpu": psutil.cpu_percent(interval=0.1, percpu=True),
        "count": psutil.cpu_count(),
        "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
    }
    
    # CPU times
    times = psutil.cpu_times()
    info["times"] = {
        "user": times.user,
        "system": times.system,
        "idle": times.idle,
    }
    
    return info


def get_memory_info():
    """Gather memory information."""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    return {
        "virtual": {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "percent": mem.percent,
        },
        "swap": {
            "total": swap.total,
            "used": swap.used,
            "free": swap.free,
            "percent": swap.percent,
        }
    }


def get_disk_info():
    """Gather disk information."""
    disks = {}
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks[part.mountpoint] = {
                "device": part.device,
                "fstype": part.fstype,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent,
            }
        except PermissionError:
            continue
    return disks


def get_network_info():
    """Gather network IO counters."""
    io = psutil.net_io_counters()
    return {
        "bytes_sent": io.bytes_sent,
        "bytes_recv": io.bytes_recv,
        "packets_sent": io.packets_sent,
        "packets_recv": io.packets_recv,
        "errin": io.errin,
        "errout": io.errout,
    }


def get_process_info():
    """Gather top processes by CPU and memory."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
        try:
            pinfo = proc.info
            if pinfo['cpu_percent'] is None:
                pinfo['cpu_percent'] = 0.0
            if pinfo['memory_percent'] is None:
                pinfo['memory_percent'] = 0.0
            processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # Sort by CPU, then by memory
    processes.sort(key=lambda x: (x.get('cpu_percent', 0), x.get('memory_percent', 0)), reverse=True)
    
    return {
        "total": len(processes),
        "top_cpu": processes[:10],
        "top_memory": sorted(processes, key=lambda x: x.get('memory_percent', 0), reverse=True)[:10],
    }


def get_gpu_info():
    """Gather GPU information if available."""
    if not HAS_GPUtil:
        # Try nvidia-smi fallback
        try:
            import subprocess
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu', 
                 '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                gpus = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) >= 6:
                            gpus.append({
                                "id": int(parts[0]),
                                "name": parts[1],
                                "utilization": float(parts[2]),
                                "memory_used": float(parts[3]),
                                "memory_total": float(parts[4]),
                                "temperature": float(parts[5]),
                            })
                return {"gpus": gpus, "source": "nvidia-smi"}
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return {"gpus": [], "source": "none"}
    
    try:
        gpus = GPUtil.getGPUs()
        return {
            "gpus": [{
                "id": gpu.id,
                "name": gpu.name,
                "utilization": gpu.load * 100,
                "memory_used": gpu.memoryUsed,
                "memory_total": gpu.memoryTotal,
                "temperature": gpu.temperature,
            } for gpu in gpus],
            "source": "GPUtil"
        }
    except Exception as e:
        return {"gpus": [], "source": f"error: {e}"}


def get_battery_info():
    """Gather battery information if available."""
    try:
        battery = psutil.sensors_battery()
        if battery:
            return {
                "percent": battery.percent,
                "time_left": battery.secsleft,
                "power_plugged": battery.power_plugged,
            }
    except Exception:
        pass
    return None


def take_snapshot():
    """Take a complete system snapshot."""
    if not HAS_PSUTIL:
        print("Error: psutil required. Install with: pip install psutil")
        return None
    
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "cpu": get_cpu_info(),
        "memory": get_memory_info(),
        "disk": get_disk_info(),
        "network": get_network_info(),
        "processes": get_process_info(),
        "gpu": get_gpu_info(),
        "battery": get_battery_info(),
    }
    
    # Load existing snapshots
    ensure_dir()
    snapshots = json.loads(SNAPSHOT_FILE.read_text())
    
    snapshot_id = len(snapshots) + 1
    snapshot["id"] = snapshot_id
    
    snapshots.append(snapshot)
    SNAPSHOT_FILE.write_text(json.dumps(snapshots, indent=2))
    
    print(f"✓ Snapshot #{snapshot_id} saved at {snapshot['timestamp']}")
    return snapshot_id


def format_bytes(bytes_val):
    """Format bytes to human readable."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024:
            return f"{bytes_val:.1f}{unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f}PB"


def format_percent(value, total):
    """Format as percentage."""
    if total == 0:
        return "0%"
    return f"{(value / total) * 100:.1f}%"


def print_snapshot(snapshot, verbose=False):
    """Print a snapshot in readable format."""
    print(f"\n{'='*60}")
    print(f"Snapshot #{snapshot['id']} - {snapshot['timestamp']}")
    print(f"{'='*60}")
    
    # CPU
    cpu = snapshot.get('cpu', {})
    print(f"\n📊 CPU: {cpu.get('percent', 0):.1f}% ({cpu.get('count', 0)} cores)")
    if verbose and cpu.get('per_cpu'):
        print(f"   Per-core: {', '.join(f'{c:.0f}%' for c in cpu['per_cpu'][:8])}")
    
    # Memory
    mem = snapshot.get('memory', {}).get('virtual', {})
    print(f"\n💾 Memory: {format_bytes(mem.get('used', 0))} / {format_bytes(mem.get('total', 0))} ({mem.get('percent', 0):.1f}%)")
    
    # GPU
    gpu = snapshot.get('gpu', {})
    if gpu.get('gpus'):
        for g in gpu['gpus']:
            print(f"\n🎮 GPU {g['id']}: {g['name']}")
            print(f"   Utilization: {g.get('utilization', 0):.1f}%")
            print(f"   Memory: {g.get('memory_used', 0):.0f}MB / {g.get('memory_total', 0):.0f}MB")
            print(f"   Temperature: {g.get('temperature', 0):.0f}°C")
    
    # Disk
    disk = snapshot.get('disk', {})
    if disk:
        print(f"\n💿 Disk Usage:")
        for mount, info in disk.items():
            print(f"   {mount}: {format_bytes(info.get('used', 0))} / {format_bytes(info.get('total', 0))} ({info.get('percent', 0):.1f}%)")
    
    # Network
    net = snapshot.get('network', {})
    print(f"\n🌐 Network: ↑{format_bytes(net.get('bytes_sent', 0))} ↓{format_bytes(net.get('bytes_recv', 0))}")
    
    # Processes
    procs = snapshot.get('processes', {})
    if verbose and procs.get('top_cpu'):
        print(f"\n🔝 Top Processes (CPU):")
        for p in procs['top_cpu'][:5]:
            print(f"   {p['name'][:30]:30s} {p.get('cpu_percent', 0):5.1f}% CPU")
    
    # Battery
    batt = snapshot.get('battery')
    if batt:
        status = "⚡ Charging" if batt.get('power_plugged') else "🔋 On Battery"
        print(f"\n{status}: {batt.get('percent', 0):.0f}%")


def list_snapshots():
    """List all snapshots."""
    ensure_dir()
    snapshots = json.loads(SNAPSHOT_FILE.read_text())
    
    if not snapshots:
        print("No snapshots yet. Run with --take first.")
        return
    
    print(f"\n{'ID':<5} {'Timestamp':<25} {'CPU%':<8} {'Memory%':<10} {'GPU%':<8}")
    print("-" * 60)
    
    for s in snapshots:
        cpu = s.get('cpu', {}).get('percent', 0)
        mem = s.get('memory', {}).get('virtual', {}).get('percent', 0)
        
        gpu_util = 0
        gpus = s.get('gpu', {}).get('gpus', [])
        if gpus:
            gpu_util = gpus[0].get('utilization', 0)
        
        print(f"{s['id']:<5} {s['timestamp'][:25]:<25} {cpu:>5.1f}%  {mem:>7.1f}%   {gpu_util:>5.1f}%")


def compare_snapshots(id1, id2):
    """Compare two snapshots."""
    ensure_dir()
    snapshots = json.loads(SNAPSHOT_FILE.read_text())
    
    snap1 = next((s for s in snapshots if s['id'] == id1), None)
    snap2 = next((s for s in snapshots if s['id'] == id2), None)
    
    if not snap1 or not snap2:
        print(f"Error: One or both snapshots not found ({id1}, {id2})")
        return
    
    print(f"\n{'='*60}")
    print(f"Comparing Snapshot #{id1} vs #{id2}")
    print(f"{'='*60}")
    
    # Time difference
    t1 = datetime.fromisoformat(snap1['timestamp'])
    t2 = datetime.fromisoformat(snap2['timestamp'])
    diff = t2 - t1
    print(f"Time difference: {diff}")
    
    # CPU comparison
    cpu1 = snap1.get('cpu', {}).get('percent', 0)
    cpu2 = snap2.get('cpu', {}).get('percent', 0)
    cpu_diff = cpu2 - cpu1
    sign = "+" if cpu_diff > 0 else ""
    print(f"\n📊 CPU:    {cpu1:.1f}% → {cpu2:.1f}% ({sign}{cpu_diff:.1f}%)")
    
    # Memory comparison
    mem1 = snap1.get('memory', {}).get('virtual', {}).get('percent', 0)
    mem2 = snap2.get('memory', {}).get('virtual', {}).get('percent', 0)
    mem_diff = mem2 - mem1
    sign = "+" if mem_diff > 0 else ""
    print(f"💾 Memory: {mem1:.1f}% → {mem2:.1f}% ({sign}{mem_diff:.1f}%)")
    
    # GPU comparison
    gpus1 = snap1.get('gpu', {}).get('gpus', [])
    gpus2 = snap2.get('gpu', {}).get('gpus', [])
    if gpus1 and gpus2:
        gpu1 = gpus1[0].get('utilization', 0)
        gpu2 = gpus2[0].get('utilization', 0)
        gpu_diff = gpu2 - gpu1
        sign = "+" if gpu_diff > 0 else ""
        print(f"🎮 GPU:    {gpu1:.1f}% → {gpu2:.1f}% ({sign}{gpu_diff:.1f}%)")
        
        mem1_mb = gpus1[0].get('memory_used', 0)
        mem2_mb = gpus2[0].get('memory_used', 0)
        mem_diff_mb = mem2_mb - mem1_mb
        sign = "+" if mem_diff_mb > 0 else ""
        print(f"   VRAM:  {mem1_mb:.0f}MB → {mem2_mb:.0f}MB ({sign}{mem_diff_mb:.0f}MB)")
    
    # Network delta
    net1 = snap1.get('network', {})
    net2 = snap2.get('network', {})
    sent_diff = net2.get('bytes_sent', 0) - net1.get('bytes_sent', 0)
    recv_diff = net2.get('bytes_recv', 0) - net1.get('bytes_recv', 0)
    print(f"\n🌐 Network: ↑{format_bytes(sent_diff)} ↓{format_bytes(recv_diff)}")
    
    # Process changes
    procs1 = {p['name']: p for p in snap1.get('processes', {}).get('top_cpu', [])}
    procs2 = snap2.get('processes', {}).get('top_cpu', [])
    
    new_procs = []
    for p in procs2:
        if p['name'] not in procs1:
            new_procs.append(p)
    
    if new_procs:
        print(f"\n🚀 New processes (by CPU):")
        for p in new_procs[:5]:
            print(f"   + {p['name']} ({p.get('cpu_percent', 0):.1f}%)")


def watch_system(interval=2, count=None):
    """Continuously monitor system resources."""
    print(f"Watching system (Ctrl+C to stop)...\n")
    
    iterations = 0
    while count is None or iterations < count:
        # Take quick snapshot
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "cpu": get_cpu_info(),
            "memory": get_memory_info(),
            "gpu": get_gpu_info(),
        }
        
        # Clear line and print
        cpu = snapshot['cpu'].get('percent', 0)
        mem = snapshot['memory']['virtual'].get('percent', 0)
        
        gpu_str = ""
        gpus = snapshot['gpu'].get('gpus', [])
        if gpus:
            gpu_util = gpus[0].get('utilization', 0)
            gpu_mem = gpus[0].get('memory_used', 0)
            gpu_str = f" | GPU: {gpu_util:5.1f}% | VRAM: {gpu_mem:5.0f}MB"
        
        timestamp = snapshot['timestamp'].split('T')[1].split('.')[0]
        print(f"\r[{timestamp}] CPU: {cpu:5.1f}% | MEM: {mem:5.1f}%{gpu_str}", end="")
        
        time.sleep(interval)
        iterations += 1
    
    print("\n")


def main():
    parser = argparse.ArgumentParser(description="Resource Snapshot Tool")
    parser.add_argument("--take", action="store_true", help="Take a snapshot")
    parser.add_argument("--list", "-l", action="store_true", help="List all snapshots")
    parser.add_argument("--latest", action="store_true", help="Show latest snapshot")
    parser.add_argument("--compare", nargs=2, type=int, metavar=("ID1", "ID2"), help="Compare two snapshots")
    parser.add_argument("--watch", "-w", action="store_true", help="Watch system continuously")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--interval", "-i", type=float, default=2, help="Watch interval in seconds")
    parser.add_argument("--count", "-c", type=int, help="Number of iterations for watch mode")
    
    args = parser.parse_args()
    
    if args.take:
        take_snapshot()
    elif args.list:
        list_snapshots()
    elif args.latest:
        ensure_dir()
        snapshots = json.loads(SNAPSHOT_FILE.read_text())
        if snapshots:
            print_snapshot(snapshots[-1], verbose=args.verbose)
        else:
            print("No snapshots yet.")
    elif args.compare:
        compare_snapshots(args.compare[0], args.compare[1])
    elif args.watch:
        if not HAS_PSUTIL:
            print("Error: psutil required for watch mode")
            sys.exit(1)
        watch_system(args.interval, args.count)
    else:
        # Default: show latest
        ensure_dir()
        snapshots = json.loads(SNAPSHOT_FILE.read_text())
        if snapshots:
            print_snapshot(snapshots[-1], verbose=args.verbose)
        else:
            print("No snapshots. Run with --take to capture current state.")


if __name__ == "__main__":
    main()
