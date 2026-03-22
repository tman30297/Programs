#!/usr/bin/env python3
"""Standalone PDF content extraction script - can be killed if it hangs."""
import sys
from pathlib import Path

if len(sys.argv) < 4:
    print("Usage: pdf_extract_worker.py <pdf_path> <max_pages> <max_chars>")
    sys.exit(1)

pdf_path = sys.argv[1]
max_pages = int(sys.argv[2])
max_chars = int(sys.argv[3])

try:
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    content = []
    
    for page in reader.pages[:max_pages]:
        text = page.extract_text()
        if text:
            text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
            if text:
                content.append(text)
    
    result = '\n\n'.join(content)
    if len(result) > max_chars:
        result = result[:max_chars] + "\n\n[... content truncated ...]"
    
    print(result if result.strip() else "")
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
