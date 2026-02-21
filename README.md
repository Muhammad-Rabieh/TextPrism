# 📖 Text Explain — Visual Lexicon for Semantic Text Annotation

**"Building a visual lexicon of icons for semantic text annotation."**

Text Explain is a visual annotation tool that transforms dense documents into beautiful, easy-to-understand explanations. It combines **LLM-inspired semantic icon mapping**, a curated **Visual Lexicon** of OpenMoji and Heroicons, and **SHAPE_IT ASCII art** for structural framing.

## ✨ Features

- 🎭 **Iconographic Annotation**: Automatically pairs concepts with visuals.
- 📚 **Visual Lexicon**: Built-in library of 1,000+ keyword-to-icon mappings.
- 🎨 **SHAPE_IT ASCII Engine**: Programmatic generation of 16+ shape types (Gantt, Flowcharts, Boxes).
- 🔓 **Free & Accessible AI**: Support for Manual Copy-Paste flow, Free API Tiers, and Local Ollama.
- 📥 **Export Options**: Download explanations as standalone HTML or Markdown.

## 🤖 AI Strategy (Multi-Tier)

The project supports four ways to use AI, prioritized by accessibility:
1. **Manual AI (Default)**: Free copy-paste prompts for web LLMs (ChatGPT/Gemini).
2. **Free API Keys**: Automatic integration with free tiers like Gemini 1.5 Flash.
3. **Local AI (Ollama)**: 100% private and offline usage via local LLMs.
4. **Paid APIs**: Premium experience with GPT-4 or Claude 3.5 Sonnet.

## 🏗️ Architecture

- **Backend**: FastAPI (Python)
- **Frontend**: Vanilla JS + CSS (Glassmorphism)
- **Visuals**: OpenMoji (4,292 PNGs) + Heroicons (324 SVGs)
- **Structural**: SHAPE_IT ASCII Art Engine

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.8+
- The asset folders `openmoji-72x72-color` and `heroicons_24x24` must be in the project root.

### 2. Installation
```bash
# Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Build the Lexicon
Run the index builder once to create the JSON lookup tables:
```bash
python build_index.py
```

### 4. Run the Application
```bash
python app.py
```
Open [http://localhost:8000](http://localhost:8000) in your browser.

## 🧠 Methodology

1. **Semantic Mapping**: The system extracts key concepts from your text.
2. **Icon Selection**: Concepts are matched against the Visual Lexicon using a 4-layer strategy (Exact → Partial → Category → Fallback).
3. **Structural Framing**: SHAPE_IT ASCII art is used to create visual hierarchy and separators.
4. **Rendering**: The final output combines all layers into a premium document.

---
*Built for the Advanced Agentic Coding project at Google DeepMind.*
