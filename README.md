# TextPrism - Visual Lexicon for Expressive Text

**"Turn any text into a premium, icon-rich visual explanation - with server-side high-fidelity PDF export."**

TextPrism is a Visual Mapping Engine that transforms dense text into rich, iconographically annotated documents. It pairs a massive 90,000+ asset Visual Lexicon (1.3 GB of offline icons, clipart, and illustrations) with LLM-generated ASCII art to produce stunning visual explanations.

---

## Features

- Server-Side PDF Generation - Built on Playwright, generating pixel-perfect multi-page PDFs with layout preservation and robust text-clipping protection.
- LLM-Driven Artistic Freedom - Prompt any LLM to use the "shape-it ascii art style". It handles structure, boxes, and flows.
- Granular Sentence-Level Mapping - Every sentence is paired with a vibrant icon via the Vibrancy Ranking Engine.
- Universal Tag Stripping - Automatically cleans up semantic tags like [keyword] from all output text, titles, and bullets for a professional look.
- 90k+ Offline Asset Lexicon - OpenMoji, OpenClipArt, Lucide, Heroicons, Noto Emoji, and 15+ more icon libraries - all local, all offline.
- Universal AI Compatibility - Works with web LLMs (ChatGPT/Gemini/Claude), local models (Ollama), or Gemini API.
- Comprehensive Verification Suite - Strict test runner ensuring stability across rendering and export pipelines.

---

## Quick Start

### 1. Setup Environment
```bash
# Clone and Setup
git clone https://github.com/Muhammad-Rabieh/TextPrism.git
cd TextPrism

# Create and Activate Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Install Dependencies using local pip module
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# Setup PDF high-fidelity engine (Required for PDF Export)
python3 -m playwright install chromium
```

### 2. Launch the Server
```bash
# Recommended: If venv is activated
python3 src/app.py

# Alternatively: Run directly using the venv path
./venv/bin/python3 src/app.py

# Open http://localhost:8000
```

### 3. Running Tests
```bash
# Run the Master Verification Suite
python3 tests/run_all_tests.py
```

---

## Architecture and Reorganized Structure

TextPrism uses a clean, categorized directory structure to maintain scalability:

- src/: Core application logic (app.py, emoji_engine.py, shape_it.py, utils.py).
- data/: The 1.3 GB Visual Lexicon (icons, clipart, indexes).
- docs/: System documentation, roadmap, and implementation plans.
- tests/: Extensive test suite and verification artifacts.
- static/: Frontend assets (Vibrant theme CSS, logic JS).
- templates/: Jinja2 templates for UI and document rendering.
- scripts/: Internal utility scripts for lexicon maintenance.

---

## Core Components

| Component | File | Purpose | Lines |
|------|---------|-------|-------|
| Rendering Engine | src/app.py | FastAPI backend - routes, AI integration, rendering logic. | ~1000 |
| Lexicon Engine | src/emoji_engine.py | Visual Lexicon Engine - 4-layer lookup for 90k assets. | ~500 |
| ASCII Engine | src/shape_it.py | SHAPE_IT ASCII art engine - 16+ programmatic shape functions. | ~630 |
| Utility Layer | src/utils.py | Shared utilities like normalize_ascii(). | ~40 |

---

## Visual Lexicon (90,000+ Assets)

The Lexicon is ranked by Vibrancy, prioritizing multi-colored, highly detailed assets over simple icons.

| Library | Format | Count | Primary Use |
|-------|--------|-------|------|
| OpenMoji | PNG 72x72 | 4,292 | General concepts/emojis |
| Heroicons | SVG | 324 | Clean UI elements |
| OpenClipArt | SVG | ~26,000 | Rich illustrations |
| Lucide/Noto | SVG | ~9,000 | Functional iconography |
| Misc Modules | SVG/PNG | ~50,000+ | Deep niche keyword coverage |

---

## AI Workflow (Multi-Tier)

1. Manual AI (Default): Use our "Magic Prompt" workflow with any web-based LLM.
2. Free API: Built-in support for Gemini 1.5 Flash (Tier 2).
3. Local AI: Full support for Ollama (Mistral/Llama3) for total privacy.
4. Premium API: Works with GPT-4, Claude 3.5, etc.

---

## License

Released under the GPL v3 License.
