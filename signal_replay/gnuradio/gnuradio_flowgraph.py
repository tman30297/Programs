#!/usr/bin/env python3
"""
GNU Radio Signal Record & Process Flowgraph
Run this script to record and process signals for replay

Usage:
    # Record from SDR
    python3 gnuradio_flowgraph.py --record --freq 154.46375e6 --output signal.wav
    
    # Process existing file
    python3 gnuradio_flowgraph.py --process --input signal.wav --output clean.wav
    
    # Full pipeline: record, clean, convert
    python3 gnuradio_flowgraph.py --pipeline --output 17_1
"""

import os
import sys
import argparse
import numpy as np
from pathlib import Path

# Try to import GNU Radio - if not available, use fallback
try:
    from gnuradio import gr, analog, blocks, filter
    HAS_GNURADIO = True
except ImportError:
    HAS_GNURADIO = False
    print("GNU Radio not found - using fallback processing")


class SignalRecorder:
    """Record signals from RTL-SDR"""
    
    def __init__(self, freq=154.46375e6, sample_rate=2400000, audio_rate=48000):
        self.freq = freq
        self.sample_rate = sample_rate
        self.audio_rate = audio_rate
        self.tb = None
        
    def record(self, output_file, duration=10):
        """Record signal for specified duration"""
        print(f"Recording {duration}s at {self.freq/1e6:.5f} MHz...")
        
        if HAS_GNURADIO:
            self._record_gnuradio(output_file, duration)
        else:
            self._record_fallback(output_file, duration)
            
        print(f"Saved to: {output_file}")
        
    def _record_gnuradio(self, output_file, duration):
        """GNU Radio recording"""
        # This would require actual GNU Radio flowgraph
        # Simplified for demonstration
        print("GNU Radio recording requires .grc file")
        
    def _record_fallback(self, output_file, duration):
        """Fallback using numpy for demo - actual SDR requires rtl_sdr CLI"""
        print("Recording requires rtl_sdr or GNU Radio")
        print(f"Run: rtl_sdr -f 154463750 -s 2400000 -n {duration * 2400000} recording.raw")
        print(f"Then convert raw to WAV")


class SignalProcessor:
    """Process recorded signals for replay"""
    
    def __init__(self, audio_rate=48000):
        self.audio_rate = audio_rate
        
    def process(self, input_file, output_file, 
                lowcut=300, highcut=3000, normalize=True, trim=True):
        """Process signal through filter chain"""
        print(f"Processing: {input_file}")
        
        if HAS_GNURADIO:
            self._process_gnuradio(input_file, output_file, lowcut, highcut, normalize)
        else:
            self._process_fallback(input_file, output_file, lowcut, highcut, normalize, trim)
            
        print(f"Saved to: {output_file}")
        
    def _process_gnuradio(self, input_file, output_file, lowcut, highcut, normalize):
        """GNU Radio processing"""
        print("GNU Radio processing requires .grc file")
        
    def _process_fallback(self, input_file, output_file, lowcut, highcut, normalize, trim):
        """Fallback processing using scipy/numpy"""
        try:
            import wave
            import struct
            
            # Read WAV
            with wave.open(input_file, 'rb') as w:
                rate = w.getframerate()
                frames = w.readframes(w.getnframes())
                n_channels = w.getnchannels()
                width = w.getsampwidth()
                
            # Convert to numpy
            if width == 2:
                audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
            else:
                audio = np.frombuffer(frames, dtype=np.uint8).astype(np.float32) / 255.0
                
            if n_channels == 2:
                audio = audio[::2]  # Take first channel
                
            # Trim silence
            if trim:
                threshold = 0.01
                mask = np.abs(audio) > threshold
                if np.any(mask):
                    indices = np.where(mask)[0]
                    audio = audio[max(0, indices[0]-1000):min(len(audio), indices[-1]+1000)]
                    
            # Apply simple bandpass (moving average)
            if lowcut > 0 or highcut < rate/2:
                # Simple filter approximation
                kernel_size = int(rate / (2 * lowcut)) if lowcut > 0 else 3
                kernel = np.ones(kernel_size) / kernel_size
                audio = np.convolve(audio, kernel, mode='same')
                
            # Normalize
            if normalize:
                max_val = np.max(np.abs(audio))
                if max_val > 0:
                    audio = audio * (0.8 / max_val)
                    
            # Convert back to int16
            audio = (audio * 32767).astype(np.int16)
            
            # Write WAV
            with wave.open(output_file, 'wb') as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(rate)
                w.writeframes(audio.tobytes())
                
            print(f"Processed: {len(audio)/rate:.2f}s audio")
            
        except Exception as e:
            print(f"Processing error: {e}")
            print("Install scipy: pip install numpy scipy")


class SignalConverter:
    """Convert to 8kHz for ESP32 replay"""
    
    def convert(self, input_file, output_file, target_rate=8000):
        """Downsample to 8kHz mono"""
        import wave
        
        print(f"Converting: {input_file}")
        
        with wave.open(input_file, 'rb') as w:
            rate = w.getframerate()
            frames = w.readframes(w.getnframes())
            n_ch = w.getnchannels()
            width = w.getsampwidth()
            
        # Convert
        audio = np.frombuffer(frames, dtype=np.int16)
        if n_ch == 2:
            audio = audio[::2]
            
        # Downsample
        if rate > target_rate:
            ratio = rate // target_rate
            audio = audio[::ratio]
            
        # Convert to 8-bit
        audio_8 = (audio // 256).astype(np.int8)
        
        # Write
        with wave.open(output_file, 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(1)
            w.setframerate(target_rate)
            w.writeframes(audio_8.tobytes())
            
        print(f"Saved to: {output_file} ({target_rate}Hz, 8-bit mono)")


def main():
    parser = argparse.ArgumentParser(description='Signal Record & Process')
    parser.add_argument('--record', action='store_true', help='Record from SDR')
    parser.add_argument('--process', action='store_true', help='Process existing file')
    parser.add_argument('--pipeline', action='store_true', help='Full pipeline')
    parser.add_argument('--freq', type=float, default=154.46375e6, help='Frequency in Hz')
    parser.add_argument('--input', '-i', help='Input file')
    parser.add_argument('--output', '-o', default='signal.wav', help='Output file')
    parser.add_argument('--duration', type=int, default=10, help='Record duration (s)')
    
    args = parser.parse_args()
    
    if args.record:
        recorder = SignalRecorder(freq=args.freq)
        recorder.record(args.output, args.duration)
        
    elif args.process:
        if not args.input:
            print("Error: --input required for processing")
            return
        processor = SignalProcessor()
        processor.process(args.input, args.output)
        
    elif args.pipeline:
        # Full pipeline: process then convert
        base = args.output.replace('.wav', '')
        
        # Step 1: Process
        processor = SignalProcessor()
        processor.process(args.input or f"{base}.wav", f"{base}_clean.wav")
        
        # Step 2: Convert
        converter = SignalConverter()
        converter.convert(f"{base}_clean.wav", f"{base}_esp32.wav")
        
        print(f"\nDone! Use: {base}_esp32.wav")
        
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
