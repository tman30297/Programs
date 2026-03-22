#!/usr/bin/env python3
"""
Git Repo Manager - Manage multiple git repositories at once
Usage: python git_repo_manager.py [command] [path]
Commands:
  status    - Show status of all repos
  pull      - Pull all repos
  fetch     - Fetch all repos
  list      - List all repos found
  recent    - Show recent commits across all repos
  branch    - Show current branch for all repos
  dirty     - Show repos with uncommitted changes
  backup    - Create backup of all repos (bare clones)
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
import shutil

REPO_DIRS = [
    "/media/tony/Drive2/Programs",
    "/home/tony/.openclaw/workspace",
    "/home/tony/projects",
]

COLORS = {
    'reset': '\033[0m',
    'green': '\033[92m',
    'red': '\033[91m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'bold': '\033[1m',
}

def color(text, color_name):
    return f"{COLORS.get(color_name, '')}{text}{COLORS['reset']}"

def is_git_repo(path):
    return os.path.isdir(os.path.join(path, '.git'))

def get_repos(base_dirs):
    """Find all git repos in given directories."""
    repos = []
    for base in base_dirs:
        if not os.path.exists(base):
            continue
        for root, dirs, files in os.walk(base):
            if '.git' in dirs:
                repos.append(root)
                dirs[:] = []  # Don't descend into subdirs
    return sorted(repos)

def get_repo_name(path):
    """Get short name of repo."""
    return os.path.basename(path)

def get_branch(path):
    """Get current branch."""
    try:
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            cwd=path, capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() or "HEAD detached"
    except:
        return "ERROR"

def get_status(path):
    """Get git status summary."""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=path, capture_output=True, text=True, timeout=5
        )
        if not result.stdout.strip():
            return "clean", color("✓ clean", "green")
        
        lines = result.stdout.strip().split('\n')
        staged = sum(1 for l in lines if l.startswith(('M', 'A', 'D')))
        unstaged = sum(1 for l in lines if l.startswith(('??', ' M')))
        
        status = []
        if staged:
            status.append(f"{color(staged, 'yellow')} staged")
        if unstaged:
            status.append(f"{color(unstaged, 'red')} unstaged")
        
        return "dirty", ", ".join(status)
    except Exception as e:
        return "error", str(e)

def get_remote_status(path):
    """Check if repo is ahead/behind remote."""
    try:
        # Fetch first
        subprocess.run(['git', 'fetch', '--all'], cwd=path, 
                      capture_output=True, timeout=30)
        
        result = subprocess.run(
            ['git', 'rev-list', '--left-right', '--count', 'HEAD...@{upstream}'],
            cwd=path, capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split()
            if len(parts) == 2:
                behind, ahead = int(parts[0]), int(parts[1])
                if behind > 0:
                    return f"{color(behind, 'red')} behind"
                elif ahead > 0:
                    return f"{color(ahead, 'blue')} ahead"
        return ""
    except:
        return ""

def cmd_status(repos, args):
    """Show status of all repos."""
    print(f"\n{color('='*60, 'bold')}")
    print(f"  Git Repository Status - {len(repos)} repos found")
    print(color('='*60, 'reset'))
    
    total_clean = 0
    total_dirty = 0
    
    for repo in repos:
        name = get_repo_name(repo)
        branch = get_branch(repo)
        status, status_text = get_status(repo)
        remote_status = get_remote_status(repo)
        
        if status == "clean":
            total_clean += 1
            icon = color("✓", "green")
        else:
            total_dirty += 1
            icon = color("✗", "red")
        
        print(f"\n{icon} {color(name, 'bold')}")
        print(f"  Branch: {color(branch, 'blue')}")
        print(f"  Path: {repo}")
        print(f"  Status: {status_text}")
        if remote_status:
            print(f"  Remote: {remote_status}")
    
    print(f"\n{color('='*60, 'reset')}")
    print(f"Summary: {color(total_clean, 'green')} clean, {color(total_dirty, 'red')} dirty")

def cmd_pull(repos, args):
    """Pull all repos."""
    print(color("\nPulling all repositories...", "bold"))
    
    success = 0
    failed = 0
    
    for repo in repos:
        name = get_repo_name(repo)
        branch = get_branch(repo)
        
        print(f"\n{color('→', 'blue')} {name} ({branch})...", end=" ", flush=True)
        
        try:
            result = subprocess.run(
                ['git', 'pull'],
                cwd=repo, capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                print(color("✓", "green"))
                if result.stdout.strip():
                    print(f"   {result.stdout.strip()[:100]}")
                success += 1
            else:
                print(color("✗", "red"))
                print(f"   {color(result.stderr.strip()[:100], 'red')}")
                failed += 1
        except Exception as e:
            print(color(f"✗ Error: {e}", "red"))
            failed += 1
    
    print(f"\n{color('='*40, 'reset')}")
    print(f"Pull complete: {color(success, 'green')} success, {color(failed, 'red')} failed")

def cmd_fetch(repos, args):
    """Fetch all repos."""
    print(color("\nFetching all repositories...", "bold"))
    
    for repo in repos:
        name = get_repo_name(repo)
        print(f"{color('→', 'blue')} {name}...", end=" ", flush=True)
        
        try:
            result = subprocess.run(
                ['git', 'fetch', '--all'],
                cwd=repo, capture_output=True, text=True, timeout=30
            )
            print(color("✓", "green") if result.returncode == 0 else color("✗", "red"))
        except:
            print(color("✗", "red"))
    
    print(color("\nFetch complete!", "green"))

def cmd_list(repos, args):
    """List all repos."""
    print(f"\n{color('Found {} git repositories:'.format(len(repos)), 'bold')}\n")
    for i, repo in enumerate(repos, 1):
        branch = get_branch(repo)
        print(f"  {i}. {color(get_repo_name(repo), 'bold')}")
        print(f"     {repo}")
        print(f"     Branch: {color(branch, 'blue')}")

def cmd_recent(repos, args):
    """Show recent commits across all repos."""
    print(f"\n{color('Recent commits across all repos:', 'bold')}\n")
    
    limit = args.limit if hasattr(args, 'limit') else 3
    
    for repo in repos:
        name = get_repo_name(repo)
        try:
            result = subprocess.run(
                ['git', 'log', f'-{limit}', '--oneline', '--pretty=format:%h | %s | %ar'],
                cwd=repo, capture_output=True, text=True, timeout=5
            )
            if result.stdout.strip():
                print(f"{color(name, 'bold')}:")
                for line in result.stdout.strip().split('\n'):
                    print(f"  {line}")
                print()
        except:
            pass

def cmd_branch(repos, args):
    """Show current branch for all repos."""
    print(f"\n{color('Current branches:', 'bold')}\n")
    for repo in repos:
        name = get_repo_name(repo)
        branch = get_branch(repo)
        status, _ = get_status(repo)
        
        if status == "dirty":
            icon = color("●", "red")
        else:
            icon = color("●", "green")
        
        print(f"  {icon} {color(name, 'bold'):30} → {color(branch, 'blue')}")

def cmd_dirty(repos, args):
    """Show repos with uncommitted changes."""
    print(f"\n{color('Repos with uncommitted changes:', 'bold')}\n")
    
    dirty_repos = []
    for repo in repos:
        status, status_text = get_status(repo)
        if status == "dirty":
            dirty_repos.append((repo, status_text))
    
    if not dirty_repos:
        print(color("  All repos are clean!", "green"))
    else:
        for repo, status_text in dirty_repos:
            name = get_repo_name(repo)
            print(f"  {color('✗', 'red')} {color(name, 'bold')}")
            print(f"    {repo}")
            print(f"    {status_text}\n")
    
    print(f"Total: {color(len(dirty_repos), 'red')}/{len(repos)} dirty")

def cmd_backup(repos, args):
    """Create backup of all repos."""
    backup_dir = args.backup_dir if hasattr(args, 'backup_dir') else "/media/tony/Drive2/Programs/backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"git_backup_{timestamp}")
    
    print(color(f"\nCreating backup at: {backup_path}", "bold"))
    os.makedirs(backup_path, exist_ok=True)
    
    for repo in repos:
        name = get_repo_name(repo)
        dest = os.path.join(backup_path, f"{name}.git")
        
        print(f"  Backing up {name}...", end=" ", flush=True)
        
        try:
            # Use git clone --bare
            result = subprocess.run(
                ['git', 'clone', '--bare', repo, dest],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                print(color("✓", "green"))
            else:
                print(color("✗", "red"))
                print(f"    {result.stderr[:100]}")
        except Exception as e:
            print(color(f"✗ {e}", "red"))
    
    print(f"\n{color('Backup complete!', 'green')}")
    print(f"Backup location: {backup_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Manage multiple git repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('command', nargs='?', default='status',
                       help='Command to run (status, pull, fetch, list, recent, branch, dirty, backup)')
    parser.add_argument('path', nargs='?', help='Additional path to scan')
    parser.add_argument('-l', '--limit', type=int, default=3, help='Limit for recent commits')
    parser.add_argument('-d', '--backup-dir', help='Backup directory for backup command')
    
    args = parser.parse_args()
    
    # Build repo dirs
    repo_dirs = REPO_DIRS.copy()
    if args.path:
        repo_dirs.append(args.path)
    
    # Find repos
    repos = get_repos(repo_dirs)
    
    if not repos:
        print(color("No git repositories found!", "red"))
        sys.exit(1)
    
    # Run command
    commands = {
        'status': cmd_status,
        'pull': cmd_pull,
        'fetch': cmd_fetch,
        'list': cmd_list,
        'recent': cmd_recent,
        'branch': cmd_branch,
        'dirty': cmd_dirty,
        'backup': cmd_backup,
    }
    
    cmd = commands.get(args.command)
    if cmd:
        cmd(repos, args)
    else:
        print(f"Unknown command: {args.command}")
        print(f"Available: {', '.join(commands.keys())}")
        sys.exit(1)

if __name__ == "__main__":
    main()
