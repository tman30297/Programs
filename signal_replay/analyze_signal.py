#!/usr/bin/env python3
"""
Signal Quality Analyzer
Tests recorded signals and provides feedback for optimization
"""

import wave
import numpy as np
import sys
from pathlib import Path


def analyze_signal(wav_file):
    """Analyze a recorded signal and provide quality metrics"""
    
    with wave.open(wav_file, 'rb') as w:
        frames = w.readframes(w.getnframes())
        sample_rate = w.getframerate()
        n_channels = w.getnchannels()
        sample_width = w.getsampwidth()
    
    # Convert to float
    if sample_width == 2:
        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    else:
        audio = np.frombuffer(frames, dtype=np.uint8).astype(np.float32) / 255.0
    
    print(f"\n{'='*50}")
    print(f"Signal Analysis: {Path(wav_file).name}")
    print(f"{'='*50}")
    
    # Basic metrics
    duration = len(audio) / sample_rate
    print(f"Duration: {duration:.2f}s")
    print(f"Sample Rate: {sample_rate}Hz")
    print(f"Channels: {n_channels}")
    
    # RMS level
    rms = np.sqrt(np.mean(audio**2))
    print(f"\nRMS Level: {rms:.4f} ({20*np.log10(rms+0.0001):.1f} dB)")
    
    # Peak level
    peak = np.max(np.abs(audio))
    print(f"Peak Level: {peak:.4f} ({20*np.log10(peak+0.0001):.1f} dB)")
    
    # Dynamic range
    print(f"Peak/RMS Ratio: {peak/(rms+0.0001):.1f}x")
    
    # Silence detection
    silence_threshold = 0.01
    non_silent = np.sum(np.abs(audio) > silence_threshold)
    silent_pct = 100 * (len(audio) - non_silent) / len(audio)
    print(f"\nSilence: {silent_pct:.1f}%")
    
    # Frequency analysis (simple)
    fft = np.fft.rfft(audio)
    freqs = np.fft.rfftfreq(len(audio), 1/sample_rate)
    magnitudes = np.abs(fft)
    
    # Find dominant frequency
    dom_idx = np.argmax(magnitudes[1:]) + 1
    dom_freq = freqs[dom_idx]
    print(f"Dominant Freq: {dom_freq:.0f}Hz")
    
    # Energy in voice band (300-3000 Hz)
    voice_band = (freqs > 300) & (freqs < 3000)
    voice_energy = np.sum(magnitudes[voice_band])
    total_energy = np.sum(magnitudes)
    voice_pct = 100 * voice_energy / (total_energy + 0.0001)
    print(f"Voice Band Energy: {voice_pct:.1f}%")
    
    # Quality score
    score = 0
    issues = []
    
    if rms < 0.1:
        issues.append("Level too low - increase gain")
        score -= 30
    elif rms > 0.7:
        issues.append("Level too high - risk of clipping")
        score -= 20
    else:
        score += 30
        
    if peak > 0.95:
        issues.append("Clipping detected!")
        score -= 40
        
    if silent_pct > 30:
        issues.append("Too much silence - trim it")
        score -= 20
        
    if voice_pct < 50:
        issues.append("Low voice band energy - check filtering")
        score -= 20
    else:
        score += 20
        
    if duration > 5:
        issues.append("Signal too long - consider trimming")
        score -= 10
    else:
        score += 10
    
    # Bonus for good metrics
    if 0.2 < rms < 0.5:
        score += 20
        
    score = max(0, min(100, score))
    
    print(f"\n{'='*50}")
    print(f"Quality Score: {score}/100")
    print(f"{'='*50}")
    
    if issues:
        print("\nIssues Found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✓ Signal looks good!")
    
    print("\nRecommendations:")
    if score < 50:
        print("  - Run through signal_processor.py")
        print("  - Check recording gain settings")
    elif score < 80:
        print("  - Minor improvements possible")
        print("  - Try normalize option")
    
    return score


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_signal.py <signal.wav>")
        sys.exit(1)
    
    analyze_signal(sys.argv[1])
