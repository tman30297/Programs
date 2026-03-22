#!/usr/bin/env python3
"""
Backup Automation Script
A configurable backup utility with compression, encryption, and rotation

Features:
- Backup files and directories
- Compress to tar.gz or zip
- Optional GPG encryption
- Automatic rotation (keep N backups)
- Backup to local or remote locations
- Logging and notifications

Usage:
    python backup_automation.py --source /path/to/backup --destination /backup/location
"""

import os
import sys
import shutil
import tarfile
import zipfile
import gzip
import hashlib
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional

# Try to import gpg for encryption (optional)
try:
    import gnupg
    GPG_AVAILABLE = True
except ImportError:
    GPG_AVAILABLE = False


# --- Configuration ---

BACKUP_VERSION = "1.0.0"
DEFAULT_ROTATION = 7  # Keep 7 backups by default


# --- Logging ---

def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure logging"""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    return logging.getLogger("backup")


# --- Backup Functions ---

def create_tarball(source: Path, destination: Path, compression: str = "gz") -> Path:
    """Create a tar.gz or tar.bz2 archive"""
    mode = f"w:{compression}" if compression in ["gz", "bz2", "xz"] else "w"
    archive_name = f"{destination.name}.tar.{compression}"
    archive_path = destination.parent / archive_name
    
    # Remove existing archive if present
    if archive_path.exists():
        archive_path.unlink()
    
    logger.info(f"Creating archive: {archive_path}")
    
    with tarfile.open(archive_path, mode) as tar:
        tar.add(source, arcname=source.name)
    
    return archive_path


def create_zip(source: Path, destination: Path) -> Path:
    """Create a zip archive"""
    archive_name = f"{destination.name}.zip"
    archive_path = destination.parent / archive_name
    
    if archive_path.exists():
        archive_path.unlink()
    
    logger.info(f"Creating zip: {archive_path}")
    
    shutil.make_archive(str(destination), "zip", source.parent, source.name)
    
    # Rename to correct path
    created_zip = str(destination) + ".zip"
    if os.path.exists(created_zip):
        shutil.move(created_zip, archive_path)
    
    return archive_path


def calculate_checksum(filepath: Path) -> str:
    """Calculate SHA256 checksum of a file"""
    sha256 = hashlib.sha256()
    
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    
    return sha256.hexdigest()


def encrypt_file(filepath: Path, recipient: str, gpg_home: Optional[Path] = None) -> Path:
    """Encrypt a file using GPG"""
    if not GPG_AVAILABLE:
        logger.error("GPG not available. Install python-gnupg: pip install python-gnupg")
        raise ImportError("GPG encryption requires python-gnupg")
    
    gpg = gnupg.GPG(gnupghome=str(gpg_home) if gpg_home else "~/.gnupg")
    
    with open(filepath, "rb") as f:
        encrypted = gpg.encrypt_file(f, recipients=[recipient])
    
    if not encrypted.ok:
        raise RuntimeError(f"GPG encryption failed: {encrypted.status}")
    
    encrypted_path = Path(str(filepath) + ".gpg")
    encrypted_data = str(encrypted)
    
    with open(encrypted_path, "w") as f:
        f.write(encrypted_data)
    
    # Remove original unencrypted file
    filepath.unlink()
    
    logger.info(f"Encrypted: {encrypted_path}")
    return encrypted_path


def rotate_backups(backup_dir: Path, keep: int = DEFAULT_ROTATION):
    """Remove old backups, keeping only the most recent N"""
    if not backup_dir.exists():
        return
    
    # Find all backup files (tar.gz, zip, etc.)
    backups = sorted(
        [f for f in backup_dir.iterdir() if f.is_file() and f.suffix in [".tar", ".gz", ".zip", ".gpg"]],
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    
    # Remove old backups
    for old_backup in backups[keep:]:
        logger.info(f"Removing old backup: {old_backup}")
        old_backup.unlink()


def save_backup_info(backup_path: Path, source: Path, checksum: str):
    """Save backup metadata to a JSON file"""
    info = {
        "version": BACKUP_VERSION,
        "timestamp": datetime.now().isoformat(),
        "source": str(source),
        "backup_file": str(backup_path),
        "checksum_sha256": checksum,
        "size_bytes": backup_path.stat().st_size
    }
    
    info_path = Path(str(backup_path) + ".json")
    
    with open(info_path, "w") as f:
        json.dump(info, f, indent=2)
    
    logger.info(f"Saved metadata: {info_path}")


# --- Main Backup Function ---

def perform_backup(
    source: str,
    destination: str,
    name: Optional[str] = None,
    compression: str = "gz",
    format: str = "tar",
    encrypt: Optional[str] = None,
    gpg_home: Optional[str] = None,
    keep: int = DEFAULT_ROTATION,
    verbose: bool = False
) -> bool:
    """Perform the backup operation"""
    global logger
    logger = setup_logging(verbose)
    
    source_path = Path(source).resolve()
    dest_path = Path(destination).resolve()
    
    # Validate source
    if not source_path.exists():
        logger.error(f"Source does not exist: {source_path}")
        return False
    
    # Create destination directory
    dest_path.mkdir(parents=True, exist_ok=True)
    
    # Generate backup name
    if name:
        backup_name = name
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{source_path.name}_{timestamp}"
    
    # Create temp destination
    temp_dest = dest_path / backup_name
    
    # Create archive
    logger.info(f"Backing up: {source_path} -> {dest_path}")
    
    try:
        if format == "zip":
            archive_path = create_zip(source_path, temp_dest)
        else:
            archive_path = create_tarball(source_path, temp_dest, compression)
        
        # Calculate checksum
        checksum = calculate_checksum(archive_path)
        logger.info(f"Checksum: {checksum}")
        
        # Encrypt if requested
        if encrypt:
            archive_path = encrypt_file(archive_path, encrypt, Path(gpg_home) if gpg_home else None)
        
        # Save metadata
        save_backup_info(archive_path, source_path, checksum)
        
        # Rotate old backups
        rotate_backups(dest_path, keep)
        
        logger.info(f"✅ Backup complete: {archive_path}")
        logger.info(f"   Size: {archive_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Backup failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


# --- CLI Interface ---

def main():
    parser = argparse.ArgumentParser(
        description="Backup automation tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple backup
  backup.py --source /home/user/documents --destination /backup
  
  # With custom name
  backup.py --source /home/user/documents --destination /backup --name mydocs
  
  # Zip format
  backup.py --source /home/user/documents --destination /backup --format zip
  
  # With encryption (requires GPG)
  backup.py --source /home/user/documents --destination /backup --encrypt recipient@example.com
  
  # Keep only 3 backups
  backup.py --source /home/user/documents --destination /backup --keep 3

GPG Encryption:
  Install: pip install python-gnupg
  Make sure you have the recipient's public key in your keyring
        """
    )
    
    parser.add_argument("--source", "-s", required=True, help="Source file or directory to backup")
    parser.add_argument("--destination", "-d", required=True, help="Destination directory for backups")
    parser.add_argument("--name", "-n", help="Custom backup name (default: backup_<source>_<timestamp>)")
    parser.add_argument("--format", choices=["tar", "zip"], default="tar", help="Archive format")
    parser.add_argument("--compression", choices=["gz", "bz2", "xz", "none"], default="gz", 
                       help="Compression type (for tar format)")
    parser.add_argument("--encrypt", "-e", help="Encrypt backup with GPG for recipient")
    parser.add_argument("--gpg-home", help="GPG home directory")
    parser.add_argument("--keep", "-k", type=int, default=DEFAULT_ROTATION, 
                       help=f"Number of backups to keep (default: {DEFAULT_ROTATION})")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    success = perform_backup(
        source=args.source,
        destination=args.destination,
        name=args.name,
        compression=args.compression,
        format=args.format,
        encrypt=args.encrypt,
        gpg_home=args.gpg_home,
        keep=args.keep,
        verbose=args.verbose
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
