# Voice Assistant with Wake Word Detection

AI voice assistant that listens for wake words and responds using Ollama.

## Features

- **Wake Word Detection** - Listens for "Hey Bob" activation
- **Speech Recognition** - Converts speech to text
- **AI Responses** - Uses Ollama (qwen3:latest) for natural responses
- **Text-to-Speech** - Speaks responses back to you

## Installation

```bash
# Install dependencies
pip install pvporcupine pyaudio SpeechRecognition pyttsx3 numpy

# Optional: For better TTS
pip install pyttsx3
```

## Porcupine Wake Word (Recommended)

Get a free access key at https://console.picovoice.com/

```bash
export PORCUPINE_ACCESS_KEY="your_key_here"
python voice_assistant.py
```

## Fallback Mode

If no Porcupine key, works with basic voice activation.

## Usage

```bash
python voice_assistant.py
```

- Say "Hey Bob" to activate
- Speak your command
- Say "stop" to exit

## Commands

- "hello" / "hi" - Greeting
- "stop" / "exit" - Quit assistant
- Any other command - AI processes it

## Requirements

- Python 3.8+
- Microphone
- Ollama with qwen3 model (optional, for AI responses)
- Porcupine access key (optional, for accurate wake word)
