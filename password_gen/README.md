# Password Generator

Generate secure random passwords.

## Usage

```bash
# Default 16 char password
python password_gen.py

# Custom length
python password_gen.py -l 24

# No symbols
python password_gen.py -l 20 -s

# Quiet mode (just password)
python password_gen.py -q
```

## Options

| Flag | Description |
|------|-------------|
| `-l, --length` | Password length (default: 16) |
| `-c, --caps` | Include uppercase |
| `-n, --numbers` | Include numbers |
| `-s, --symbols` | Include special symbols |
| `-q, --quiet` | Quiet mode |

Uses `secrets` module for cryptographically secure randomness.
