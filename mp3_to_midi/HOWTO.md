# MP3 to MIDI Converter

A simple CLI tool that converts MP3 (and other audio formats) to MIDI using Spotify's **Basic-Pitch** neural network for automatic music transcription.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

Or just:
```bash
pip install basic-pitch
```

## Usage

### Basic conversion
```bash
python mp3_to_midi.py input.mp3
```

The MIDI file will be saved in the same directory as the input file.

### Specify output directory
```bash
python mp3_to_midi.py song.mp3 -o /path/to/output
```

### Verbose mode (shows model progress)
```bash
python mp3_to_midi.py track.mp3 -v
```

### Make executable
```bash
chmod +x mp3_to_midi.py
./mp3_to_midi.py audio.mp3
```

## Supported Input Formats

- MP3
- WAV
- FLAC
- OGG
- M4A

## How It Works

Spotify's Basic-Pitch is a neural network trained for polyphonic note transcription. It:
1. Analyzes the audio spectrum
2. Detects pitch frequencies
3. Identifies note onsets
4. Outputs a MIDI file with the detected notes

## Tips for Best Results

- **Clean recordings work best** - Isolated instruments or solo recordings
- **Avoid full mixes** - Background instruments may cause errors
- **High quality audio** - Better sample rate = better results
- **Expect 80-90% accuracy** - Perfect transcription is still an unsolved problem

## Troubleshooting

### "Module not found" error
Make sure dependencies are installed:
```bash
pip install basic-pitch
```

### Poor transcription quality
- Try with a cleaner recording (isolated instrument)
- Audio with clear melodic content works best
- Heavy bass or drums can interfere with note detection