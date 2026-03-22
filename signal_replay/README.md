# Signal Replay System - Complete Guide

## Hardware Setup

### CYD Pin Connections (Extended Headers)

| SA818-V Pin | CYD Connector | GPIO | Function |
|-------------|---------------|------|----------|
| Pin 6 (RXD) | CN1 | 27 | TX to radio |
| Pin 7 (TXD) | CN1 | 22 | RX from radio |
| Pin 18 (MIC) | P3 | 25 | Audio output (DAC) |
| Pin 5 (PTT) | CN1 | 21 | Push-to-Talk |
| Pin 8 (VCC) | 5V | - | Power |
| GND | GND | - | Ground |

**⚠️ CRITICAL:** Add a 0.1µF to 10µF capacitor in series on the audio line (GPIO 25 → SA818 MIC) to block DC offset and prevent audio "thump"

### Power Requirements
- SA818-V pulls up to 750mA during transmit
- Use dedicated 5V 2A power supply, NOT laptop USB

---

## Signal Recording Workflow

### Step 1: Record with SDR

#### Gqrx (Linux)
```bash
sudo apt install gqrx-sdr
gqrx
```

**Settings:**
- Device: HackRF/BladeRF/B210
- Frequency: 154.46375 MHz
- Mode: NFM
- Filter Width: 8 kHz
- Audio: 48kHz
- Recording: File → Start Recording

#### SDR# + Virtual Audio Cable (Windows)
1. Configure SDR# for your device
2. Set mode to NFM
3. Install Virtual Audio Cable
4. Route SDR# output to VAC
5. Record with Audacity from VAC

### Step 2: Convert to 8kHz Mono
```bash
python3 convert_audio.py recording.wav 17_1.wav
```

### Step 3: Analyze Quality
```bash
python3 analyze_signal.py 17_1.wav
```

### Step 4: Clean the Signal
```bash
python3 signal_processor.py 17_1.wav 17_1_clean.wav
```

### Step 5: Copy to SD Card
```
/17_1.wav
/17_3.wav
/18_1.wav
/18_3.wav
/19_1.wav
/19_3.wav
/20_1.wav
/20_3.wav
/21_1.wav
/21_3.wav
/reset.wav
```

---

## Tone Frequency Configuration

In the code, you can define either:
1. **Tone frequencies** - Hardware-generated sine waves
2. **Audio files** - Pre-recorded WAV files

```cpp
// Example: Tone-based
{"17/1", "", 1000, 0, 200, TFT_RED}
// name, filename(empty), tone1, tone2, duration(ms), color

// Example: File-based  
{"17/1", "17_1.wav", 0, 0, 0, TFT_RED}
// name, filename, tone1(0=use file), tone2, duration, color
```

### Standard Utility Tone Frequencies
Adjust `tone1` values in code to match your protocol:

| Signal | Frequency (Hz) | Duration |
|--------|----------------|----------|
| 17/1   | 1000           | 200ms    |
| 17/3   | 1100           | 200ms    |
| 18/1   | 1200           | 200ms    |
| 18/3   | 1300           | 200ms    |
| 19/1   | 1400           | 200ms    |
| 19/3   | 1500           | 200ms    |
| 20/1   | 1600           | 200ms    |
| 20/3   | 1700           | 200ms    |
| 21/1   | 1800           | 200ms    |
| 21/3   | 1900           | 200ms    |
| RESET  | 2000           | 500ms    |

---

## Advanced: GNU Radio Processing

For more advanced signal processing, use GNU Radio Companion.

### Install
```bash
sudo apt install gnuradio
```

### Flow Graph: Clean & Prepare Signal
```
[File Source] → [Band Pass Filter] → [Noise Gate] → [AGC] → [Rational Resampler] → [File Sink]
                300-3000Hz           Threshold: 0.01   Target: 0.5      48kHz → 8kHz
```

### Flow Graph: Record & Demod
```
[RTL-SDR Source] → [NFM Decode] → [Audio Sink]
  154.46375 MHz    48000 rate       Speaker/File
```

### Example: Record Signal (Python/GR)
```python
#!/usr/bin/env python3
import numpy as np
from gnuradio import gr, analog, blocks, filter

class signal_recorder(gr.top_block):
    def __init__(self, freq=154.46375e6):
        gr.top_block.__init__(self)
        
        # SDR Source (replace with your device)
        self.rtlsdr_source = blocks.rtlsdr_source_c(4800000)
        self.rtlsdr_source.set_center_freq(freq)
        self.rtlsdr_source.set_sample_rate(4800000)
        self.rtlsdr_source.set_gain(20)
        
        # NFM Demod
        self.nfm_demod = analog.nfm_demod_cf(
            channel_rate=48000,
            audio_decimation=10,
            deviation=5000
        )
        
        # Audio to file
        self.sink = blocks.wavfile_sink_nc('recording.wav', 1, 8000, 8)
        
        # Connect
        self.connect(self.rtlsdr_source, self.nfm_demod, self.sink)

if __name__ == '__main__':
    tb = signal_recorder()
    tb.start()
    input("Recording... Press Enter to stop\n")
    tb.stop()
```

---

## Troubleshooting

### No Audio on Replay
- [ ] Check capacitor on audio line (required!)
- [ ] Verify SA818 MIC_IN connection
- [ ] Test with headphones on SA818

### PTT Not Working
- [ ] Check GPIO 21 connection
- [ ] Verify SA818 PTT pin
- [ ] Test: manual ground PTT pin

### SD Card Issues
- [ ] Format as FAT32
- [ ] Use short filenames
- [ ] Check SPI connections

### Signal Quality
- [ ] Run `analyze_signal.py` 
- [ ] Check for clipping
- [ ] Adjust noise gate threshold

---

## Files

| File | Purpose |
|------|---------|
| `ESP32_CYD_SA818.ino` | Main ESP32 code |
| `convert_audio.py` | Convert to 8kHz mono |
| `analyze_signal.py` | Quality check |
| `signal_processor.py` | Clean signals |
| `README.md` | This file |
