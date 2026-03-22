#!/usr/bin/env python3
"""
Backup Utility - Incremental backups with rotation
"""
import argparse
import os
import shutil
import json
from pathlib import Path
from datetime import datetime
import hashlib

def get_file_hash(filepath):
    h = hashlib.md5()
    with open(filepath, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()

def create_backup(src, dest, name=None, exclude=None, dry_run=False):
    src = Path(src).resolve()
    dest = Path(dest).resolve()
    
    if not src.exists():
        print(f"Error: Source {src} does not exist")
        return
    
    exclude = exclude or []
    name = name or src.name
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"{name}_{timestamp}"
    backup_dir = dest / backup_name
    manifest = {
        'source': str(src),
        'timestamp': timestamp,
        'files': [],
        'incremental': False
    }
    
    # Check for previous backup to do incremental
    previous = None
    for d in sorted(dest.glob(f"{name}_*"), reverse=True):
        manifest_file = d / '.manifest.json'
        if manifest_file.exists():
            previous = d
            break
    
    if previous:
        with open(previous / '.manifest.json') as f:
            prev_manifest = json.load(f)
        manifest['incremental'] = True
        manifest['previous_backup'] = str(previous)
        print(f"Incremental backup from: {previous.name}")
    else:
        print(f"Full backup of: {src}")
    
    if not dry_run:
        backup_dir.mkdir(parents=True, exist_ok=True)
    
    file_count = 0
    skipped_count = 0
    
    for f in src.rglob('*'):
        if not f.is_file():
            continue
        
        # Check exclusions
        rel_path = f.relative_to(src)
        if any(excl in str(rel_path) for excl in exclude):
            continue
        
        # Check if incremental and file unchanged
        if previous:
            prev_file = previous / rel_path
            if prev_file.exists():
                try:
                    if get_file_hash(f) == get_file_hash(prev_file):
                        # Link instead of copy
                        if not dry_run:
                            backup_dir.mkdir(parents=True, exist_ok=True)
                            os.link(prev_file, backup_dir / rel_path)
                        file_count += 1
                        skipped_count += 1
                        continue
                except:
                    pass
        
        if not dry_run:
            dest_file = backup_dir / rel_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest_file)
        
        file_count += 1
        manifest['files'].append(str(rel_path))
    
    # Save manifest
    if not dry_run:
        with open(backup_dir / '.manifest.json', 'w') as f:
            json.dump(manifest, f, indent=2)
    
    action = "Would create" if dry_run else "Created"
    print(f"{action} backup: {backup_name}")
    print(f"  Files: {file_count} ({skipped_count} skipped - unchanged)")
    
    # Rotate old backups
    if not dry_run:
        rotate_backups(dest, name)

def rotate_backups(dest, name, keep=5):
    backups = sorted(dest.glob(f"{name}_*"), reverse=True)
    if len(backups) > keep:
        for old in backups[keep:]:
            print(f"  Removing old: {old.name}")
            shutil.rmtree(old)

def list_backups(dest, name=None):
    dest = Path(dest)
    print(f"\nBackups in: {dest}\n")
    
    for d in sorted(dest.glob('*'), reverse=True):
        if not d.is_dir():
            continue
        manifest_file = d / '.manifest.json'
        if manifest_file.exists():
            with open(manifest_file) as f:
                m = json.load(f)
            print(f"  {d.name}")
            print(f"    Files: {len(m.get('files', []))}")
            print(f"    Incremental: {m.get('incremental', False)}")
            if m.get('previous_backup'):
                print(f"    From: {Path(m['previous_backup']).name}")
        else:
            print(f"  {d.name} (no manifest)")

def main():
    parser = argparse.ArgumentParser(description='Backup utility with incremental support')
    sub = parser.add_subparsers()
    
    cp = sub.add_parser('create', help='Create a backup')
    cp.add_argument('source', help='Source directory')
    cp.add_argument('dest', help='Destination backup directory')
    cp.add_argument('-n', '--name', help='Backup name (default: source dir name)')
    cp.add_argument('-e', '--exclude', action='append', default=[], help='Patterns to exclude')
    cp.add_argument('-n', '--dry-run', action='store_true', help='Show what would be done')
    
    lp = sub.add_parser('list', help='List backups')
    lp.add_argument('dest', help='Backup directory')
    lp.add_argument('-n', '--name', help='Filter by name')
    
    args = parser.parse_args()
    
    if hasattr(args, 'source'):
        create_backup(args.source, args.dest, args.name, args.exclude, args.dry_run)
    elif hasattr(args, 'dest'):
        list_backups(args.dest, args.name)

if __name__ == '__main__':
    main()
