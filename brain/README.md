# Brain - Technical Documentation

## Overview

Brain is a personal knowledge management system that combines:
- **Voice transcription** (local Whisper AI)
- **YouTube import** (download + transcript)
- **Semantic search** (QMD vector embeddings)
- **Knowledge graph** (SQLite + JSON)
- **Notes** (markdown + metadata)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Brain                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐               │
│  │  Voice  │   │ YouTube  │   │  Notes   │   ← INPUTS   │
│  │  Input  │   │  Import  │   │  Manual  │               │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘               │
│       │              │              │                       │
│       ▼              ▼              ▼                       │
│  ┌─────────────────────────────────────────┐                │
│  │         Transcription (Whisper)         │                │
│  └─────────────────┬───────────────────────┘                │
│                    │                                        │
│                    ▼                                        │
│  ┌─────────────────────────────────────────┐                │
│  │     Storage Layer                       │                │
│  │  ┌─────────┐  ┌─────────┐  ┌────────┐  │                │
│  │  │ SQLite  │  │ Markdown│  │  QMD   │  │                │
│  │  │   DB    │  │  Files  │  │ Index  │  │                │
│  │  └────┬────┘  └─────────┘  └────┬───┘  │                │
│  │       │                          │       │                │
│  │  Metadata                       │       │                │
│  │  + Tags                         │       │                │
│  │  + Timestamps        Semantic   │       │                │
│  │  + Relationships      Search    │       │                │
│  └────────────────────────┬────────┘       │                │
│                           │                 │                │
│                           ▼                 │                │
│  ┌─────────────────────────────────────────┐│ OUTPUTS       │
│  │  Search / Query / Graph View            ││                │
│  └─────────────────────────────────────────┘│                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. SQLite Database (`brain.db`)

**Tables:**

```sql
-- Notes (voice memos, manual notes)
CREATE TABLE notes (
    id INTEGER PRIMARY KEY,
    content TEXT NOT NULL,
    author TEXT,          -- who created
    source TEXT,          -- voice, manual, youtube
    created_at TIMESTAMP,
    tags TEXT,            -- comma-separated
    title TEXT
);

-- YouTube Transcripts
CREATE TABLE transcripts (
    id INTEGER PRIMARY KEY,
    title TEXT,
    url TEXT,
    content TEXT NOT NULL,
    author TEXT,
    source TEXT DEFAULT 'youtube',
    duration TEXT,
    created_at TIMESTAMP,
    tags TEXT
);

-- Knowledge Graph Connections
CREATE TABLE graph_edges (
    id INTEGER PRIMARY KEY,
    from_note_id INTEGER,
    to_note_id INTEGER,
    relationship TEXT,
    FOREIGN KEY (from_note_id) REFERENCES notes(id),
    FOREIGN KEY (to_note_id) REFERENCES notes(id)
);
```

### 2. File Storage

```
/media/tony/Drive2/Brain/
├── brain.db           # SQLite database
├── notes/             # Individual note files
│   └── YYYYMMDD_HHMMSS.md
├── transcripts/      # YouTube transcripts
│   └── YYYYMMDD_HHMMSS_title.md
└── graph.json         # Knowledge graph
```

### 3. QMD Integration

QMD (Query Markup Documents) provides semantic search:

- **Vector embeddings** - Find semantically similar content
- **BM25** - Keyword search
- **Hybrid** - Combine both

When notes/transcripts are added, they're indexed in QMD:
```bash
qmd index add --root /media/tony/Drive2/Brain \
    --path /path/to/note.md \
    --collection brain
```

Search uses:
```bash
qmd search "query" --root /media/tony/Drive2/Brain \
    --collection brain -n 5
```

## Voice Processing Pipeline

```
1. Recording
   ┌─────────────────────────────────────┐
   │ sounddevice.rec()                   │
   │ - Sample rate: 16000 Hz             │
   │ - Channels: 1 (mono)                │
   │ - Format: int16                     │
   └─────────────────┬───────────────────┘
                     │
                     ▼
2. Audio Format Conversion
   ┌─────────────────────────────────────┐
   │ ffmpeg -f s16le -ar 16000           │
   │   -ac 1 -i - output.wav             │
   │ (converts to WAV for Whisper)       │
   └─────────────────┬───────────────────┘
                     │
                     ▼
3. Transcription
   ┌─────────────────────────────────────┐
   │ faster-whisper.WhisperModel()        │
   │ - Model: base (int8 CPU)             │
   │ - Output: text segments             │
   └─────────────────┬───────────────────┘
                     │
                     ▼
4. Storage
   ┌─────────────────────────────────────┐
   │ - Save to SQLite (metadata)          │
   │ - Save to Markdown (content)        │
   │ - Index in QMD (search)              │
   └─────────────────────────────────────┘
```

