# Research Report: Latest Tech Topics - March 2026

**Date:** 2026-03-14  
**Agent:** Researcher (subagent)

---

## Summary

This report covers trending topics from Hacker News and tech news sources as of March 2026, including local AI running capabilities, supply chain issues, and emerging security technologies.

---

## Findings

### 1. Running AI Locally - canirun.ai

A popular resource (990 points on HN) that helps users determine which AI models their hardware can run locally.

**Key Insights:**
- **Memory Requirements Range Widely:**
  - Tiny models (0.5-1GB): TinyLlama 1.1B, Qwen 3.5 0.8B, Gemma 3 1B - run on almost any device
  - Small models (1-4GB): Llama 3.2 3B, Qwen 3 4B, Gemma 3 4B - laptop-friendly
  - Medium models (4-16GB): Llama 3.1 8B, Qwen 3 32B, DeepSeek R1 Distill 32B - gaming GPU territory
  - Large models (16-64GB): Llama 3.3 70B, Llama 4 Scout 109B - high-end GPU required
  - Massive models (64GB+): DeepSeek R1 671B, DeepSeek V3.2 685B, Kimi K2 1T - multi-GPU clusters

- **Best Models by Category:**
  - **Reasoning:** DeepSeek R1 series, Phi-4, GPT-OSS
  - **Coding:** Qwen 2.5 Coder, Devstral 2 (72.2% SWE-bench), GPT-OSS
  - **Multimodal:** Llama 3.2 Vision, Gemma 3, Qwen 3.5, Mistral Small 3.1
  - **General Purpose:** Llama 3.3 70B, Qwen 3 32B, Gemma 2 9B

- **Key Trend:** 1-bit LLMs (like Microsoft's BitNet) enable running 70B parameter models on consumer hardware - 10-100x memory reduction

**Resource:** [canirun.ai](https://www.canirun.ai/)

---

### 2. Qatar Helium Shutdown - Chip Supply Crisis

**Key Insights:**
- Qatar (supplying ~30% of global helium) has shut down operations
- Chip manufacturers now on a "two-week clock" for helium supplies
- SK hynix forced to diversify suppliers urgently
- Helium is critical for semiconductor manufacturing (cooling, chip fabrication)
- This follows ongoing supply chain vulnerabilities highlighted in previous research

**Impact:**
- Potential GPU production delays
- Memory chip manufacturing at risk
- Could affect AI hardware availability and pricing

---

### 3. Negative Light Technology - Invisible Data Transfer

Researchers at UNSW Sydney and Monash University developed an innovative security technology.

**How It Works:**
- Uses "negative luminescence" - makes signals blend into background thermal radiation
- Looks like no data is being sent to thermal cameras
- Only receivers with proper equipment can detect the hidden message
- Data rates achieved: ~100 KB/s in lab (potential for GB/s with improvements)

**Applications:**
- Defense communications
- Financial sector security
- Any scenario where even the existence of communication should be hidden

**Why It Matters:**
- Traditional encryption protects data content, but interceptors know communication is happening
- This method makes communication invisible entirely
- Described as "like a flashlight that can somehow go darker than 'off'" for infrared light

**Paper:** Published in Nature's Light: Science & Applications

---

### 4. TUI Studio - Visual Terminal UI Design

A Figma-like visual editor for terminal applications (570 points on HN).

**Features:**
- Drag-and-drop visual canvas with real-time ANSI preview
- 20+ built-in components (Box, Button, Table, Tree, Tabs, Modal, etc.)
- Multiple layout engines: Absolute, Flexbox, Grid
- 8 color themes: Dracula, Nord, Solarized, Monokai, etc.
- Export to 6 frameworks: Ink, BubbleTea, Blessed, Textual, OpenTUI, Tview

**Status:** Alpha (code export not yet functional)

**Platform Support:** Apple Silicon (M1-M4), Windows, Linux

---

### 5. Other Notable Topics from HN

- **xAI Turmoil:** Elon Musk pushing out more xAI founders as AI coding effort struggles
- **MacBook Neo:** Can run Windows in a virtual machine (Parallels confirmation)
- **Algolia Security:** Researcher found 39 exposed Admin Keys across open source documentation sites
- **Hammerspoon:** Open source alternative to Logitech mouse software (228 points)
- **Channel Surfer:** YouTube app like cable TV (428 points)

---

## Recommendations

1. **For Local AI:** Start with Qwen 3.5 or Llama 3.2 small models if limited hardware; DeepSeek R1 Distill offers excellent reasoning at reasonable resource requirements

2. **For Supply Chain Monitoring:** Helium shortage could impact GPU prices - consider hardware purchases soon if needed

3. **For Security:** Negative luminescence technology represents paradigm shift in covert communications - worth watching for commercial applications

4. **For TUI Development:** TUI Studio could significantly speed up terminal app development once export功能 is ready

---

## Sources
- https://www.canirun.ai/
- https://www.tomshardware.com/tech-industry/qatar-helium-shutdown-puts-chip-supply-chain-on-a-two-week-clock
- https://www.unsw.edu.au/newsroom/news/2026/03/New-negative-light-technology-hides-data-transfers-in-plain-sight
- https://tui.studio/
- https://news.ycombinator.com/

---

*Report saved to: /media/tony/Drive2/Programs/reports/*
