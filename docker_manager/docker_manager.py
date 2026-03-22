#!/usr/bin/env python3
"""
Docker Container Manager - Manage Docker containers, images, volumes, and networks
Usage: docker_manager.py <command> [options]
Commands:
  ps [opts]           List containers (use -a for all, -s for size)
  images              List images
  logs <name>         View container logs (use -f to follow)
  stats               Show container stats (live)
  start <name>        Start container
  stop <name>         Stop container
  restart <name>     Restart container
  remove <name>       Remove container (use -f to force)
  inspect <name>      Inspect container details
  exec <name> <cmd>   Execute command in container
  pull <image>        Pull an image
  clean               Clean up unused containers/images/volumes
  networks            List Docker networks
  volumes             List volumes
  top <name>          Show running processes in container
"""

import os
import sys
import subprocess
import argparse
import json

def run_cmd(cmd, capture=True):
    """Run docker command"""
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    return result.returncode, result.stdout, result.stderr

def list_containers(all_flag=False, size=False):
    """List containers"""
    cmd = "docker ps --format '{{.ID}}|{{.Image}}|{{.Status}}|{{.Names}}|{{.Ports}}'"
    if all_flag:
        cmd = "docker ps -a --format '{{.ID}}|{{.Image}}|{{.Status}}|{{.Names}}|{{.Ports}}'"
    if size:
        cmd += " --size"
    
    code, out, err = run_cmd(cmd)
    
    if code != 0:
        print(f"❌ Error: {err}")
        return
    
    print("🐳 Docker Containers:\n")
    print(f"{'ID':<12} {'Image':<20} {'Status':<15} {'Names':<20} {'Ports'}")
    print("-" * 90)
    
    for line in out.strip().split('\n'):
        if '|' in line:
            parts = line.split('|')
            if len(parts) >= 4:
                print(f"{parts[0][:12]:<12} {parts[1][:20]:<20} {parts[2][:15]:<15} {parts[3][:20]:<20} {parts[4] if len(parts) > 4 else ''}")

def list_images():
    """List Docker images"""
    cmd = "docker images --format '{{.Repository}}|{{.Tag}}|{{.Size}}|{{.CreatedAt}}|{{.ID}}'"
    
    code, out, err = run_cmd(cmd)
    
    if code != 0:
        print(f"❌ Error: {err}")
        return
    
    print("🖼️  Docker Images:\n")
    print(f"{'Repository':<30} {'Tag':<15} {'Size':<10} {'Created':<20} {'ID'}")
    print("-" * 95)
    
    for line in out.strip().split('\n'):
        if '|' in line:
            parts = line.split('|')
            if len(parts) >= 5:
                print(f"{parts[0][:30]:<30} {parts[1][:15]:<15} {parts[2][:10]:<10} {parts[3][:20]:<20} {parts[4]}")

def container_logs(name, follow=False, tail=50):
    """View container logs"""
    cmd = f"docker logs {'-f' if follow else ''} --tail {tail} {name}"
    code, out, err = run_cmd(cmd)
    
    if code != 0:
        print(f"❌ Error: {err}")
        return
    
    print(out)

def container_stats():
    """Show live container stats"""
    cmd = "docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}'"
    code, out, err = run_cmd(cmd)
    
    if code != 0:
        print(f"❌ Error: {err}")
        return
    
    print("📊 Container Stats:\n")
    print(out)

def container_action(action, name):
    """Start/Stop/Restart container"""
    cmd = f"docker {action} {name}"
    code, out, err = run_cmd(cmd)
    
    if code == 0:
        print(f"✅ Container {action}ed: {name}")
    else:
        print(f"❌ Error: {err}")

def remove_container(name, force=False):
    """Remove container"""
    cmd = f"docker rm {'-f' if force else ''} {name}"
    code, out, err = run_cmd(cmd)
    
    if code == 0:
        print(f"✅ Removed container: {name}")
    else:
        print(f"❌ Error: {err}")

def inspect_container(name):
    """Inspect container details"""
    cmd = f"docker inspect {name}"
    code, out, err = run_cmd(cmd)
    
    if code != 0:
        print(f"❌ Error: {err}")
        return
    
    try:
        data = json.loads(out)[0]
        
        print(f"🔍 Container: {data['Name'].strip('/')}\n")
        print(f"  ID:        {data['Id'][:12]}")
        print(f"  Image:     {data['Config']['Image']}")
        print(f"  Status:    {data['State']['Status']}")
        print(f"  Created:   {data['Created']}")
        print(f"  Ports:     {data['NetworkSettings']['Ports']}")
        
        # Mounts
        if data['Mounts']:
            print(f"\n  Mounts:")
            for m in data['Mounts']:
                print(f"    {m['Source']} -> {m['Destination']} ({m['Type']})")
        
        # Networks
        if data['NetworkSettings']['Networks']:
            print(f"\n  Networks:")
            for net, details in data['NetworkSettings']['Networks'].items():
                print(f"    {net}: {details.get('IPAddress', 'N/A')}")
                
    except json.JSONDecodeError:
        print(out)

