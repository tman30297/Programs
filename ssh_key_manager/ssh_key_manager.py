#!/usr/bin/env python3
"""
SSH Key Manager - Manage SSH keys with ease
Usage: ssh_key_manager.py <command> [options]
Commands:
  list              List all SSH keys
  generate <name>   Generate a new SSH key pair
  add <keyfile>     Add existing key to ssh-agent
  remove <name>    Remove key from ssh-agent
  fingerprint <key> Show key fingerprint
  backup            Backup all public keys
  restore           Restore from backup
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import shutil

SSH_DIR = Path.home() / ".ssh"
AGENT_ENV = os.environ.get("SSH_AUTH_SOCK")

def run_cmd(cmd, capture=True):
    """Run shell command"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def list_keys():
    """List all SSH keys in ~/.ssh"""
    if not SSH_DIR.exists():
        print("❌ No .ssh directory found")
        return
    
    print("📁 SSH Keys in ~/.ssh/\n")
    keys = []
    for f in SSH_DIR.iterdir():
        if f.is_file() and not f.name.endswith('.pub') and not f.name.startswith('.'):
            keys.append(f)
    
    if not keys:
        print("  No private keys found")
        return
    
    for key in sorted(keys):
        pub = key.with_suffix(key.suffix + '.pub')
        status = "✅ loaded" if key.name in load_agent_keys() else "❌ not loaded"
        print(f"  🔑 {key.name}")
        print(f"     Path: {key}")
        print(f"     Status: {status}")
        if pub.exists():
            _, out, _ = run_cmd(f'ssh-keygen -lf {pub}')
            if out:
                print(f"     Fingerprint: {out.strip()}")
        print()

def load_agent_keys():
    """Get keys currently loaded in ssh-agent"""
    if not AGENT_ENV:
        return []
    _, out, _ = run_cmd("ssh-add -l 2>/dev/null")
    return [line.split()[-1] if line.strip() else '' for line in out.split('\n') if line.strip()]

def generate_key(name, key_type="ed25519", bits=None):
    """Generate a new SSH key pair"""
    key_path = SSH_DIR / name
    
    if key_path.exists():
        print(f"❌ Key '{name}' already exists!")
        return False
    
    SSH_DIR.mkdir(mode=0o700, exist_ok=True)
    
    cmd = f'ssh-keygen -t {key_type}'
    if bits:
        cmd += f' -b {bits}'
    cmd += f' -f {key_path} -N "" -C "{name}@$(hostname)"'
    
    print(f"🔐 Generating {key_type} key: {name}")
    code, out, err = run_cmd(cmd)
    
    if code == 0:
        key_path.chmod(0o600)
        key_path.with_suffix(key_path.suffix + '.pub').chmod(0o644)
        print(f"✅ Key generated: {key_path}")
        print(f"   Public key:\n   {key_path.with_suffix(key_path.suffix + '.pub').read_text().strip()}")
        return True
    else:
        print(f"❌ Error: {err}")
        return False

def add_key(keyfile):
    """Add key to ssh-agent"""
    path = Path(keyfile).expanduser()
    if not path.exists():
        path = SSH_DIR / keyfile
    
    if not path.exists():
        print(f"❌ Key not found: {keyfile}")
        return False
    
    path.chmod(0o600)
    code, out, err = run_cmd(f'ssh-add {path}')
    
    if code == 0:
        print(f"✅ Added key to agent: {path.name}")
        return True
    else:
        print(f"❌ Error: {err}")
        return False

def remove_key(name):
    """Remove key from ssh-agent by name or path"""
    keys = list(SSH_DIR.glob(name)) + list(SSH_DIR.glob(f"{name}.pub"))
    if keys:
        for k in keys:
            code, out, err = run_cmd(f'ssh-add -d {k}')
            if code == 0:
                print(f"✅ Removed: {k.name}")
        return True
    return False

def show_fingerprint(keyfile):
    """Show fingerprint of a key"""
    path = Path(keyfile).expanduser()
    if not path.exists():
        path = SSH_DIR / keyfile
    if not path.exists():
        path = SSH_DIR / f"{keyfile}.pub"
    
    if not path.exists():
        print(f"❌ Key not found: {keyfile}")
        return
    
    code, out, err = run_cmd(f'ssh-keygen -lf {path}')
    if code == 0:
        print(f"🔍 Fingerprint for {path.name}:")
        print(f"   {out.strip()}")
    else:
        print(f"❌ Error: {err}")

def backup_keys():
    """Backup all public keys"""
    backup_dir = Path("/media/tony/Drive2/Programs/ssh_keys_backup")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for pub in SSH_DIR.glob("*.pub"):
        dest = backup_dir / pub.name
        shutil.copy2(pub, dest)
        count += 1
        print(f"📦 Backed up: {pub.name}")
    
    if count > 0:
        # Also backup known_hosts
        kh = SSH_DIR / "known_hosts"
        if kh.exists():
            shutil.copy2(kh, backup_dir / "known_hosts")
        print(f"\n✅ Backed up {count} keys to {backup_dir}")
    else:
        print("❌ No public keys found to backup")

def restore_keys():
    """Restore keys from backup"""
    backup_dir = Path("/media/tony/Drive2/Programs/ssh_keys_backup")
    if not backup_dir.exists():
        print(f"❌ No backup found at {backup_dir}")
        return
    
    SSH_DIR.mkdir(mode=0o700, exist_ok=True)
    count = 0
    for pub in backup_dir.glob("*.pub"):
        dest = SSH_DIR / pub.name
        shutil.copy2(pub, dest)
        count += 1
        print(f"🔄 Restored: {pub.name}")
    
    kh = backup_dir / "known_hosts"
    if kh.exists():
        shutil.copy2(kh, SSH_DIR / "known_hosts")
        print(f"🔄 Restored: known_hosts")
    
    print(f"\n✅ Restored {count} keys")

def main():
    parser = argparse.ArgumentParser(description="SSH Key Manager")
    parser.add_argument("command", nargs="?", help="Command to run")
    parser.add_argument("args", nargs="*", help="Arguments for command")
    
    args = parser.parse_args()
    cmd = args.command
    
    if not cmd or cmd == "list":
        list_keys()
    elif cmd == "generate" and args.args:
        generate_key(args.args[0])
    elif cmd == "add" and args.args:
        add_key(args.args[0])
    elif cmd == "remove" and args.args:
        remove_key(args.args[0])
    elif cmd == "fingerprint" and args.args:
        show_fingerprint(args.args[0])
    elif cmd == "backup":
        backup_keys()
    elif cmd == "restore":
        restore_keys()
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
