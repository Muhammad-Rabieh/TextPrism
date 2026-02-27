# 💎 TextPrism — Visual Lexicon for Expressive Text

**"Turn any text into a premium, icon-rich visual explanation — no LLM required."**

TextPrism is a **Visual Mapping Engine** that transforms dense text into rich, iconographically annotated documents. It pairs a massive **90,000+ asset Visual Lexicon** (1.3 GB of offline icons, clipart, and illustrations) with LLM-generated ASCII art to produce stunning visual explanations.

---

## ✨ Features

- 🎭 **LLM-Driven Artistic Freedom** — Prompt any LLM to use the **"shape-it ascii art style"**. It handles structure, boxes, and flows. TextPrism provides the premium visual assets.
- 🗺️ **Granular Sentence-Level Mapping** — Every sentence is paired with a vibrant, semantically relevant icon via the **Vibrancy Ranking Engine**.
- 📚 **90k+ Offline Asset Lexicon** — OpenMoji, OpenClipArt, Lucide, Heroicons, Noto Emoji, and 15+ more icon libraries — all local, all offline.
- 🔓 **Universal AI Compatibility** — Works with web LLMs (ChatGPT/Gemini/Claude), local models (Ollama), or API-based mapping (Gemini API).
- 📥 **Export-Ready** — Generates standalone HTML visual documents.
- 🧪 **Offline Testable** — Standalone test scripts generate visual explanations without any API key or network.

---

## 🚀 Quick Start

```bash
# 1. Clone & Setup
git clone https://github.com/yourusername/TextPrism.git
cd TextPrism
python -m venv venv
source venv/bin/activate

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Launch the Server
python app.py
# Open http://localhost:8000
```

### Offline Test (No API Key Needed)

```bash
# Generate a C++ Templates visual tutorial
python test_cpp_templates.py

# Open cpp_templates_tutorial.html in your browser
```

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                  TextPrism Pipeline                            │
│                                                                │
│  1. INPUT: User pastes document text OR uses Magic Prompt      │
│  2. DISTILL: LLM summarizes text into structured sections      │
│  3. MAP: LLM maps concepts into a Hybrid Format (JSON + Text)  │
│  4. RENDER: TextPrism parses JSON rules and attaches raw ASCII │
│     • Vibrancy Ranking Engine scores icon quality              │
│     • ASCII art normalized for pixel-perfect alignment         │
│  5. OUTPUT: Standalone HTML with embedded icons + ASCII art     │
└────────────────────────────────────────────────────────────────┘
```

### Two-Phase Manual Workflow

| Phase | Action | Input | Output |
|-------|--------|-------|--------|
| **Phase 1: Distill** | LLM structures raw text into sections with ASCII art | Raw document text | Structured explanation |
| **Phase 2: Map** | LLM maps structure to visual keywords and raw ASCII art | Phase 1 output | Hybrid format: JSON map + Raw Text ASCII blocks |

---

## 🧠 Core Components

| File | Purpose | Lines |
|------|---------|-------|
| `app.py` | FastAPI backend — routes, AI integration, rendering | 718 |
| `emoji_engine.py` | Visual Lexicon Engine — Vibrancy Ranking, 4-layer lookup | 407 |
| `shape_it.py` | SHAPE_IT ASCII art engine — 16+ shape functions | 635 |
| `utils.py` | Shared utilities — `normalize_ascii()` | 41 |
| `templates/index.html` | Frontend UI — Magic Prompt workflow | — |
| `templates/explanation.html` | Output HTML template — section grid, icons, ASCII | — |
| `static/style.css` | Premium theme — vibrant palette, glassmorphism | — |
| `static/script.js` | Frontend logic — form handling, render flow | — |

### Test & Scripts

| File | Purpose |
|------|---------|
| `test_cpp_templates.py` | Offline C++ Templates tutorial (no API needed) |
| `test_render.py` | Generic standalone render test |
| `scripts/build_index.py` | Build unified Visual Lexicon index |
| `scripts/download_clipart.py` | Batch download 20 clipart modules |
| `scripts/optimize_images.py` | Compress PNG/SVG assets |
| `scripts/flatten_clipart.py` | Flatten nested clipart directories |

---

## 📦 Visual Lexicon (Offline Assets)

| Asset | Location | Format | Count | Size |
|-------|----------|--------|-------|------|
| OpenMoji | `data/icons/openmoji/` | PNG 72×72 | 4,292 | ~30 MB |
| Heroicons | `data/icons/heroicons/` | SVG 24×24 | 324 | ~2 MB |
| OpenClipArt (Debian) | `data/clipart/module_1/` | SVG | ~26,000 | ~24 MB |
| Lucide | `data/clipart/module_2/` | SVG | ~5,300 | ~43 MB |
| Google Noto Emoji | `data/clipart/module_3/` | SVG | ~3,500 | ~150 MB |
| UN OCHA | `data/clipart/module_4/` | SVG | ~700 | ~4 MB |
| + 15 more modules | `data/clipart/module_5-20/` | SVG/PNG | ~50,000+ | ~1 GB |
| **Total** | | | **~90,000+** | **~1.3 GB** |

---

## 🤖 AI Strategy (Multi-Tier)

| Tier | Method | Cost | Setup |
|------|--------|------|-------|
| **1. Manual AI** (Default) | Copy-paste prompts to ChatGPT/Gemini/Claude | Free | None |
| **2. Free API** | Gemini 1.5 Flash via API | Free | Add `GEMINI_API_KEY` to `.env` |
| **3. Local AI** | Ollama (Mistral, Llama3, etc.) | Free | Install Ollama locally |
| **4. Paid API** | GPT-4, Claude 3.5, etc. | Paid | Add respective API keys |

---

## 📋 Prerequisites

- Python 3.10+
- ~2 GB Disk Space (for the full Visual Lexicon)

## ⚖️ License

Released under the **GPL v3** License.
