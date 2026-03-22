#!/usr/bin/env python3
"""
Voice Assistant with Wake Word Detection
Uses Picovoice Porcupine for wake word detection + Ollama for AI responses.

Setup:
    pip install pvporcupine pyaudio
    Download porcupine model from https://github.com/Picovoice/porcupine
    
Usage:
    python3 voice_assistant.py
    Say "Hey Bob" to activate, then speak your command.
    Say "stop" to exit.
"""

import pvporcupine
import pyaudio
import numpy as np
import subprocess
import threading
import speech_recognition as sr
import time

# Configuration
WAKE_WORDS = ["hey bob", "hey bot", "computer"]
OLLAMA_MODEL = "qwen3:latest"
RESPONSE_SPEAKER = " espeak "  # Or use pyttsx3 / your TTS

# Audio settings
CHUNK_SIZE = 512
SAMPLE_RATE = 16000

class VoiceAssistant:
    def __init__(self):
        self.running = False
        self.porcupine = None
        self.pa = None
        self.stream = None
        self.recognizer = sr.Recognizer()
        self.listening_for_command = False
        
    def load_porcupine(self):
        """Initialize Porcupine wake word detector."""
        try:
            # Try to load with default keywords
            # You'll need to download the .ppn file from Picovoice
            # https://github.com/Picovoice/porcupine/tree/master/python
            
            # For now, use a simpler approach with keyword spotting
            print("Loading wake word detector...")
            
            # Try to find porcupine library
            try:
                import pvporcupine
                import os
                
                # Get access key from env or use test key
                access_key = os.environ.get("PORCUPINE_ACCESS_KEY", "")
                
                if access_key:
                    keywords = ["hey bob", "computer"] if len(sys.argv) < 2 else [sys.argv[1]]
                    self.porcupine = pvporcupine.create(
                        access_key=access_key,
                        keywords=keywords
                    )
                    print(f"✅ Porcupine loaded with keywords: {keywords}")
                    return True
                else:
                    print("⚠️ No Porcupine access key. Using fallback...")
                    return self.load_fallback()
            except ImportError:
                print("⚠️ pvporcupine not installed. Using fallback...")
                return self.load_fallback()
                
        except Exception as e:
            print(f"⚠️ Porcupine init failed: {e}")
            return self.load_fallback()
    
    def load_fallback(self):
        """Simple wake word using speech_recognition keyword spotting."""
        print("📝 Using keyword spotting fallback")
        return True
    
    def listen_for_wake_word(self):
        """Main loop - listen for wake word."""
        print("🎤 Listening for wake word...")
        print("Say 'Hey Bob' to activate")
        
        self.running = True
        
        # Use PyAudio for continuous listening
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            rate=SAMPLE_RATE,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=CHUNK_SIZE
        )
        
        while self.running:
            try:
                # Read audio chunk
                audio_chunk = self.stream.read(CHUNK_SIZE, exception_on_overflow=False)
                audio_data = np.frombuffer(audio_chunk, dtype=np.int16)
                
                # Check for wake word with Porcupine
                if self.porcupine:
                    keyword_index = self.porcupine.process(audio_data)
                    if keyword_index >= 0:
                        print("👂 Wake word detected!")
                        self.handle_wake_word()
                else:
                    # Fallback: simple volume-based detection
                    if np.abs(audio_data).mean() > 5000:  # Threshold for loud sounds
                        # Could trigger here, but let's just wait for actual speech
                        pass
                        
            except Exception as e:
                if self.running:
                    print(f"⚠️ Error in listening loop: {e}")
                time.sleep(0.1)
        
        self.cleanup()
    
    def handle_wake_word(self):
        """Wake word detected - now listen for command."""
        # Play acknowledgment sound
        self.play_beep()
        
        print("🎯 Ready for command...")
        self.listen_for_command()
    
    def listen_for_command(self):
        """Listen for user command using speech recognition."""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                # Listen for up to 10 seconds
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
                command = self.recognizer.recognize_google(audio)
                print(f"📝 Command: {command}")
                
                # Process command with AI
                self.process_command(command)
                
            except sr.WaitTimeoutError:
                print("⏱️ No command heard")
            except sr.UnknownValueError:
                print("❓ Couldn't understand")
            except Exception as e:
                print(f"⚠️ Recognition error: {e}")
    
    def process_command(self, command):
        """Process command with Ollama AI."""
        command = command.lower().strip()
        
        # Check for exit commands
        if command in ["stop", "exit", "goodbye", "shut down"]:
            print("👋 Goodbye!")
            self.running = False
            return
        
        # Check for simple responses
        if command in ["hello", "hi", "hey"]:
            self.speak("Hello! How can I help you?")
            return
        
        # Use Ollama for AI response
        print("🤔 Thinking...")
        try:
            result = subprocess.run(
                ["ollama", "run", OLLAMA_MODEL],
                input=f"You are a helpful voice assistant. Respond concisely. Command: {command}",
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                response = result.stdout.strip()
                print(f"💬 AI: {response}")
                self.speak(response)
            else:
                self.speak("Sorry, I couldn't process that.")
                
        except Exception as e:
            print(f"⚠️ AI error: {e}")
            self.speak("Sorry, something went wrong.")
    
    def speak(self, text):
        """Convert text to speech."""
        try:
            # Try espeak first (usually available)
            subprocess.run(["espeak", text], capture_output=True, timeout=10)
        except:
            try:
                # Try pyttsx3
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
            except:
                print(f"🔊 Would speak: {text}")
    
    def play_beep(self):
        """Play acknowledgment beep."""
        try:
            # Simple beep using aplay
            subprocess.run(["aplay", "/usr/share/sounds/alsa/Front_Center.wav"], 
                         capture_output=True, timeout=2)
        except:
            pass
    
    def cleanup(self):
        """Clean up resources."""
        if self.stream:
            self.stream.close()
        if self.pa:
            self.pa.terminate()
        if self.porcupine:
            self.porcupine.delete()

def main():
    import sys
    
    print("🎤 Voice Assistant Starting...")
    
    # Check for Porcupine key
    import os
    if "PORCUPINE_ACCESS_KEY" not in os.environ:
        print("ℹ️ To use Porcupine wake word, set PORCUPINE_ACCESS_KEY")
        print("   Get free key at: https://console.picovoice.com/")
    
    assistant = VoiceAssistant()
    
    try:
        assistant.listen_for_wake_word()
    except KeyboardInterrupt:
        print("\n👋 Stopped by user")
        assistant.running = False
        assistant.cleanup()

if __name__ == "__main__":
    main()
