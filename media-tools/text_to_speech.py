#!/usr/bin/env python3
"""Text-to-Speech - Convert text to audio"""

import argparse
import os
import tempfile
import subprocess
from pathlib import Path

def speak_gtts(text, output_path=None, lang="en", slow=False):
    """Use gTTS for TTS."""
    try:
        from gtts import gTTS
    except ImportError:
        print("Error: gTTS not installed. Run: pip install gtts")
        return None
    
    if output_path is None:
        output_path = tempfile.mktemp(suffix=".mp3")
    
    tts = gTTS(text=text, lang=lang, slow=slow)
    tts.save(output_path)
    return output_path

def speak_pyttsx3(text, output_path=None, voice=0, rate=200, volume=1.0):
    """Use pyttsx3 for offline TTS."""
    try:
        import pyttsx3
    except ImportError:
        print("Error: pyttsx3 not installed. Run: pip install pyttsx3")
        return None
    
    engine = pyttsx3.init()
    
    # Set properties
    engine.setProperty('rate', rate)
    engine.setProperty('volume', volume)
    
    voices = engine.getProperty('voices')
    if voices and voice < len(voices):
        engine.setProperty('voice', voices[voice].id)
    
    if output_path is None:
        output_path = tempfile.mktemp(suffix=".mp3")
    
    engine.save_to_file(text, output_path)
    engine.runAndWait()
    return output_path

def speak_espeak(text, output_path=None, voice="en", speed=170):
    """Use espeak for TTS."""
    if output_path is None:
        output_path = tempfile.mktemp(suffix=".wav")
    
    cmd = ["espeak", "-w", output_path, "-s", str(speed), "-v", voice, text]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    except FileNotFoundError:
        print("Error: espeak not installed. Run: sudo apt install espeak")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error: espeak failed: {e}")
        return None

def list_voices():
    """List available voices."""
    print("=== gTTS Languages ===")
    from gtts.lang import tts_langs
    langs = tts_langs()
    for code in sorted(langs.keys()):
        print(f"  {code}: {langs[code]}")
    
    print("\n=== pyttsx3 Voices ===")
    try:
        import pyttsx3
        engine = pyttsx3.init()
        for i, voice in enumerate(engine.getProperty('voices')):
            print(f"  [{i}] {voice.name} ({voice.languages})")
        engine.stop()
    except:
        pass
    
    print("\n=== espeak Voices ===")
    try:
        result = subprocess.run(["espeak", "--voices"], capture_output=True, text=True)
        for line in result.stdout.split('\n')[1:21]:
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    print(f"  {parts[0]}: {' '.join(parts[2:])}")
    except:
        pass

def main():
    parser = argparse.ArgumentParser(description="Text-to-Speech converter")
    parser.add_argument("text", nargs="?", help="Text to speak")
    parser.add_argument("-f", "--file", help="Input text file")
    parser.add_argument("-o", "--output", help="Output audio file")
    parser.add_argument("-m", "--method", choices=["gtts", "pyttsx3", "espeak"], default="gtts",
                        help="TTS method (default: gtts)")
    parser.add_argument("-l", "--lang", default="en", help="Language code (default: en)")
    parser.add_argument("--slow", action="store_true", help="Speak slowly (gtts only)")
    parser.add_argument("-r", "--rate", type=int, default=200, help="Speech rate (pyttsx3, default: 200)")
    parser.add_argument("-v", "--volume", type=float, default=1.0, help="Volume 0-1 (pyttsx3, default: 1.0)")
    parser.add_argument("--voice", type=int, default=0, help="Voice index (pyttsx3)")
    parser.add_argument("--list-voices", action="store_true", help="List available voices")
    parser.add_argument("-p", "--play", action="store_true", help="Play audio after generation")
    
    args = parser.parse_args()
    
    if args.list_voices:
        list_voices()
        return
    
    # Get text from file or argument
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}")
            return
        with open(args.file, 'r') as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        print("Error: Provide text or -f/--file")
        return
    
    if not text.strip():
        print("Error: Empty text")
        return
    
    # Generate speech
    print(f"Generating speech ({args.method})...")
    
    if args.method == "gtts":
        output = speak_gtts(text, args.output, args.lang, args.slow)
    elif args.method == "pyttsx3":
        output = speak_pyttsx3(text, args.output, args.voice, args.rate, args.volume)
    elif args.method == "espeak":
        output = speak_espeak(text, args.output, args.lang, args.rate)
    else:
        print(f"Unknown method: {args.method}")
        return
    
    if output and os.path.exists(output):
        size = os.path.getsize(output)
        print(f"✓ Saved: {output} ({size/1024:.1f} KB)")
        
        if args.play:
            print("Playing...")
            subprocess.run(["play", output], capture_output=True)
    else:
        print("Failed to generate speech")

if __name__ == "__main__":
    main()
