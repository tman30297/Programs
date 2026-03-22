# Local AI Models for GTX 1060 (6GB VRAM) - 2026

## Overview
This guide helps determine which AI models can run on a GTX 1060 with 6GB VRAM.

## Recommended Models by VRAM Tier

### 0.5GB - 2GB (Very Low-end)
- **Qwen 3.5 0.8B** - 0.5GB - Ultra-tiny for edge devices
- **Llama 3.2 1B** - 0.5GB - Meta's smallest Llama
- **Gemma 3 1B** - 0.5GB - Google's on-device model
- **TinyLlama 1.1B** - 0.6GB - Lightweight for constrained devices
- **DeepSeek R1 1.5B** - 0.8GB - Tiny reasoning model
- **Qwen 2.5 Coder 1.5B** - 0.8GB - Coding-focused
- **Qwen 3 1.7B** - 0.9GB - Compact multilingual
- **Llama 3.2 3B** - 1.5GB - Lightweight for mobile
- **Phi-3.5 Mini** - 1.9GB - Microsoft's efficient model

### 2GB - 4GB (Low-end GPU - GTX 1060 3GB variant)
- **Qwen 2.5 7B** - 3.6GB - Strong multilingual/coding
- **Mistral 7B v0.3** - 3.6GB - High-quality with sliding window
- **DeepSeek R1 Distill 7B** - 3.6GB - Reasoning model

### 4GB - 6GB (Mid-range - GTX 1060 6GB ideal)
- **Llama 3.1 8B** - 4.1GB - Meta's versatile 8B (recommended starting point)
- **Qwen 3.5 9B** - 4.6GB - Multimodal
- **Gemma 2 9B** - 4.6GB - Google's best mid-size
- **Nemotron Nano 9B v2** - 4.6GB - NVIDIA's hybrid Mamba2
- **Llama 3.2 11B Vision** - 5.6GB - Multimodal vision+text

### 7GB+ (Requires more VRAM - Not ideal for GTX 1060)
- **Phi-4 14B** - 7.2GB - Microsoft's reasoning model
- **Qwen 2.5 14B** - 7.2GB - Excellent quality
- **Mistral Small 3.1 24B** - 12.3GB - Multimodal with vision
- **Gemma 3 27B** - 13.8GB - Google's flagship

## Recommended Setup for GTX 1060

### Tools
- **Ollama** - Easiest for beginners
- **LM Studio** - GUI for model management
- **llama.cpp** - Command-line, most flexible

### Best Choice for GTX 1060
1. **Qwen 2.5 7B** or **Mistral 7B** - Best quality/speed ratio
2. **Llama 3.1 8B** - If you need larger context (128K)
3. **DeepSeek R1 Distill 7B** - For reasoning tasks

### Installation (Ollama)
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull mistral
ollama pull llama3.2:7b
ollama pull qwen2.5:7b

# Run interactively
ollama run mistral
```

## Key Insights
- **Quantization** can reduce VRAM needs by 50-75%
- **Qwen 2.5** series offers best quality for size
- **DeepSeek R1** provides excellent reasoning capabilities
- For coding: **Qwen 2.5 Coder 7B** or **DeepSeek R1 Distill 7B**

## Resource
- [canirun.ai](https://www.canirun.ai) - Check compatibility for your specific GPU

---
*Generated: 2026-03-14*
*Workspace: ~/.openclaw/workspace-research*
