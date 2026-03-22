#!/usr/bin/env python3
"""
MP3 to MIDI Converter - Uses Spotify's Basic-Pitch
Converts MP3 files to MIDI using neural network-based automatic music transcription.
"""

import argparse
import os
import sys
from pathlib import Path

import basic_pitch
from basic_pitch.inference import predict_and_save

# Find the bundled model - use ONNX model
PACKAGE_DIR = os.path.dirname(basic_pitch.__file__)
DEFAULT_MODEL = os.path.join(PACKAGE_DIR, "saved_models", "icassp_2022", "nmp.onnx")


def convert_file(input_path: str, output_dir: str = None, verbose: bool = False):
    """
    Convert an audio file (MP3, WAV, FLAC, OGG, M4A) to MIDI.
    
    Args:
        input_path: Path to the input audio file
        output_dir: Output directory (defaults to same directory as input)
        verbose: Enable verbose output
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return False
    
    # Determine output directory
    if output_dir is None:
        output_dir = input_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Converting: {input_path.name}")
    print(f"Output directory: {output_dir}")
    
    try:
        # Run prediction and save MIDI
        predict_and_save(
            audio_path_list=[str(input_path)],
            output_directory=str(output_dir),
            save_midi=True,
            save_notes=False,  # Set True for CSV note events
            save_model_outputs=False,
            sonify_midi=False,
            model_or_model_path=DEFAULT_MODEL
        )
        
        # Find the output MIDI file
        base_name = input_path.stem
        midi_file = output_dir / f"{base_name}_basic_pitch.mid"
        
        if midi_file.exists():
            print(f"✓ Success! MIDI saved to: {midi_file}")
            return True
        else:
            # Basic-pitch might name it differently
            midi_files = list(output_dir.glob(f"{base_name}*.mid"))
            if midi_files:
                print(f"✓ Success! MIDI saved to: {midi_files[0]}")
                return True
            print("Warning: MIDI file not found in output", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"Error during conversion: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Convert MP3 (and other audio formats) to MIDI using Spotify Basic-Pitch",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s song.mp3
  %(prog)s audio.wav -o /output/dir
  %(prog)s track.mp3 -v
        """
    )
    
    parser.add_argument(
        "input",
        help="Path to input audio file (MP3, WAV, FLAC, OGG, M4A)"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output directory (default: same as input file)",
        default=None
    )
    
    parser.add_argument(
        "-v", "--verbose",
        help="Enable verbose output",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    success = convert_file(args.input, args.output, args.verbose)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()