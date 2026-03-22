# AI Assist

Local AI CLI assistant using Ollama.

## Requirements

- [Ollama](https://ollama.ai) installed and running

## Usage

```bash
# Chat with AI
aiassist.py "How do I reverse a string in Python?"

# Use specific model
aiassist.py "Explain quantum computing" --model phi3

# Stream response
aiassist.py "Write a bash script" --stream

# List available models
aiassist.py --list-models
```

## Features

- Uses Ollama for local AI
- Default model: llama3.2:3b
- Configurable via environment: `OLLAMA_HOST`
- Streaming responses