## YouTube Processing Pipeline

```
1. URL Input
   ┌─────────────────────────────────────┐
   │ python brain.py youtube <urls>      │
   └─────────────────┬───────────────────┘
                     │
                     ▼
2. Get Video Info
   ┌─────────────────────────────────────┐
   │ yt-dlp --print '%(title)s|%(duration)s'
   │ → Extracts title & length           │
   └─────────────────┬───────────────────┘
                     │
                     ▼
3. Download Audio
   ┌─────────────────────────────────────┐
   │ yt-dlp -x --audio-format wav       │
   │ → Downloads best audio, converts    │
   └─────────────────┬───────────────────┘
                     │
                     ▼
4. Transcribe (same as voice)
   ┌─────────────────────────────────────┐
   │ faster-whisper (base model)         │
   └─────────────────┬───────────────────┘
                     │
                     ▼
5. Storage
   ┌─────────────────────────────────────┐
   │ - SQLite: title, url, content       │
   │ - Markdown: full transcript        │
   │ - QMD: indexed for search          │
   └─────────────────────────────────────┘
```

## Search System

### Semantic Search (QMD)
```bash
# Natural language queries
qmd search "how does asyncio gather work"
qmd search "rust ownership explained"
```

### SQLite Search (Fallback)
```sql
-- Keyword + filters
SELECT * FROM notes 
WHERE content LIKE '%python%' 
  AND author = 'Tony'
  AND created_at > '2026-01-01';
```

### Combined Approach
1. **Semantic**: "What notes about Python?"
2. **Filter**: By date, author, tags
3. **Graph**: Related ideas

## Knowledge Graph

Connections between notes:

```json
{
  "nodes": [
    {"id": 1, "title": "Voice Memo 1", "type": "note"},
    {"id": 2, "title": "YouTube: Rust Tutorial", "type": "transcript"}
  ],
  "edges": [
    {"from": 1, "to": 2, "relationship": "related_to"}
  ]
}
```

Use cases:
- Link research notes to source videos
- Connect voice memos to follow-up notes
- Track idea evolution

## Audio Input Methods

### 1. Local Microphone
```python
import sounddevice as sd
audio = sd.rec(frames, samplerate=16000, channels=1)
sd.wait()
```

### 2. XiaoZhi ESP32 Device

**Connection:**
1. XiaoZhi → WiFi → Gateway WebSocket
2. Gateway forwards to brain

**Protocol:**
- Audio chunks sent as binary WebSocket messages
- brain.py receives via stdin or socket

**Integration:**
```python
# In xiaozhiclaw skill or custom handler
def on_audio_chunk(chunk):
    # Send to brain
    subprocess.run(['python3', 'brain.py', 'voice', '--stdin'], 
                   input=chunk)
```

### 3. OpenClaw Node (Phone)

**Flow:**
1. Node captures audio via app
2. Sends to Gateway via WebRTC/websocket
3. Gateway forwards to brain

**Commands:**
```bash
# Capture from node
openclaw nodes invoke <node_id> voice_capture --duration 30

# Process result
python3 brain.py voice --file /path/to/node_audio.wav
```

## Dependencies

```bash
# Core
pip install faster-whisper sounddevice

# System
sudo apt install portaudio19-dev ffmpeg

# YouTube
pip install yt-dlp

# QMD (for semantic search)
bun install -g https://github.com/tobi/qmd
```

## Performance Notes

- **Whisper model**: `base` is good balance speed/accuracy
  - `tiny`: ~1GB, 10x realtime
  - `base`: ~1GB, 4x realtime
  - `small`: ~2GB, 2x realtime
- **CPU**: Works on CPU (int8 mode)
- **GPU**: Optional CUDA acceleration

## Extending Brain

### Adding New Input Sources

1. Create processing function
2. Save to SQLite + Markdown
3. Index in QMD
4. Update CLI

Example - Email import:
```python
def import_email(subject, body, sender):
    # Save to DB
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO notes (content, author, source, title) VALUES (?, ?, ?, ?)",
              (body, sender, 'email', subject))
    
    # Index
    index_in_qmd(...)
```

### Adding New Output Formats

- Export to Obsidian
- Generate website
- Create PDF summaries

---

## Security & Privacy

- **Local only**: Everything stays on your drive
- **No cloud**: Whisper runs locally
- **Your data**: Not sent anywhere

## Future Enhancements

- [ ] Web interface
- [ ] Multi-user support
- [ ] Real-time transcription
- [ ] Auto-tagging with AI
- [ ] Citation linking
- [ ] Export to Obsidian/Notion
