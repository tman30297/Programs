# File Encrypt

Encrypt/decrypt files using AES-256-GCM with password-derived keys.

## Requirements

```bash
pip install cryptography
```

## Usage

```bash
# Encrypt a file
python file_encrypt.py encrypt secret.txt mypassword

# Decrypt a file
python file_encrypt.py decrypt secret.txt.enc mypassword
```

## Details

- **Algorithm:** AES-256-GCM
- **Key Derivation:** PBKDF2-HMAC-SHA256 (100,000 iterations)
- **Salt:** Random 16 bytes (generated per file)
- **Nonce:** Random 12 bytes (generated per file)

Output files get `.enc` extension. Decryption removes it (or adds `.decrypted` if needed).

⚠️ **Warning:** If you lose the password, files cannot be recovered!
