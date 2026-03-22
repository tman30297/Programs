# Media Tools

Collection of media processing utilities.

## Tools

| # | Tool | Description |
|---|------|-------------|
| 1 | Video Thumbnail | Extract frames from videos |
| 2 | Audio Converter | Convert between audio formats |
| 3 | Text-to-Speech | Convert text to audio |
| 4 | Speech-to-Text | Convert audio to text |

## Quick Start

```bash
cd /media/tony/Drive2/Programs/media-tools

# Run launcher
python3 media_tools.py

# Or run individual tools:
python3 video_thumbnail.py video.mp4 -o thumb.jpg -t 5 -w 320
python3 audio_converter.py song.wav -f mp3 -b 320k
python3 text_to_speech.py "Hello world" -o hello.mp3 -l en
python3 speech_to_text.py audio.mp3 -o transcript.txt
```

## Dependencies

```bash
# Python packages
pip install opencv-python gtts pyttsx3 speechrecognition
pip install faster-whisper  # Recommended for STT

# System packages
sudo apt install ffmpeg espeak sox
```

## Video Thumbnail

```bash
python3 video_thumbnail.py <video> [-o output] [-t timestamp] [-w width]
```

## Audio Converter

```bash
python3 audio_converter.py <input> [-o output] [-f format] [-b bitrate]
```

## Text-to-Speech

```bash
python3 text_to_speech.py <text> [-f file] [-o output] [-m method] [-l lang]
```

## Speech-to-Text

```bash
python3 speech_to_text.py <audio> [-o output] [-m method] [-m model]
```
