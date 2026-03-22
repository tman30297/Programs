#!/usr/bin/env python3
"""Audio Converter - Convert between audio formats"""

import argparse
import os
import subprocess
from pathlib import Path

def convert_audio(input_path, output_path=None, format=None, bitrate="192k", 
                  sample_rate=None, channels=None, quality=2):
    """Convert audio between formats using ffmpeg."""
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        return False
    
    # Determine output format
    input_ext = Path(input_path).suffix.lower()
    if format:
        out_format = format.lower()
    elif output_path:
        out_format = Path(output_path).suffix.lower().lstrip('.')
    else:
        # Default to mp3
        out_format = "mp3"
    
    if output_path is None:
        output_path = str(Path(input_path).with_suffix(f".{out_format}"))
    
    if out_format == input_ext.lstrip('.'):
        print("Error: Output format same as input")
        return False
    
    # Build ffmpeg command
    cmd = ["ffmpeg", "-y", "-i", input_path]
    
    # Audio settings
    if out_format in ["mp3"]:
        cmd.extend(["-ab", bitrate])
    elif out_format in ["aac", "m4a"]:
        cmd.extend(["-ab", bitrate])
    elif out_format in ["ogg", "oga"]:
        cmd.extend(["-q:a", str(quality)])
    elif out_format in ["flac"]:
        cmd.extend(["-compression_level", str(quality)])
    
    if sample_rate:
        cmd.extend(["-ar", str(sample_rate)])
    if channels:
        cmd.extend(["-ac", str(channels)])
    
    cmd.append(output_path)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: ffmpeg failed")
            print(result.stderr)
            return False
        
        # Get file size
        size = os.path.getsize(output_path)
        print(f"✓ Converted: {output_path}")
        print(f"  Size: {size/1024:.1f} KB | Format: {out_format}")
        return True
    except FileNotFoundError:
        print("Error: ffmpeg not found. Install with: sudo apt install ffmpeg")
        return False

def get_audio_info(input_path):
    """Get audio file info."""
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", 
           "-show_format", "-show_streams", input_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        import json
        data = json.loads(result.stdout)
        
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "audio":
                print(f"File: {input_path}")
                print(f"  Format: {data.get('format', {}).get('format_name')}")
                print(f"  Duration: {data.get('format', {}).get('duration')}s")
                print(f"  Codec: {stream.get('codec_name')}")
                print(f"  Sample Rate: {stream.get('sample_rate')} Hz")
                print(f"  Channels: {stream.get('channels')}")
                print(f"  Bitrate: {data.get('format', {}).get('bit_rate')} bps")
                return
        print("No audio stream found")
    except Exception as e:
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Convert audio between formats")
    parser.add_argument("input", help="Input audio file")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("-f", "--format", choices=["mp3", "wav", "aac", "m4a", "ogg", "flac", "wma"],
                        help="Output format")
    parser.add_argument("-b", "--bitrate", default="192k", help="Audio bitrate (default: 192k)")
    parser.add_argument("-r", "--sample-rate", type=int, help="Sample rate (e.g., 44100, 48000)")
    parser.add_argument("-c", "--channels", type=int, choices=[1, 2], help="Channels (1=mono, 2=stereo)")
    parser.add_argument("-q", "--quality", type=int, default=2, choices=range(0, 11),
                        help="Quality 0-10 (0=best, 10=worst) for opus/ogg")
    parser.add_argument("-i", "--info", action="store_true", help="Show audio file info")
    
    args = parser.parse_args()
    
    if args.info:
        get_audio_info(args.input)
        return
    
    convert_audio(args.input, args.output, args.format, args.bitrate, 
                  args.sample_rate, args.channels, args.quality)

if __name__ == "__main__":
    main()
