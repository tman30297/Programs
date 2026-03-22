#!/usr/bin/env python3
"""Media Tools Launcher - Quick access to all media tools"""

import subprocess
import sys
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

TOOLS = {
    "1": ("Video Thumbnail Generator", "video_thumbnail.py"),
    "2": ("Audio Converter", "audio_converter.py"),
    "3": ("Text-to-Speech", "text_to_speech.py"),
    "4": ("Speech-to-Text", "speech_to_text.py"),
}

def main():
    print("╔══════════════════════════════════════════╗")
    print("║         MEDIA TOOLS v1.0                  ║")
    print("╠══════════════════════════════════════════╣")
    for key, (name, _) in TOOLS.items():
        print(f"║  {key}. {name:<34} ║")
    print("║  5. Install Dependencies                  ║")
    print("║  q. Quit                                  ║")
    print("╚══════════════════════════════════════════╝")
    
    choice = input("\nSelect tool: ").strip().lower()
    
    if choice == 'q':
        return
    
    if choice == '5':
        print("\nInstalling dependencies...")
        deps = [
            "pip install opencv-python gtts pyttsx3 speechrecognition",
            "pip install faster-whisper",
            "sudo apt install ffmpeg espeak sox"
        ]
        for dep in deps:
            print(f"  $ {dep}")
            os.system(dep)
        return
    
    if choice in TOOLS:
        name, script = TOOLS[choice]
        script_path = SCRIPT_DIR / script
        print(f"\nRunning {name}...")
        os.system(f"python3 {script_path}")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
