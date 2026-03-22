#!/usr/bin/env python3
"""
PDF to Text Converter
Extracts text from PDF files and saves as .txt
"""

import sys
import os
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    print("Installing pypdf...")
    os.system("pip install pypdf")
    from pypdf import PdfReader


def pdf_to_text(pdf_path, output_path=None, verbose=False):
    """Extract text from PDF and save to file."""
    
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        return {"success": False, "error": f"File not found: {pdf_path}"}
    
    if pdf_path.suffix.lower() != '.pdf':
        return {"success": False, "error": "File must be a PDF"}
    
    # Default output: same directory, same name .txt
    if output_path is None:
        output_path = pdf_path.with_suffix('.txt')
    else:
        output_path = Path(output_path)
    
    try:
        reader = PdfReader(str(pdf_path))
        num_pages = len(reader.pages)
        
        if verbose:
            print(f"Processing: {pdf_path.name}")
            print(f"Pages: {num_pages}")
        
        full_text = []
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                full_text.append(f"--- Page {i+1} ---\n{text}")
        
        # Write to file
        output_path.write_text('\n\n'.join(full_text), encoding='utf-8')
        
        return {
            "success": True,
            "pages": num_pages,
            "output": str(output_path),
            "size_kb": output_path.stat().st_size / 1024
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    if len(sys.argv) < 2:
        print("PDF to Text Converter")
        print("Usage: python pdf_to_text.py <pdf_file> [output_txt_file]")
        print("\nExamples:")
        print("  python pdf_to_text.py book.pdf")
        print("  python pdf_to_text.py book.pdf output.txt")
        print("  python pdf_to_text.py /path/to/book.pdf /path/to/output.txt")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = pdf_to_text(pdf_file, output_file, verbose=True)
    
    if result["success"]:
        print(f"\n✅ Success!")
        print(f"   Pages: {result['pages']}")
        print(f"   Output: {result['output']}")
        print(f"   Size: {result['size_kb']:.1f} KB")
    else:
        print(f"\n❌ Error: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
