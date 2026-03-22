# DevToolkit

Collection of useful CLI utilities for developers.

## Usage

```bash
# Hash a string
devtoolkit.py hash "hello world"

# Base64 encode
devtoolkit.py b64 encode "hello"

# Generate UUID
devtoolkit.py uuid

# Timestamp conversion
devtoolkit.py time 1700000000
devtoolkit.py time "2024-01-01"

# JSON pretty print
devtoolkit.py json '{"a":1}'

# Random password
devtoolkit.py pass -l 20

# Case conversion
devtoolkit.py case "HELLO WORLD" lower
```

## Features

- Hash generation (MD5, SHA1, SHA256, SHA512)
- Base64 encode/decode
- UUID generation
- Timestamp conversion
- JSON pretty print
- Password generation
- String utilities
