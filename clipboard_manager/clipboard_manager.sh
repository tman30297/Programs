#!/bin/bash
# Clipboard Manager Launcher

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check for pyperclip
python3 -c "import pyperclip" 2>/dev/null || pip install pyperclip

python3 clipboard_manager.py "$@"
