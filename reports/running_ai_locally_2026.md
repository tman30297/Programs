# Running AI Locally - Research Report

*Updated: March 14, 2026*

## Can Your Machine Run AI? 

Great resource: **canirun.ai** - Check what models your GPU can run

## Tony's Hardware
- **GPU:** NVIDIA GTX 1060 (6GB VRAM)
- **Recommendation:** Can run models up to ~7GB VRAM requirement

## Recommended Models for GTX 1060 (6GB)

### Lightweight (< 4GB VRAM)
| Model | Size | Use Case |
|-------|------|----------|
| Qwen 3.5 0.8B | 0.5 GB | Embedded/edge |
| Llama 3.2 1B | 0.5 GB | Edge devices |
| Gemma 3 1B | 0.5 GB | On-device |
| TinyLlama 1.1B | 0.6 GB | Constrained devices |
| Qwen 2.5 Coder 1.5B | 0.8 GB | Lightweight coding |
| DeepSeek R1 1.5B | 0.8 GB | Reasoning |
| Qwen 3 1.7B | 0.9 GB | Compact multilingual |
| Llama 3.2 3B | 1.5 GB | Mobile/edge |

### Mid-Range (4-7GB VRAM)
| Model | Size | Use Case |
|-------|------|----------|
| Qwen 3 4B | 2 GB | General tasks |
| Gemma 3 4B | 2 GB | Multimodal |
| Mistral 7B v0.3 | 3.6 GB | High-quality |
| Qwen 2.5 7B | 3.6 GB | Multilingual/coding |
| Qwen 2.5 Coder 7B | 3.6 GB | Dedicated coding |
| DeepSeek R1 Distill 7B | 3.6 GB | Reasoning |
| Qwen 3 8B | 4.1 GB | With thinking mode |
| Gemma 2 9B | 4.6 GB | Mid-size best quality |
| Phi-3.5 Mini | 1.9 GB | Long context efficient |

## Tools to Run Locally

### Ollama
- Easy model management
- `ollama run qwen2.5:7b`
- Great for beginners

### LM Studio
- GUI for running LLMs
- Model library integration
- Chat UI included

### llama.cpp
- Pure CPU inference possible
- Quantization support (Q4, Q5, Q8)
- Most lightweight option

## Key Insights from Recent Research

1. **Local AI is booming** - Hacker News showed "Can I run AI locally?" as top story with 970 points
2. **Model quality/size trade-off** - Qwen and Llama families offer great options
3. **Quantization** - Use Q4/Q5 quantizations to fit larger models in less VRAM
4. **Coding models** - Devstral 2 (72.2% SWE-bench) and Qwen 2.5 Coder are excellent for coding
5. **Reasoning models** - DeepSeek R1 distilled versions offer reasoning at smaller sizes

## Recommendations for Tony

Given GTX 1060 (6GB):
1. **Daily use:** Qwen 2.5:7b or Llama 3.2:3b
2. **Coding:** Qwen 2.5-coder:7b
3. **Lightweight:** Qwen 3:1.7b or smaller

## Context Windows
- Most models now support 32K-128K context
- Newer models (Nemotron 3 Nano) support up to 1M context
- Llama 4 Maverick supports 1M context but needs ~205GB storage!

---
*Report saved to: /media/tony/Drive2/Programs/reports/*
