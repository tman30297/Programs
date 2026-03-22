#!/usr/bin/env python3
"""
File Encryption/Decryption Tool
Encrypts files using AES-256-GCM with a password-derived key.
Usage:
    python file_encrypt.py encrypt <file> <password>
    python file_encrypt.py decrypt <encrypted_file> <password>
"""

import argparse
import os
import sys
import hashlib
import secrets
from pathlib import Path

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
except ImportError:
    print("Error: cryptography package not installed.")
    print("Install with: pip install cryptography")
    sys.exit(1)

SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32  # AES-256
ITERATIONS = 100_000
CHUNK_SIZE = 64 * 1024  # 64KB chunks for large files


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 256-bit key from password using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=ITERATIONS,
    )
    return kdf.derive(password.encode())


def encrypt_file(input_path: Path, password: str) -> Path:
    """Encrypt a file using AES-256-GCM."""
    if not input_path.exists():
        print(f"Error: File '{input_path}' not found.")
        sys.exit(1)
    
    # Generate random salt
    salt = secrets.token_bytes(SALT_SIZE)
    
    # Derive key from password
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    
    # Output file
    output_path = input_path.with_suffix(input_path.suffix + '.enc')
    
    # Read entire file (AES-GCM is secure for files, but for very large files
    # we could chunk this - keeping simple for now)
    with open(input_path, 'rb') as f:
        plaintext = f.read()
    
    # Generate unique nonce for this file
    nonce = secrets.token_bytes(NONCE_SIZE)
    
    # Encrypt
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    
    # Write: salt + nonce + ciphertext
    with open(output_path, 'wb') as f:
        f.write(salt + nonce + ciphertext)
    
    # Clear sensitive data from memory
    del key
    del aesgcm
    del plaintext
    del ciphertext
    
    print(f"✓ Encrypted: {input_path.name} -> {output_path.name}")
    print(f"  Original size: {input_path.stat().st_size:,} bytes")
    print(f"  Encrypted size: {output_path.stat().st_size:,} bytes")
    
    return output_path


def decrypt_file(input_path: Path, password: str) -> Path:
    """Decrypt a file using AES-256-GCM."""
    if not input_path.exists():
        print(f"Error: File '{input_path}' not found.")
        sys.exit(1)
    
    if not input_path.suffix.endswith('.enc'):
        print("Warning: File doesn't have .enc extension. Proceeding anyway...")
    
    # Read entire encrypted file
    with open(input_path, 'rb') as f:
        data = f.read()
    
    # Extract salt, nonce, and ciphertext
    salt = data[:SALT_SIZE]
    nonce = data[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
    ciphertext = data[SALT_SIZE + NONCE_SIZE:]
    
    # Derive key from password
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    
    # Decrypt
    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception:
        print(f"\n✗ Decryption failed: Wrong password or corrupted file.")
        # Clean up
        del key
        del aesgcm
        sys.exit(1)
    
    # Output file (remove .enc extension)
    output_path = input_path.with_suffix('')
    if output_path == input_path:
        output_path = input_path.parent / (input_path.name + '.decrypted')
    
    # Handle existing file
    counter = 1
    original_output = output_path
    while output_path.exists():
        output_path = original_output.parent / f"{original_output.stem}_{counter}{original_output.suffix}"
        counter += 1
    
    with open(output_path, 'wb') as f:
        f.write(plaintext)
    
    # Clear sensitive data from memory
    del key
    del aesgcm
    del plaintext
    
    print(f"✓ Decrypted: {input_path.name} -> {output_path.name}")
    print(f"  File size: {output_path.stat().st_size:,} bytes")
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Encrypt/Decrypt files with AES-256-GCM',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s encrypt secret.txt mypassword
  %(prog)s decrypt secret.txt.enc mypassword
  %(prog)s encrypt /path/to/file.txt "complex password with spaces"
        '''
    )
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Encrypt subcommand
    encrypt_parser = subparsers.add_parser('encrypt', help='Encrypt a file')
    encrypt_parser.add_argument('file', type=Path, help='File to encrypt')
    encrypt_parser.add_argument('password', help='Encryption password')
    
    # Decrypt subcommand
    decrypt_parser = subparsers.add_parser('decrypt', help='Decrypt a file')
    decrypt_parser.add_argument('file', type=Path, help='File to decrypt')
    decrypt_parser.add_argument('password', help='Decryption password')
    
    args = parser.parse_args()
    
    if args.command == 'encrypt':
        encrypt_file(args.file, args.password)
    elif args.command == 'decrypt':
        decrypt_file(args.file, args.password)


if __name__ == '__main__':
    main()
