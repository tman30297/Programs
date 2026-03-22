# PDF Manipulator

A CLI tool for PDF operations including merge, split, rotate, extract, watermark, and compress.

## Installation

```bash
pip install pypdf reportlab
```

## Usage

```bash
# Get PDF information
python pdf_manipulator.py info -i document.pdf

# Merge multiple PDFs
python pdf_manipulator.py merge -i file1.pdf file2.pdf file3.pdf -o output.pdf

# Split PDF into pages
python pdf_manipulator.py split -i document.pdf -o ./pages/

# Rotate pages (90, 180, or 270 degrees)
python pdf_manipulator.py rotate -i document.pdf -o output.pdf -d 90 -p "1-5,7"

# Extract specific pages
python pdf_manipulator.py extract -i document.pdf -o output.pdf -p "1-5,7,9-10"

# Add watermark
python pdf_manipulator.py watermark -i document.pdf -o output.pdf -t "CONFIDENTIAL" -a 45

# Compress PDF
python pdf_manipulator.py compress -i document.pdf -o output.pdf -q medium
```

## Commands

| Command | Description |
|---------|-------------|
| `merge` | Combine multiple PDFs into one |
| `split` | Split PDF into individual pages |
| `rotate` | Rotate pages by 90/180/270 degrees |
| `extract` | Extract specific pages to new PDF |
| `info` | Display PDF metadata and page info |
| `watermark` | Add text watermark to pages |
| `compress` | Reduce PDF file size |

## Page Range Format

For commands that accept page ranges, use:
- Single page: `5`
- Range: `1-5`
- Multiple: `1-5,7,9-10`
