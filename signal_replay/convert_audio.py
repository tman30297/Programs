#!/usr/bin/env python3
"""
Convert WAV files to format suitable for ESP32 DAC playback
Usage: python3 convert_audio.py input.wav output.wav
"""

import wave
import sys
import os

def convert_wav(input_file, output_file):
    """Convert WAV to 8-bit mono 8kHz for ESP32 DAC"""
    
    with wave.open(input_file, 'rb') as inp:
        # Read original parameters
        n_channels = inp.getnchannels()
        sample_width = inp.getsampwidth()
        framerate = inp.getframerate()
        n_frames = inp.getnframes()
        
        print(f"Input: {n_channels}ch, {sample_width*8}bit, {framerate}Hz")
        
        # Read audio data
        frames = inp.readframes(n_frames)
        
        # Convert to mono if stereo
        if n_channels == 2:
            # Average channels
            if sample_width == 2:
                import struct
                samples = struct.unpack('<' + 'h' * (n_frames * 2), frames)
                mono = [samples[i] // 2 + samples[i+1] // 2 for i in range(0, len(samples), 2)]
                frames = struct.pack('<' + 'h' * len(mono), *mono)
                n_frames = len(mono)
            else:
                frames = frames[::2]  # Take every other byte for 8-bit stereo
                n_frames //= 2
        
        # Convert to 8-bit
        if sample_width == 2:
            import struct
            samples = struct.unpack('<' + 'h' * n_frames, frames)
            # Convert from signed 16-bit to unsigned 8-bit
            samples_8 = [(s // 256) + 128 for s in samples]
            frames = bytes(samples_8)
        
        # Resample to 8kHz if needed (simple decimation)
        target_rate = 8000
        if framerate != target_rate:
            # Decimate or duplicate samples
            ratio = framerate // target_rate
            if ratio > 1:
                frames = frames[::ratio][:target_rate * (n_frames // ratio)]
                n_frames = len(frames)
    
    # Write output
    with wave.open(output_file, 'wb') as out:
        out.setnchannels(1)
        out.setsampwidth(1)  # 8-bit
        out.setframerate(target_rate)
        out.writeframes(frames)
    
    print(f"Output: 1ch, 8bit, {target_rate}Hz")
    print(f"Saved to: {output_file}")

def batch_convert(input_dir, output_dir):
    """Convert all WAV files in a directory"""
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.wav'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            print(f"\nConverting: {filename}")
            convert_wav(input_path, output_path)

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        convert_wav(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        # Convert in place
        output = sys.argv[1].replace('.wav', '_converted.wav')
        convert_wav(sys.argv[1], output)
    else:
        print("Usage: python3 convert_audio.py <input.wav> [output.wav]")
        print("Or: python3 convert_audio.py <input_dir> <output_dir>")
