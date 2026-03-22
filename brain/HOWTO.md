# Brain - HOWTO Guide

A personal knowledge hub for voice memos, YouTube transcripts, notes, and semantic search.

## Quick Start

```bash
# Record a voice memo (30 seconds)
python3 /media/tony/Drive2/Programs/brain/brain.py voice

# Record with custom duration and tags
python3 /media/tony/Drive2/Programs/brain/brain.py voice --duration 60 --tags "idea,project"

# Import YouTube video
python3 /media/tony/Drive2/Programs/brain/brain.py youtube "https://youtube.com/watch?v=..."

# Import multiple videos
python3 /media/tony/Drive2/Programs/brain/brain.py youtube url1 url2 url3

# Add a text note
python3 /media/tony/Drive2/Programs/brain/brain.py note "Your note content here" --title "My Note"

# Search
python3 /media/tony/Drive2/Programs/brain/brain.py search "python asyncio"

# List recent notes
python3 /media/tony/Drive2/Programs/brain/brain.py list

# Show knowledge graph
python3 /media/tony/Drive2/Programs/brain/brain.py graph
```

## Commands

### 🎙️ Voice Memos
```bash
python3 brain.py voice [options]
```

Options:
- `--author NAME` - Who recorded (default: Tony)
- `--tags TAG1,TAG2` - Comma-separated tags
- `--duration SECONDS` - Recording time (default: 30)

The program will record audio from your default microphone, transcribe it using Whisper AI, and save it to your knowledge base.

### 📺 YouTube Import
```bash
python3 brain.py youtube <url1> [url2] [url3...] [options]
```

Options:
- `--author NAME` - Source name (default: YouTube)
- `--tags TAG1,TAG2` - Tags for all imported videos

Downloads audio, transcribes, and saves. Great for educational content, podcasts, or lectures.

### 📝 Text Notes
```bash
python3 brain.py note "content" [options]
```

Options:
- `--title "Title"` - Note title
- `--author NAME` - Author (default: Tony)
- `--tags TAG1,TAG2` - Tags

### 🔍 Search
```bash
python3 brain.py search "query" [--limit N]
```

Uses semantic search (QMD) to find relevant content. Works with natural language queries.

### 📊 Knowledge Graph
```bash
# View connections
python3 brain.py graph

# Link two notes
python3 brain.py link FROM_ID TO_ID --rel "related"
```

### 📋 List Notes
```bash
python3 brain.py list [--limit N]
```

---

## Voice Input Methods

### Method 1: Computer Microphone (Default)

Just run the voice command - it uses your default ALSA/PulseAudio mic:
```bash
python3 brain.py voice
```

Detected devices:
- Device 0: Laptop mic (HDA Intel PCH)
- Device 8: System default
- Device 16: Default (PipeWire/ PulseAudio)

To use a specific device:
```python
# Edit brain.py and change:
sd.query_devices()  # List devices
sd.rec(..., device=0)  # Use specific device
```

### Method 2: XiaoZhi AI Device

The XiaoZhi ESP32 device can send voice data via WebSocket. 

**Setup:**
1. Configure XiaoZhi to stream to your Gateway's WebSocket port
2. Voice data will be received as audio bytes
3. The brain can process incoming WebSocket audio streams

**In OpenClaw:**
Use the xiaozhiclaw skill to capture voice from XiaoZhi and pipe to brain:
```bash
# In your agent or cron job
# Capture voice → transcribe → save to brain
```

### Method 3: OpenClaw Nodes (Phone)

Your paired Android/iOS nodes can capture voice:

**On your phone:**
1. Open OpenClaw node app
2. Use voice input feature
3. Audio is sent to Gateway

**Processing:**
The node audio can be forwarded to brain for transcription via:
- Node's `invoke` command to run brain.py
- Or capture node audio stream directly

---

## Connecting Audio Sources

### XiaoZhi ESP32 → Brain

1. **Configure XiaoZhi** (see xiaozhiclaw skill)
2. Set up WebSocket bridge in OpenClaw
3. Create a pipeline:

```
XiaoZhi Device → WebSocket → OpenClaw Gateway → brain.py --stdin
```

Or modify brain.py to accept stdin audio:
```python
# Add to brain.py
import sys
if not sys.stdin.isatty():
    audio_data = sys.stdin.buffer.read()
    # Process audio_data...
```

### Phone Node → Brain

1. **Pair your phone** with OpenClaw
2. Use node voice capture:
   ```bash
   openclaw nodes invoke <node_id> voice_capture --duration 30
   ```
3. Save audio, then:
   ```bash
   python3 brain.py voice --file /path/to/audio.wav
   ```

---

## File Storage

All data is stored in `/media/tony/Drive2/Brain/`:

```
Brain/
├── brain.db           # SQLite database (metadata, search)
├── notes/             # Text notes (markdown)
├── transcripts/       # YouTube transcripts
├── graph.json         # Knowledge graph connections
└── (QMD index)        # Semantic search index
```

---

## Adding to PATH

Add to your shell for easy access:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="/media/tony/Drive2/Programs/brain:$PATH"

# Or create alias
alias brain='python3 /media/tony/Drive2/Programs/brain/brain.py'
```

Then use:
```bash
brain voice
brain search "python"
```

---

## Troubleshooting

### "PortAudio not found"
```bash
sudo apt install portaudio19-dev python3-pyaudio
```

### "Whisper model not found"
First run will download the model automatically. Models: tiny, base, small, medium, large

### No microphone detected
Check ALSA devices:
```bash
python3 -c "import sounddevice as sd; print(sd.query_devices())"
```

### YouTube download fails
```bash
# Update yt-dlp
pip install --upgrade yt-dlp
```

---

## Integration with OpenClaw

Create a cron job for automated voice transcription:

```bash
# In OpenClaw cron
# Voice memo processing
```

Or use as a tool in your agents:
```python
# In agent code
subprocess.run(['python3', '/media/tony/Drive2/Programs/brain/brain.py', 
                'note', 'Agent learning: ...'])
```

---

For technical details, see README.md
