# 💎 TextPrism — Visual Lexicon for LLM Explanations

**"Providing the high-fidelity assets for LLMs to build expressive visual documents."**

TextPrism is a mapping engine that enables LLMs to transform dense text into rich, visual explanations. We focus on providing the **Visual Asset Layer**: a massive, localized **Visual Lexicon** (90,000+ icons/clipart) and a rendering engine that perfectly integrates high-resolution graphics into the LLM's freeform ASCII layouts.

## ✨ Features

- 🎭 **LLM-Driven Artistic Freedom**: Simply tell your LLM to use the **"shape-it ascii art style"**. It handles all structure, ASCII art, and layout design, while we provide the "High-Res Ink" to make it pop.
- 🗺️ **Premium Graphic Mapping**: Automatically identifies LLM icon tags and replaces them with high-fidelity local clipart and icons.
- 📚 **90k+ Asset Lexicon**: A comprehensive, searchable library of Illustrations, Emojis, and Icons (1.3GB) that outclasses standard emoji support.
- 🔓 **Universal AI Compatibility**: Designed for a seamless workflow with web-based LLMs (ChatGPT/Gemini), Local models (Ollama), or API-based mapping.
- 📥 **Export-Ready**: Transform raw LLM output into standalone, premium Visual Explanations with a single click.

The core magic of TextPrism is giving any LLM (ChatGPT, Gemini, Claude) a simple command to unleash its artistic mapping capabilities:

> **"explain the following using shape-it ascii art style: [INSERT YOUR TEXT]"**

The LLM then crafts a structured layout using its creative choice of ASCII boxes and flows. When you copy that result into TextPrism, we instantly upgrade every concept into a premium, high-res visual.

## 🤖 AI Strategy (Multi-Tier)

The project supports four ways to use AI, prioritized by accessibility:
1. **Manual AI (Default)**: Free copy-paste prompts for web LLMs (ChatGPT/Gemini).
2. **Free API Keys**: Automatic integration with free tiers like Gemini 1.5 Flash.
3. **Local AI (Ollama)**: 100% private and offline usage via local LLMs.
4. **Paid API**: Professional high-throughput usage.

---

## 🏗️ Technical Architecture

- **Backend**: FastAPI (Python 3.13)
- **Visual Lexicon**: Curated keyword-to-asset mapping system (`emoji_engine.py`)
- **Assets**: 
    - 4,292 OpenMoji (PNG)
    - 324 Heroicons (SVG)
    - 90,000+ Clipart/Illustrations (PNG/SVG)
- **Layouts**: LLM-generated ASCII structure (via `shape-it` style)

## 📥 Prerequisites

- Python 3.10+
- 2GB Disk Space (for the full Visual Lexicon)

## 🚀 Getting Started

```bash
# 1. Clone & Setup
git clone https://github.com/yourusername/TextPrism.git
cd TextPrism
python -m venv venv
source venv/bin/activate

# 2. Install Dependencies
pip install -r requirements.xml

# 3. Launch the Studio
python app.py
```

## ⚖️ License
Released under the MIT License. Built for the open-source community.
