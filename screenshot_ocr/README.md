# Screenshot OCR

Capture screens and extract text using OCR.

## Requirements

```bash
# Python packages
pip install --break-system-packages pillow pytesseract requests

# System packages
sudo apt install tesseract-ocr gnome-screenshot scrot
```

## Usage

```bash
# Take area screenshot and extract text
python screenshot_ocr.py

# Full screen screenshot
python screenshot_ocr.py -m full

# Copy result to clipboard
python screenshot_ocr.py -c

# Save to file
python screenshot_ocr.py -o output.txt

# OCR existing image
python screenshot_ocr.py --no-screenshot image.png

# Use web OCR (no tesseract needed)
python screenshot_ocr.py --web

# Specify language
python screenshot_ocr.py -l spa  # Spanish
```

## Options

| Flag | Description |
|------|-------------|
| `-m, --mode` | Screenshot mode: `full` or `area` |
| `-o, --output` | Output file to save text |
| `-l, --lang` | Language for OCR (default: eng) |
| `-c, --copy` | Copy result to clipboard |
| `-p, --print` | Print extracted text |
| `--no-screenshot` | Skip screenshot, use existing image |
| `--web` | Use OCR.space web API |
