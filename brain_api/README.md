# Brain API Server

REST API for the Brain AI System - provides HTTP access to Brain functionality for external applications, scripts, and integrations.

## Features

- **Notes**: List, get, add, edit notes
- **Search**: Search notes, hybrid search, multi-source search
- **Chat**: Ask questions to Brain (RAG)
- **YouTube**: Import and transcribe videos
- **PDF**: Search and import PDFs
- **Stats**: Get Brain statistics
- **Export**: Export all Brain data as JSON
- **Graph**: Access knowledge graph data

## Quick Start

```bash
# Install dependencies
cd /media/tony/Drive2/Programs/brain_api
pip install -r requirements.txt

# Run the server
python3 server.py

# Or use the launcher
chmod +x run.sh
./run.sh
```

The server starts on `http://0.0.0.0:8081` by default.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info and endpoints |
| GET | `/health` | Health check |
| GET | `/notes` | List notes |
| POST | `/notes` | Add a new note |
| GET | `/notes/{id}` | Get a specific note |
| GET | `/search?query=...` | Search notes |
| GET | `/hybrid?query=...` | Hybrid search |
| GET | `/multi?query=...` | Multi-source search |
| POST | `/chat` | Ask a question |
| POST | `/youtube` | Import YouTube video |
| GET | `/pdf/search?query=...` | Search PDFs |
| GET | `/stats` | Get Brain statistics |
| GET | `/random` | Get random note |
| GET | `/export` | Export all data |
| GET | `/graph` | Get knowledge graph |
| GET | `/summarize/{id}` | Summarize a note |
| GET | `/flashcard/{id}` | Generate flashcards |

## Example Usage

### Python Client

```python
import requests

BASE = "http://localhost:8081"

# Search notes
results = requests.get(f"{BASE}/search", params={"query": "Python"}).json()

# Ask a question
response = requests.post(f"{BASE}/chat", json={"prompt": "What do I know about ESP32?"}).json()

# Get stats
stats = requests.get(f"{BASE}/stats").json()

# Add a note
requests.post(f"{BASE}/notes", json={"content": "New note content", "tags": "python,ai"})
```

### cURL

```bash
# Search
curl "http://localhost:8081/search?query=python"

# Chat
curl -X POST http://localhost:8081/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is my knowledge on Rust?"}'

# Stats
curl http://localhost:8081/stats

# Get random note
curl http://localhost:8081/random
```

### JavaScript

```javascript
const BASE = "http://localhost:8081";

// Search
const results = await fetch(`${BASE}/search?query=python`).then(r => r.json());

// Chat
const response = await fetch(`${BASE}/chat`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({prompt: "What do I know about AI?"})
}).then(r => r.json());
```

## Configuration

Edit `server.py` or use command-line arguments:

```bash
python3 server.py --help
```

Options:
- `--host HOST` - Host to bind to (default: 0.0.0.0)
- `--port PORT` - Port to bind to (default: 8081)
- `--debug` - Enable debug mode
- `--framework [fastapi|flask|auto]` - Web framework

## Running in Background

```bash
# Using systemd (create a service file)
# Or using nohup
nohup python3 server.py > api.log 2>&1 &

# Or using screen/tmux
screen -S brain-api
python3 server.py
# Ctrl+A D to detach
```

## Framework

The server automatically detects FastAPI (preferred) and falls back to Flask if not available.

- **FastAPI**: Automatic docs at `/docs`, better performance
- Flask: Simpler, no extra dependencies

Install FastAPI for the full experience:
```bash
pip install fastapi uvicorn
```