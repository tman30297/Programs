#!/usr/bin/env python3
"""
Signal Processor for SDR Replay
Cleans and prepares recorded signals for transmission via SA818-V

Features:
- Noise gate
- Bandpass filter
- Normalize audio levels
- FM deviation adjustment
- Trim silence
"""

import wave
import struct
import sys
import os
from pathlib import Path

try:
    import numpy as np
    from scipy import signal
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    print("Warning: scipy not installed. Run: pip install numpy scipy")


class SignalProcessor:
    def __init__(self, input_file, output_file=None):
        self.input_file = input_file
        self.output_file = output_file or input_file.replace('.wav', '_clean.wav')
        
        # Audio parameters
        self.sample_rate = 8000
        self.target_level = 0.8  # 0-1 range
        
    def load_wav(self):
        """Load WAV file"""
        with wave.open(self.input_file, 'rb') as w:
            self.n_channels = w.getnchannels()
            self.sample_width = w.getsampwidth()
            self.framerate = w.getframerate()
            self.n_frames = w.getnframes()
            self.frames = w.readframes(self.n_frames)
            
        print(f"Loaded: {self.n_channels}ch, {self.sample_width*8}bit, {self.framerate}Hz")
        
        # Convert to numpy array
        if self.sample_width == 2:
            self.audio = np.frombuffer(self.frames, dtype=np.int16)
        else:
            self.audio = np.frombuffer(self.frames, dtype=np.uint8)
            
        # Convert to float 0-1
        self.audio = self.audio.astype(np.float32)
        if self.sample_width == 2:
            self.audio /= 32768.0
        else:
            self.audio /= 255.0
            
        return self.audio
    
    def trim_silence(self, threshold=0.01, min_duration=0.1):
        """Remove silence from start and end"""
        # Find non-silent regions
        mask = np.abs(self.audio) > threshold
        
        if not np.any(mask):
            return self.audio
            
        # Find first and last non-silent sample
        indices = np.where(mask)[0]
        start = max(0, indices[0] - int(min_duration * self.framerate))
        end = min(len(self.audio), indices[-1] + int(min_duration * self.framerate))
        
        self.audio = self.audio[start:end]
        print(f"Trimmed silence: {start/self.framerate:.2f}s - {end/self.framerate:.2f}s")
        
        return self.audio
    
    def apply_noise_gate(self, threshold=0.02):
        """Apply noise gate to remove background noise"""
        mask = np.abs(self.audio) < threshold
        self.audio[mask] = 0
        print(f"Noise gate applied (threshold: {threshold})")
        return self.audio
    
    def normalize(self, target_level=0.8):
        """Normalize audio to target level"""
        max_val = np.max(np.abs(self.audio))
        if max_val > 0:
            self.audio = self.audio * (target_level / max_val)
        print(f"Normalized to {target_level}")
        return self.audio
    
    def apply_bandpass(self, lowcut=300, highcut=3000):
        """Apply bandpass filter (voice frequencies)"""
        if not HAS_SCIPY:
            print("scipy required for bandpass filter")
            return self.audio
            
        nyq = self.framerate / 2
        low = lowcut / nyq
        high = highcut / nyq
        
        # Design filter
        b, a = signal.butter(4, [low, high], btype='band')
        
        # Apply
        self.audio = signal.filtfilt(b, a, self.audio)
        print(f"Bandpass filter applied: {lowcut}Hz - {highcut}Hz")
        
        return self.audio
    
    def fm_deviation_adjust(self, deviation=2500):
        """Adjust FM deviation for proper SA818 transmission"""
        # SA818 expects ~2.5kHz deviation for narrowband
        # This is a simple gain adjustment
        gain = deviation / 2500.0
        self.audio = self.audio * gain
        print(f"FM deviation adjusted: {deviation}Hz")
        return self.audio
    
    def highpass_filter(self, cutoff=200):
        """Remove low frequency rumble"""
        if not HAS_SCIPY:
            return self.audio
            
        nyq = self.framerate / 2
        b, a = signal.butter(2, cutoff/nyq, btype='high')
        self.audio = signal.filtfilt(b, a, self.audio)
        print(f"Highpass filter applied: {cutoff}Hz")
        
        return self.audio
    
    def deemphasize(self):
        """Apply de-emphasis (inverse of pre-emphasis)"""
        if not HAS_SCIPY:
            return self.audio
            
        # Simple RC de-emphasis
        RC = 0.000075  # 75μs standard
        dt = 1.0 / self.framerate
        alpha = RC / (RC + dt)
        
        output = np.zeros_like(self.audio)
        output[0] = self.audio[0]
        
        for i in range(1, len(self.audio)):
            output[i] = alpha * output[i-1] + alpha * (self.audio[i] - self.audio[i-1])
        
        self.audio = output
        print("De-emphasis applied")
        return self.audio
    
    def process(self, trim=True, noise_gate=True, bandpass=True, 
                 normalize=True, highpass=True, deemph=True):
        """Run full processing pipeline"""
        print(f"\nProcessing: {self.input_file}")
        
        # Load
        self.load_wav()
        
        # Processing chain
        if trim:
            self.trim_silence()
            
        if noise_gate:
            self.apply_noise_gate()
            
        if highpass:
            self.highpass_filter()
            
        if bandpass:
            self.apply_bandpass(300, 3000)  # Voice band
            
        if normalize:
            self.normalize(0.8)
            
        if deemph:
            self.deemphasize()
            
        # Final normalize
        self.normalize(0.8)
        
        # Save
        self.save_wav()
        
        return self.output_file
    
    def save_wav(self):
        """Save processed audio"""
        # Convert back to int16
        if self.sample_width == 2:
            output = (self.audio * 32767).astype(np.int16)
            output = output.tobytes()
        else:
            output = (self.audio * 255).astype(np.uint8)
            output = output.tobytes()
            
        # Write WAV
        with wave.open(self.output_file, 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(self.sample_width)
            w.setframerate(self.framerate)
            w.writeframes(output)
            
        print(f"Saved: {self.output_file}")


def process_file(input_file, output_file=None):
    """Process a single file"""
    processor = SignalProcessor(input_file, output_file)
    return processor.process()


def batch_process(input_dir, output_dir=None, pattern="*.wav"):
    """Process all WAV files in directory"""
    input_path = Path(input_dir)
    output_path = Path(output_dir) if output_dir else input_path
    
    files = list(input_path.glob(pattern))
    print(f"Found {len(files)} files to process")
    
    for f in files:
        out_file = output_path / f.name
        process_file(str(f), str(out_file))
    
    print(f"\nProcessed {len(files)} files")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 signal_processor.py <input.wav> [output.wav]")
        print("  python3 signal_processor.py --batch <input_dir> [output_dir]")
        sys.exit(1)
    
    if sys.argv[1] == '--batch':
        input_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
        output_dir = sys.argv[3] if len(sys.argv) > 3 else None
        batch_process(input_dir, output_dir)
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        process_file(input_file, output_file)