def exec_in_container(name, command):
    """Execute command in container"""
    cmd = f"docker exec {name} {command}"
    code, out, err = run_cmd(cmd)
    
    if code == 0:
        print(out)
    else:
        print(f"❌ Error: {err}")

def pull_image(image):
    """Pull Docker image"""
    print(f"📥 Pulling image: {image}")
    cmd = f"docker pull {image}"
    code, out, err = run_cmd(cmd)
    
    if code == 0:
        print(f"✅ Image pulled: {image}")
    else:
        print(f"❌ Error: {err}")

def clean_docker():
    """Clean up unused containers, images, volumes"""
    print("🧹 Cleaning Docker resources...\n")
    
    # Stopped containers
    code, out, _ = run_cmd("docker ps -aq -f status=exited")
    if out.strip():
        run_cmd(f"docker rm {out.strip()}")
        print(f"  Removed {len(out.strip().split())} stopped container(s)")
    
    # dangling images
    code, out, _ = run_cmd("docker images -q -f dangling=true")
    if out.strip():
        run_cmd(f"docker rmi {out.strip()}")
        print(f"  Removed {len(out.strip().split())} dangling image(s)")
    
    # unused volumes
    code, out, _ = run_cmd("docker volume ls -qf dangling=true")
    if out.strip():
        run_cmd(f"docker volume rm {out.strip()}")
        print(f"  Removed {len(out.strip().split())} unused volume(s)")
    
    print("\n✅ Cleanup complete")

def list_networks():
    """List Docker networks"""
    cmd = "docker network ls --format '{{.Name}}|{{.Driver}}|{{.Scope}}'"
    code, out, err = run_cmd(cmd)
    
    if code != 0:
        print(f"❌ Error: {err}")
        return
    
    print("🌐 Docker Networks:\n")
    print(f"{'Name':<20} {'Driver':<15} {'Scope'}")
    print("-" * 50)
    
    for line in out.strip().split('\n'):
        if '|' in line:
            parts = line.split('|')
            if len(parts) >= 3:
                print(f"{parts[0]:<20} {parts[1]:<15} {parts[2]}")

def list_volumes():
    """List Docker volumes"""
    cmd = "docker volume ls --format '{{.Name}}|{{.Driver}}|{{.Mountpoint}}'"
    code, out, err = run_cmd(cmd)
    
    if code != 0:
        print(f"❌ Error: {err}")
        return
    
    print("💾 Docker Volumes:\n")
    print(f"{'Name':<30} {'Driver':<10} {'Mountpoint'}")
    print("-" * 80)
    
    for line in out.strip().split('\n'):
        if '|' in line:
            parts = line.split('|')
            if len(parts) >= 3:
                print(f"{parts[0][:30]:<30} {parts[1]:<10} {parts[2][:40]}")

def container_top(name):
    """Show running processes in container"""
    cmd = f"docker top {name}"
    code, out, err = run_cmd(cmd)
    
    if code != 0:
        print(f"❌ Error: {err}")
        return
    
    print(f"📊 Processes in {name}:\n")
    print(out)

def main():
    parser = argparse.ArgumentParser(description="Docker Container Manager")
    parser.add_argument("command", nargs="?", help="Command to run")
    parser.add_argument("args", nargs="*", help="Arguments")
    parser.add_argument("-a", "--all", action="store_true", help="Show all containers")
    parser.add_argument("-s", "--size", action="store_true", help="Show container sizes")
    parser.add_argument("-f", "--follow", action="store_true", help="Follow logs")
    parser.add_argument("-t", "--tail", type=int, default=50, help="Tail lines for logs")
    parser.add_argument("--force", "-f", action="store_true", help="Force action")
    
    args = parser.parse_args()
    cmd = args.command
    
    if not cmd or cmd == "ps":
        list_containers(args.all, args.size)
    elif cmd == "images":
        list_images()
    elif cmd == "logs" and args.args:
        container_logs(args.args[0], args.follow, args.tail)
    elif cmd == "stats":
        container_stats()
    elif cmd == "start" and args.args:
        container_action("start", args.args[0])
    elif cmd == "stop" and args.args:
        container_action("stop", args.args[0])
    elif cmd == "restart" and args.args:
        container_action("restart", args.args[0])
    elif cmd == "remove" and args.args:
        remove_container(args.args[0], args.force)
    elif cmd == "inspect" and args.args:
        inspect_container(args.args[0])
    elif cmd == "exec" and len(args.args) >= 2:
        exec_in_container(args.args[0], ' '.join(args.args[1:]))
    elif cmd == "pull" and args.args:
        pull_image(args.args[0])
    elif cmd == "clean":
        clean_docker()
    elif cmd == "networks":
        list_networks()
    elif cmd == "volumes":
        list_volumes()
    elif cmd == "top" and args.args:
        container_top(args.args[0])
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
