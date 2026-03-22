#!/usr/bin/env python3
"""
Screenshot OCR Tool - Capture screens and extract text
Usage: python3 screenshot_ocr.py [options]

Requirements:
    pip install --break-system-packages pillow pytesseract requests
    sudo apt install tesseract-ocr gnome-screenshot scrot
"""

import argparse
import os
import subprocess
import sys
import tempfile

# Try importing, show helpful error if missing
try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not installed")
    print("Run: pip install --break-system-packages pillow")
    sys.exit(1)

try:
    import pytesseract
except ImportError:
    print("ERROR: pytesseract not installed")
    print("Run: pip install --break-system-packages pytesseract")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("ERROR: requests not installed")
    print("Run: pip install --break-system-packages requests")
    sys.exit(1)


def find_screenshot_tool():
    """Find available screenshot tool on the system."""
    tools = [
        ("gnome-screenshot", ["-a", "-f"]),
        ("scrot", ["-s"]),
        ("maim", ["-s"]),
        ("xfce4-screenshooter", ["-r"]),
    ]
    
    for tool, args in tools:
        result = subprocess.run(["which", tool], capture_output=True)
        if result.returncode == 0:
            return tool, args
    return None, None


def take_screenshot(mode="full"):
    """Take a screenshot using available tool."""
    tool, args = find_screenshot_tool()
    
    if not tool:
        print("No screenshot tool found. Install one of: gnome-screenshot, scrot, maim")
        print("On Ubuntu/Debian: sudo apt install gnome-screenshot scrot")
        sys.exit(1)
    
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        temp_file = f.name
    
    try:
        if tool == "gnome-screenshot":
            if mode == "area":
                cmd = [tool, "-a", "-f", temp_file]
            else:
                cmd = [tool, "-f", temp_file]
        elif tool == "scrot":
            if mode == "area":
                cmd = [tool, "-s", temp_file]
            else:
                cmd = [tool, temp_file]
        elif tool == "maim":
            if mode == "area":
                cmd = ["maim", "-s", temp_file]
            else:
                cmd = ["maim", temp_file]
        
        subprocess.run(cmd, check=True)
        return temp_file
    except subprocess.CalledProcessError:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        return None


def check_tesseract():
    """Check if tesseract is available."""
    try:
        result = subprocess.run(["tesseract", "--version"], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def extract_text_local(image_path, lang=None):
    """Extract text from image using local Tesseract."""
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"Error opening image: {e}")
        return None
    
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    try:
        text = pytesseract.image_to_string(image, lang=lang)
        return text.strip()
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None


def extract_text_web(image_path, lang="en"):
    """Extract text using OCR.space free API (fallback)."""
    print("Using OCR.space web API...")
    
    with open(image_path, "rb") as f:
        files = {"file": f}
        data = {"language": lang, "isOverlayRequired": "false"}
        response = requests.post(
            "https://api.ocr.space/parse/image",
            files=files,
            data=data,
            timeout=30
        )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("IsErroredOnProcessing") == False:
            return result["ParsedResults"][0]["ParsedText"]
        else:
            print(f"OCR API error: {result}")
            return None
    else:
        print(f"OCR API error: {response.status_code}")
        return None


def extract_text(image_path, lang=None, use_web=False):
    """Extract text from image."""
    if use_web:
        return extract_text_web(image_path)
    return extract_text_local(image_path, lang)


def copy_to_clipboard(text):
    """Copy text to clipboard."""
    try:
        subprocess.run(["xclip", "-selection", "clipboard"], 
                      input=text.encode(), check=True)
        print("Text copied to clipboard!")
        return True
    except FileNotFoundError:
        pass
    
    try:
        subprocess.run(["wl-paste"], input=text.encode(), check=True)
        print("Text copied to clipboard!")
        return True
    except FileNotFoundError:
        pass
    
    try:
        subprocess.run(["xsel", "--clipboard", "--input"], 
                      input=text.encode(), check=True)
        print("Text copied to clipboard!")
        return True
    except FileNotFoundError:
        pass
    
    print("No clipboard tool found (xclip, wl-paste, xsel)")
    return False


def save_to_file(text, output_path):
    """Save extracted text to file."""
    with open(output_path, "w") as f:
        f.write(text)
    print(f"Text saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Screenshot OCR - Extract text from screenshots",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Take area screenshot, extract text
  %(prog)s -m full                   # Take full screen screenshot
  %(prog)s -c                        # Copy result to clipboard
  %(prog)s -o output.txt             # Save to file
  %(prog)s --no-screenshot image.png # OCR existing image
  %(prog)s --web                     # Use web OCR (no tesseract needed)

Install dependencies:
  pip install --break-system-packages pillow pytesseract requests
  sudo apt install tesseract-ocr gnome-screenshot scrot
        """
    )
    parser.add_argument("-m", "--mode", choices=["full", "area"], default="area",
                        help="Screenshot mode")
    parser.add_argument("-o", "--output", help="Output file to save text")
    parser.add_argument("-l", "--lang", default="eng", help="Language for OCR (default: eng)")
    parser.add_argument("-p", "--print", action="store_true", help="Print extracted text")
    parser.add_argument("-c", "--copy", action="store_true", help="Copy to clipboard")
    parser.add_argument("--no-screenshot", action="store_true", help="Skip screenshot")
    parser.add_argument("--web", action="store_true", help="Use web OCR")
    parser.add_argument("image_file", nargs="?", help="Image file to process")
    
    args = parser.parse_args()
    
    has_tesseract = check_tesseract()
    use_web = args.web
    
    if not has_tesseract and not use_web:
        print("Tesseract not found!")
        print("Install: sudo apt install tesseract-ocr")
        print("Or use --web flag for web-based OCR")
        sys.exit(1)
    
    image_path = None
    
    if args.no_screenshot and args.image_file:
        if os.path.exists(args.image_file):
            image_path = args.image_file
        else:
            print(f"Image file not found: {args.image_file}")
            sys.exit(1)
    elif not args.no_screenshot:
        print(f"Taking {args.mode} screenshot...")
        image_path = take_screenshot(args.mode)
        
        if not image_path:
            print("Screenshot cancelled or failed")
            sys.exit(1)
    
    print(f"Extracting text from: {image_path}")
    text = extract_text(image_path, args.lang, use_web)
    
    if not text:
        print("No text extracted")
        sys.exit(1)
    
    if args.copy:
        copy_to_clipboard(text)
    
    if args.print or (not args.output and not args.copy):
        print("\n" + "="*50)
        print("EXTRACTED TEXT:")
        print("="*50)
        print(text)
        print("="*50)
    
    if args.output:
        save_to_file(text, args.output)
    
    # Cleanup temp screenshot
    if not args.no_screenshot and image_path and os.path.exists(image_path):
        os.unlink(image_path)


if __name__ == "__main__":
    main()
