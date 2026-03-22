#!/usr/bin/env python3
"""
QR Code Generator - CLI Tool
Generates QR codes from text, URLs, or files.
"""

import argparse
import sys
import os

try:
    import qrcode
    from PIL import Image
except ImportError:
    print("Installing required packages...")
    os.system(f"{sys.executable} -m pip install qrcode[pil] pillow -q")
    import qrcode
    from PIL import Image


def generate_qr(data, output_file=None, fill_color="black", back_color="white", 
                 box_size=10, border=4, error_correction="M"):
    """Generate a QR code from the given data."""
    
    # Map error correction levels
    ec_map = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H
    }
    
    qr = qrcode.QRCode(
        version=None,  # Auto-size
        error_correction=ec_map.get(error_correction.upper(), qrcode.constants.ERROR_CORRECT_M),
        box_size=box_size,
        border=border,
    )
    
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    
    if output_file:
        img.save(output_file)
        print(f"✓ QR code saved to: {output_file}")
    else:
        img.show()
    
    return img


def generate_qr_from_file(input_file, output_file=None, **kwargs):
    """Generate QR code from a file's contents."""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = f.read()
    return generate_qr(data, output_file, **kwargs)


def generate_batch(input_file, output_dir=".", **kwargs):
    """Generate multiple QR codes from a file with one entry per line."""
    os.makedirs(output_dir, exist_ok=True)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    for i, line in enumerate(lines, 1):
        # Create filename from first word or line number
        safe_name = line[:30].replace('/', '_').replace('\\', '_').replace(' ', '_')
        output_file = os.path.join(output_dir, f"qr_{i:03d}_{safe_name}.png")
        
        print(f"[{i}/{len(lines)}] Generating: {line[:50]}...")
        generate_qr(line, output_file, **kwargs)
    
    print(f"\n✓ Generated {len(lines)} QR codes in: {output_dir}")


def print_sample_usage():
    """Print example usage."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                  QR Code Generator v1.0                       ║
╠══════════════════════════════════════════════════════════════╣
║  Examples:                                                   ║
║                                                              ║
║    # Simple text QR                                          ║
║    python qr_generator.py "Hello World"                     ║
║                                                              ║
║    # URL QR with custom colors                               ║
║    python qr_generator.py "https://github.com" -o qr.png    ║
║                                                              ║
║    # From file (single entry)                                ║
║    python qr_generator.py -f myfile.txt -o output.png        ║
║                                                              ║
║    # Batch: one QR per line                                  ║
║    python qr_generator.py -b urls.txt --out-dir qr_codes/   ║
║                                                              ║
║    # Custom styling                                          ║
║    python qr_generator.py "Data" -o qr.png --fill blue      ║
║                    --back white --error H                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")


def main():
    parser = argparse.ArgumentParser(
        description="Generate QR codes from text, URLs, or files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=print_sample_usage() or ""
    )
    
    parser.add_argument("data", nargs="?", help="Text or URL to encode")
    parser.add_argument("-o", "--output", help="Output file path (PNG)")
    parser.add_argument("-f", "--file", help="Read data from file")
    parser.add_argument("-b", "--batch", metavar="FILE", 
                        help="Generate batch QR codes (one per line)")
    parser.add_argument("--out-dir", default=".", 
                        help="Output directory for batch mode")
    
    # Styling options
    parser.add_argument("--fill", "--fill-color", default="black",
                        help="QR code color (default: black)")
    parser.add_argument("--back", "--back-color", default="white",
                        help="Background color (default: white)")
    parser.add_argument("--box-size", type=int, default=10,
                        help="Size of each box (default: 10)")
    parser.add_argument("--border", type=int, default=4,
                        help="Border width in boxes (default: 4)")
    parser.add_argument("--error", "-e", default="M",
                        choices=["L", "M", "Q", "H"],
                        help="Error correction level: L(ow), M(edium), Q(uart), H(igh)")
    
    parser.add_argument("--sample", action="store_true",
                        help="Show usage examples")
    
    args = parser.parse_args()
    
    if args.sample:
        print_sample_usage()
        return
    
    # Determine data source
    if args.batch:
        if not os.path.exists(args.batch):
            print(f"Error: File not found: {args.batch}")
            sys.exit(1)
        generate_batch(args.batch, args.out_dir,
                      fill_color=args.fill, back_color=args.back,
                      box_size=args.box_size, border=args.border,
                      error_correction=args.error)
    
    elif args.file:
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
        generate_qr_from_file(args.file, args.output,
                             fill_color=args.fill, back_color=args.back,
                             box_size=args.box_size, border=args.border,
                             error_correction=args.error)
    
    elif args.data:
        generate_qr(args.data, args.output,
                   fill_color=args.fill, back_color=args.back,
                   box_size=args.box_size, border=args.border,
                   error_correction=args.error)
    else:
        print("Error: No data provided. Use --help for usage information.")
        print("       Use --sample to see examples.")
        sys.exit(1)


if __name__ == "__main__":
    main()
