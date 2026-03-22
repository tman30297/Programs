#!/usr/bin/env python3
"""
PDF Manipulator - A CLI tool for PDF operations
Usage: python pdf_manipulator.py [command] [options]

Commands:
    merge      - Merge multiple PDFs into one
    split      - Split a PDF into individual pages
    rotate     - Rotate pages in a PDF
    extract    - Extract pages from a PDF
    info       - Get information about a PDF
    watermark  - Add text watermark to PDF
    compress   - Compress PDF file size
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

try:
    from pypdf import PdfReader, PdfWriter, PageObject
    from pypdf.generic import RectangleObject
except ImportError:
    print("Installing pypdf...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
    from pypdf import PdfReader, PdfWriter, PageObject
    from pypdf.generic import RectangleObject


class PDFManipulator:
    def __init__(self):
        self.supported_extensions = ['.pdf']
    
    def _validate_pdf(self, filepath: str) -> Path:
        """Validate that the file exists and is a PDF."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {path.suffix}")
        return path
    
    def _get_reader(self, filepath: str) -> PdfReader:
        """Create a PdfReader for the given file."""
        return PdfReader(self._validate_pdf(filepath))
    
    def merge(self, input_files: List[str], output: str) -> None:
        """Merge multiple PDF files into one."""
        writer = PdfWriter()
        
        for file in input_files:
            reader = self._get_reader(file)
            for page in reader.pages:
                writer.add_page(page)
        
        output_path = Path(output)
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        print(f"✓ Merged {len(input_files)} files into {output}")
    
    def split(self, input_file: str, output_dir: str, prefix: str = "page") -> None:
        """Split a PDF into individual pages."""
        reader = self._get_reader(input_file)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for i, page in enumerate(reader.pages, 1):
            writer = PdfWriter()
            writer.add_page(page)
            
            output_file = output_path / f"{prefix}_{i:03d}.pdf"
            with open(output_file, 'wb') as f:
                writer.write(f)
        
        print(f"✓ Split into {len(reader.pages)} pages in {output_dir}")
    
    def rotate(self, input_file: str, output: str, degrees: int = 90, 
               pages: Optional[str] = None) -> None:
        """Rotate pages in a PDF. degrees: 90, 180, or 270."""
        reader = self._get_reader(input_file)
        writer = PdfWriter()
        
        page_indices = self._parse_page_range(pages, len(reader.pages))
        
        for i, page in enumerate(reader.pages):
            if i in page_indices:
                page.rotate(degrees)
            writer.add_page(page)
        
        output_path = Path(output)
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        print(f"✓ Rotated {len(page_indices)} pages by {degrees}°")
    
    def extract(self, input_file: str, output: str, pages: str) -> None:
        """Extract specific pages from a PDF."""
        reader = self._get_reader(input_file)
        writer = PdfWriter()
        
        page_indices = self._parse_page_range(pages, len(reader.pages))
        
        for i in page_indices:
            writer.add_page(reader.pages[i])
        
        output_path = Path(output)
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        print(f"✓ Extracted pages to {output}")
    
    def info(self, input_file: str) -> None:
        """Display information about a PDF."""
        reader = self._get_reader(input_file)
        
        print(f"\n📄 PDF Information: {Path(input_file).name}")
        print(f"   Pages: {len(reader.pages)}")
        
        metadata = reader.metadata
        if metadata:
            print(f"   Title: {metadata.get('/Title', 'N/A')}")
            print(f"   Author: {metadata.get('/Author', 'N/A')}")
            print(f"   Subject: {metadata.get('/Subject', 'N/A')}")
            print(f"   Creator: {metadata.get('/Creator', 'N/A')}")
        
        # Page sizes
        print("\n   Page Sizes:")
        for i, page in enumerate(reader.pages, 1):
            mediabox = page.mediabox
            width = float(mediabox.width)
            height = float(mediabox.height)
            print(f"     Page {i}: {width:.1f} x {height:.1f} points")
    
    def watermark(self, input_file: str, output: str, text: str = "CONFIDENTIAL",
                  angle: int = 45, opacity: float = 0.3, font_size: int = 50) -> None:
        """Add a text watermark to all pages."""
        from pypdf.filters import PageExtensions
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        import io
        
        reader = self._get_reader(input_file)
        writer = PdfWriter()
        
        for page in reader.pages:
            # Get page dimensions
            mediabox = page.mediabox
            width = float(mediabox.width)
            height = float(mediabox.height)
            
            # Create watermark overlay
            packet = io.BytesIO()
            c = canvas.Canvas(packet, pagesize=(width, height))
            
            c.setFont("Helvetica-Bold", font_size)
            c.setFillColorGray(0.5, alpha=opacity)
            
            # Draw text at center with rotation
            c.saveState()
            c.translate(width/2, height/2)
            c.rotate(angle)
            c.drawCentredString(0, 0, text)
            c.restoreState()
            
            c.save()
            packet.seek(0)
            
            # Merge watermark
            watermark = PdfReader(packet)
            watermark_page = watermark.pages[0]
            page.merge_page(watermark_page)
            writer.add_page(page)
        
        output_path = Path(output)
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        print(f"✓ Added watermark '{text}' to {len(reader.pages)} pages")
    
    def compress(self, input_file: str, output: str, quality: str = "medium") -> None:
        """Compress PDF file size."""
        reader = self._get_reader(input_file)
        writer = PdfWriter(clip_permanent_files=False)
        
        # Set compression based on quality
        if quality == "low":
            writer.compression_level = 0
        elif quality == "medium":
            writer.compression_level = 6
        else:  # high
            writer.compression_level = 9
        
        for page in reader.pages:
            writer.add_page(page)
        
        output_path = Path(output)
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        original_size = Path(input_file).stat().st_size
        compressed_size = output_path.stat().st_size
        ratio = (1 - compressed_size/original_size) * 100
        
        print(f"✓ Compressed: {original_size/1024:.1f}KB → {compressed_size/1024:.1f}KB ({ratio:.1f}% reduction)")
    
    def _parse_page_range(self, pages: Optional[str], total: int) -> List[int]:
        """Parse page range string like '1-5,7,9-11' into list of indices."""
        if pages is None:
            return list(range(total))
        
        indices = set()
        parts = pages.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                indices.update(range(int(start.strip()) - 1, int(end.strip())))
            else:
                indices.add(int(part) - 1)
        
        return sorted([i for i in indices if 0 <= i < total])


