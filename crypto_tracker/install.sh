#!/bin/bash
# Install crypto tracker as a CLI command

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/crypto.py"

# Create symlink in ~/.local/bin
mkdir -p ~/.local/bin
ln -sf "$PYTHON_SCRIPT" ~/.local/bin/crypto
chmod +x "$PYTHON_SCRIPT"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "Add this to your ~/.bashrc or ~/.zshrc:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

echo "Crypto Tracker installed! Run 'crypto --help' to get started."
