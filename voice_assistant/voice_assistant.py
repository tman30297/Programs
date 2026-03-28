#!/usr/bin/env python3
"""
Voice Assistant - Whisper STT + Ollama AI
Supports both one-shot and continuous wake-word modes.

Usage:
    python3 voice_assistant.py          # One-shot mode (press Enter)
    python3 voice_assistant.py --wake   # Continuous mode (says "hey bob" to activate)
"""

import subprocess
import pyaudio
import wave
import numpy as np
import threading
import time
from faster_whisper import WhisperModel

# Configuration
OLLAMA_MODEL = "qwen3:latest"
WAKE_WORD = "hey bob"
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
SILENCE_THRESHOLD = 500  # Volume threshold for VAD

# Load Whisper model
print("Loading Whisper model...")
WHISPER_MODEL = WhisperModel("base", device="cpu", compute_type="int8")
print("✓ Whisper ready")

class VoiceAssistant:
    def __init__(self):
        self.running = False
        self.hearing_command = False
        self.audio_buffer = []
        self.in_speech = False
        self.silence_count = 0
    
    def vad_loop(self):
        """Continuous VAD + wake word loop."""
        p = pyaudio.PyAudio()
        
        # Find mic
        mic_index = None
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                try:
                    test = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, 
                                  input=True, input_device_index=i, frames_per_buffer=CHUNK_SIZE)
                    test.close()
                    mic_index = i
                    print(f"✓ Using mic {i}: {dev['name']}")
                    break
                except:
                    continue
        
        if mic_index is None:
            print("❌ No mic found")
            return
        
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, 
                      input=True, input_device_index=mic_index, frames_per_buffer=CHUNK_SIZE)
        
        self.running = True
        print("👂 Listening for 'hey bob'... (continuous mode)")
        print("   Say 'hey bob' to activate, then speak your command")
        print("   Say 'stop' to exit")
        
        frames_buffer = []
        
        while self.running:
            try:
                data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                
                # VAD: check volume
                audio_np = np.frombuffer(data, dtype=np.int16)
                volume = np.abs(audio_np).mean()
                
                if volume > SILENCE_THRESHOLD:
                    if not self.in_speech:
                        print("🎤 Speech detected...")
                    self.in_speech = True
                    self.silence_count = 0
                    frames_buffer.append(data)
                else:
                    if self.in_speech:
                        self.silence_count += 1
                        frames_buffer.append(data)
                        
                        # End of speech - check if wake word
                        if self.silence_count > 20:  # ~0.6 seconds of silence
                            if frames_buffer:
                                # Save and transcribe
                                wf = wave.open("/tmp/wake.wav", 'wb')
                                wf.setnchannels(CHANNELS)
                                wf.setsampwidth(p.get_sample_size(FORMAT))
                                wf.setframerate(RATE)
                                wf.writeframes(b''.join(frames_buffer))
                                wf.close()
                                
                                text = self.transcribe("/tmp/wake.wav")
                                if text:
                                    print(f"📝 Heard: {text}")
                                    if WAKE_WORD in text.lower():
                                        self.handle_wake_word()
                                
                                frames_buffer = []
                            self.in_speech = False
                            
            except Exception as e:
                if self.running:
                    print(f"Error: {e}")
                time.sleep(0.1)
        
        stream.close()
        p.terminate()
    
    def handle_wake_word(self):
        """Wake word detected - beep and listen for command."""
        self.play_beep()
        print("🎯 Listening for command...")
        
        # Record command
        audio_file = self.record_command()
        if audio_file:
            text = self.transcribe(audio_file)
            if text:
                print(f"📝 Command: {text}")
                self.process_command(text)
    
    def record_command(self):
        """Record a command after wake word."""
        p = pyaudio.PyAudio()
        
        mic_index = 0
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                mic_index = i
                break
        
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                       input=True, input_device_index=mic_index, frames_per_buffer=CHUNK_SIZE)
        
        print("🔴 Recording command...")
        frames = []
        silent_frames = 0
        
        # Record until silence
        while silent_frames < 50:  # ~3 seconds max
            data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            frames.append(data)
            
            audio_np = np.frombuffer(data, dtype=np.int16)
            if np.abs(audio_np).mean() < SILENCE_THRESHOLD:
                silent_frames += 1
            else:
                silent_frames = 0
        
        stream.close()
        p.terminate()
        
        wf = wave.open("/tmp/command.wav", 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        return "/tmp/command.wav"
    
    def transcribe(self, audio_file):
        """Transcribe audio with Whisper."""
        try:
            segments, info = WHISPER_MODEL.transcribe(audio_file, language="en")
            text = " ".join([seg.text.strip() for seg in segments])
            return text
        except Exception as e:
            print(f"Transcribe error: {e}")
            return ""
    
    def process_command(self, command):
        """Process command with Ollama AI."""
        command = command.lower().strip()
        
        if command in ["stop", "exit", "goodbye", "quit"]:
            print("👋 Goodbye!")
            self.running = False
            return
        
        print("🤔 Thinking...")
        try:
            result = subprocess.run(
                ["ollama", "run", OLLAMA_MODEL, command],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                response = result.stdout.strip()
                if ">>>" in response:
                    response = response.split(">>>")[-1].strip()
                print(f"💬 AI: {response}")
                self.speak(response)
            else:
                self.speak("Sorry, I couldn't process that.")
                
        except subprocess.TimeoutExpired:
            self.speak("Sorry, that took too long.")
        except Exception as e:
            print(f"⚠️ AI error: {e}")
            self.speak("Sorry, something went wrong.")
    
    def speak(self, text):
        """Convert text to speech."""
        try:
            subprocess.run(["espeak", text], capture_output=True, timeout=15)
        except:
            print(f"🔊 Would speak: {text}")
    
    def play_beep(self):
        """Play acknowledgment beep."""
        try:
            subprocess.run(["aplay", "-q", "/usr/share/sounds/alsa/Front_Center.wav"], 
                         capture_output=True, timeout=2)
        except:
            pass

def one_shot_mode():
    """Original one-shot mode - press Enter to listen."""
    print("\n🎤 One-shot mode selected")
    print("📦 Using Whisper (local STT) + Ollama (local AI)")
    print("🎯 Press Enter to start listening, say 'exit' to quit")
    
    assistant = VoiceAssistant()
    
    while True:
        input("\nPress Enter to listen...")
        
        audio_file = assistant.record_command()
        if audio_file:
            text = assistant.transcribe(audio_file)
            if text:
                print(f"📝 You said: {text}")
                result = assistant.process_command(text)
                if result == "exit":
                    break

def wake_mode():
    """Continuous wake-word mode."""
    print("\n🎤 Wake-word mode selected")
    print("👂 Say 'hey bob' to activate")
    
    assistant = VoiceAssistant()
    
    try:
        assistant.vad_loop()
    except KeyboardInterrupt:
        print("\n👋 Stopped")
        assistant.running = False

def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--wake":
        wake_mode()
    else:
        one_shot_mode()

if __name__ == "__main__":
    main()
