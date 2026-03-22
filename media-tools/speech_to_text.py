#!/usr/bin/env python3
"""Speech-to-Text - Convert audio to text"""

import argparse
import os
import subprocess
import json
from pathlib import Path

def speech_to_text_whisper(audio_path, model="base", language=None, output=None):
    """Use Whisper for transcription."""
    try:
        import whisper
    except ImportError:
        print("Error: whisper not installed. Run: pip install openai-whisper")
        return None
    
    print(f"Loading Whisper {model} model...")
    model_obj = whisper.load_model(model)
    
    result = model_obj.transcribe(audio_path, language=language)
    text = result["text"]
    
    if output:
        with open(output, 'w') as f:
            f.write(text)
        print(f"✓ Saved to: {output}")
    
    return text

def speech_to_text_google(audio_path, output=None):
    """Use Google Speech Recognition."""
    try:
        import speech_recognition as sr
    except ImportError:
        print("Error: speech_recognition not installed. Run: pip install speechrecognition")
        return None
    
    recognizer = sr.Recognizer()
    
    # Try different audio formats
    audio_file = audio_path
    if audio_path.endswith('.mp3'):
        # Convert to wav first
        wav_path = audio_path.replace('.mp3', '.wav')
        subprocess.run(["ffmpeg", "-y", "-i", audio_path, wav_path], 
                       capture_output=True)
        audio_file = wav_path
    
    try:
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
        
        text = recognizer.recognize_google(audio)
        
        if output:
            with open(output, 'w') as f:
                f.write(text)
            print(f"✓ Saved to: {output}")
        
        return text
    except sr.UnknownValueError:
        print("Error: Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Error: {e}")
        return None

def speech_to_text_faster_whisper(audio_path, model="base", language=None, output=None):
    """Use faster-whisper for transcription."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("Error: faster-whisper not installed. Run: pip install faster-whisper")
        return None
    
    print(f"Loading Faster Whisper {model} model...")
    model_obj = WhisperModel(model, compute_type="int8")
    
    segments, info = model_obj.transcribe(audio_path, language=language)
    
    text_parts = []
    for segment in segments:
        text_parts.append(segment.text)
    
    text = " ".join(text_parts)
    
    if output:
        with open(output, 'w') as f:
            f.write(text)
        print(f"✓ Saved to: {output}")
    
    return text

def list_models():
    """List available Whisper models."""
    print("Whisper models (size decreases as quality decreases):")
    print("  tiny    - ~39 MB  |  fastest")
    print("  base    - ~74 MB  |  fast")
    print("  small   - ~244 MB |  moderate")
    print("  medium  - ~769 MB |  slow")
    print("  large   - ~1550 MB|  slowest")
    print("\nFaster-Whisper models:")
    print("  tiny, base, small, medium, large-v2, large-v3")

def main():
    parser = argparse.ArgumentParser(description="Speech-to-Text converter")
    parser.add_argument("audio", nargs="?", help="Input audio file")
    parser.add_argument("-o", "--output", help="Output text file")
    parser.add_argument("-m", "--method", choices=["whisper", "faster-whisper", "google"], 
                        default="faster-whisper", help="STT method")
    parser.add_argument("--model", default="base", 
                        help="Model name (tiny/base/small/medium/large)")
    parser.add_argument("-l", "--language", 
                        help="Language code (e.g., en, es, fr) - auto-detect if not specified")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    parser.add_argument("-t", "--translate", action="store_true", 
                        help="Translate to English (whisper only)")
    
    args = parser.parse_args()
    
    if args.list_models:
        list_models()
        return
    
    if not args.audio:
        parser.print_help()
        return
    
    if not os.path.exists(args.audio):
        print(f"Error: Audio file not found: {args.audio}")
        return
    
    print(f"Transcribing: {args.audio}")
    
    if args.method == "whisper":
        text = speech_to_text_whisper(args.audio, args.model, args.language, args.output)
    elif args.method == "faster-whisper":
        text = speech_to_text_faster_whisper(args.audio, args.model, args.language, args.output)
    elif args.method == "google":
        text = speech_to_text_google(args.audio, args.output)
    else:
        print(f"Unknown method: {args.method}")
        return
    
    if text:
        print(f"\n=== Transcription ===")
        print(text)
    else:
        print("Transcription failed")

if __name__ == "__main__":
    main()