def main():
    parser = argparse.ArgumentParser(
        description="PDF Manipulator - CLI tool for PDF operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Merge command
    merge_parser = subparsers.add_parser("merge", help="Merge multiple PDFs")
    merge_parser.add_argument("-i", "--inputs", nargs="+", required=True, help="Input PDF files")
    merge_parser.add_argument("-o", "--output", required=True, help="Output PDF file")
    
    # Split command
    split_parser = subparsers.add_parser("split", help="Split PDF into pages")
    split_parser.add_argument("-i", "--input", required=True, help="Input PDF file")
    split_parser.add_argument("-o", "--output-dir", required=True, help="Output directory")
    split_parser.add_argument("-p", "--prefix", default="page", help="Output file prefix")
    
    # Rotate command
    rotate_parser = subparsers.add_parser("rotate", help="Rotate PDF pages")
    rotate_parser.add_argument("-i", "--input", required=True, help="Input PDF file")
    rotate_parser.add_argument("-o", "--output", required=True, help="Output PDF file")
    rotate_parser.add_argument("-d", "--degrees", type=int, default=90, choices=[90, 180, 270], help="Rotation degrees")
    rotate_parser.add_argument("-p", "--pages", help="Page range (e.g., '1-5,7,9')")
    
    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract pages from PDF")
    extract_parser.add_argument("-i", "--input", required=True, help="Input PDF file")
    extract_parser.add_argument("-o", "--output", required=True, help="Output PDF file")
    extract_parser.add_argument("-p", "--pages", required=True, help="Page range (e.g., '1-5,7,9')")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Get PDF information")
    info_parser.add_argument("-i", "--input", required=True, help="Input PDF file")
    
    # Watermark command
    watermark_parser = subparsers.add_parser("watermark", help="Add watermark to PDF")
    watermark_parser.add_argument("-i", "--input", required=True, help="Input PDF file")
    watermark_parser.add_argument("-o", "--output", required=True, help="Output PDF file")
    watermark_parser.add_argument("-t", "--text", default="CONFIDENTIAL", help="Watermark text")
    watermark_parser.add_argument("-a", "--angle", type=int, default=45, help="Rotation angle")
    watermark_parser.add_argument("-o", "--opacity", type=float, default=0.3, help="Opacity (0-1)")
    watermark_parser.add_argument("-s", "--font-size", type=int, default=50, help="Font size")
    
    # Compress command
    compress_parser = subparsers.add_parser("compress", help="Compress PDF")
    compress_parser.add_argument("-i", "--input", required=True, help="Input PDF file")
    compress_parser.add_argument("-o", "--output", required=True, help="Output PDF file")
    compress_parser.add_argument("-q", "--quality", default="medium", choices=["low", "medium", "high"], help="Compression quality")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    pdf = PDFManipulator()
    
    try:
        if args.command == "merge":
            pdf.merge(args.inputs, args.output)
        elif args.command == "split":
            pdf.split(args.input, args.output_dir, args.prefix)
        elif args.command == "rotate":
            pdf.rotate(args.input, args.output, args.degrees, args.pages)
        elif args.command == "extract":
            pdf.extract(args.input, args.output, args.pages)
        elif args.command == "info":
            pdf.info(args.input)
        elif args.command == "watermark":
            pdf.watermark(args.input, args.output, args.text, args.angle, args.opacity, args.font_size)
        elif args.command == "compress":
            pdf.compress(args.input, args.output, args.quality)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
