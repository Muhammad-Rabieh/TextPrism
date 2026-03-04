# 💎 TextPrism — Implementation Plan

> Last updated: 2026-02-27

## 🎯 Project Vision

**"Empowering LLMs with the visual palettes and style guides to create expressive explanations."**

TextPrism is a **Visual Mapping Engine** that enables LLMs to transform dense text into rich, visual summaries. The LLM acts as the **Artist** — it handles all structure, ASCII art, and layout. TextPrism provides the **Essential Tools**: a massive 1.3 GB Visual Lexicon and a rendering engine that produces premium visual documents.

- 🗺️ **Granular Sentence-Level Mapping**: Every thought is paired with a specific, vibrant visual asset.
- 🎨 **LLM-Driven Artistic Freedom**: LLM designs all boxes, flows, and hierarchy using the "shape-it ASCII art style."
- 📥 **Export-Ready**: Premium Visual Documents from raw text or structured JSON.
- 🧪 **Offline Testable**: Test scripts generate full visual documents without any API key.

---

## 🧠 Core Methodology

### Layer 1: Iconographic Annotation

> *Assigning a small, simple visual (icon, emoji, SVG) to a concept, word, or object.*
> *Enhances readability, memory retention, and comprehension.*

**How we do it:**
- Every key concept gets paired with a **high-quality icon** from the 90k+ asset library
- The **Vibrancy Ranking Engine** scores all candidate icons and picks the most colorful, relevant match
- Priority order: OpenClipArt (score 100) → OpenMoji (score 90) → Lucide/3D (score 85) → Heroicons (score 10)

### Layer 2: Visual Lexicon (Reusable Vocabulary)

> *A systematic set of visuals/icons representing a vocabulary of terms or concepts.*

**How we do it:**
- `emoji_index.json` — Maps 4,292 OpenMoji icons to English keywords
- `heroicon_index.json` — Maps 324 Heroicons to category keywords
- `clipart_index.json` — Maps 85,000+ clipart assets across 20 modules
- The lexicon is **reusable** across any document and continuously expandable

### Layer 3: Semantic Icon Mapping (AI or Heuristic)

> *Mapping text labels to semantically meaningful images automatically.*

**How we do it:**
- **With API**: Gemini 1.5 Flash or Ollama extracts concepts and selects keywords
- **Without API**: Heuristic keyword mapping with semantic remapping (e.g., "safety" → "shield", "efficiency" → "rocket")
- **Granular**: Keywords are assigned to *every sentence*, not just section titles

### Layer 4: SHAPE_IT ASCII Structural Art

> *Programmatic generation of shapes using ASCII/Unicode characters for visual structure.*

**How we do it:**
- The LLM generates all ASCII art (boxes, flowcharts, hierarchies, separators)
- TextPrism normalizes the art with `normalize_ascii()`:
  - Tab expansion, common indent removal, uniform line padding
  - Literal `\n` un-escaping for LLM JSON compatibility
- CSS tuned for pixel-perfect rendering: `line-height: 1.0`, `letter-spacing: -0.2px`

### Layer 5: PDF Export & Layout Integrity

> *Generating high-fidelity, multi-page documents that preserve web styling.*

**How we do it:**
- **html2pdf.js Integration**: Captures the DOM as a high-resolution canvas before converting to PDF.
- **Break Avoidance**: `page-break-inside: avoid` ensures ASCII charts and icon grids are never split across pages.
- **Selective Rendering**: PDF controls are stripped from standalone HTML exports for a cleaner user experience.

### Layer 6: Continuous Verification

> *Ensuring 100% stability across visual and programmatic pipelines.*

**How we do it:**
- **Master Runner**: `tests/run_all_tests.py` executes 14+ specialized test scripts.
- **Mocked AI Flows**: Playwright tests simulate AI responses to verify frontend rendering and export buttons.
- **PDF Structure Analysis**: `pypdf` is used to programmatically verify page counts and content continuity.

---

## 📦 Available Assets (Offline)

| Asset | Location | Format | Count | Size |
|-------|----------|--------|-------|------|
| OpenMoji (color) | `data/icons/openmoji/` | PNG 72×72 | 4,292 | ~30 MB |
| Heroicons | `data/icons/heroicons/` | SVG 24×24 | 324 | ~2 MB |
| OpenClipArt (Debian) | `data/clipart/module_1/` | SVG | ~26,000 | ~24 MB |
| Lucide Icons | `data/clipart/module_2/` | SVG | ~5,300 | ~43 MB |
| Google Noto Emoji | `data/clipart/module_3/` | SVG | ~3,500 | ~150 MB |
| UN OCHA | `data/clipart/module_4/` | SVG | ~700 | ~4 MB |
| Open Doodles | `data/clipart/module_5/` | SVG | ~50 | ~5 MB |
| Humaaans | `data/clipart/module_6/` | SVG | ~30 | ~15 MB |
| Handy Arrows | `data/clipart/module_7/` | SVG | ~40 | ~2 MB |
| Ira Design | `data/clipart/module_8/` | SVG | ~100 | ~10 MB |
| Fluent Emoji | `data/clipart/module_9/` | SVG | ~7,500 | ~80 MB |
| 3D Icons | `data/clipart/module_10/` | PNG | ~1,440 | ~50 MB |
| + Modules 11-20 | `data/clipart/module_11-20/` | SVG/PNG | ~10,000+ | ~200 MB |
| **Total** | | | **~90,000+** | **~1.3 GB** |

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    TextPrism Rendering Pipeline                 │
│                                                                │
│  ┌──────────┐    ┌────────────────────┐    ┌────────────────┐  │
│  │  INPUT   │───►│  Two-Phase Prompt  │───►│  RENDER ENGINE │  │
│  │  (text)  │    │  1. Distill        │    │  • Vibrancy    │  │
│  └──────────┘    │  2. Map to JSON    │    │    Ranking     │  │
│                  └────────────────────┘    │  • ASCII Norm  │  │
│                           │                │  • Template    │  │
│                           ▼                └───────┬────────┘  │
│                  ┌────────────────┐                │           │
│                  │ VISUAL LEXICON │                ▼           │
│                  │ 90k+ assets   │        ┌──────────────┐    │
│                  │ 3 JSON indexes│        │   OUTPUT     │    │
│                  └────────────────┘        │   HTML with: │    │
│                                           │  • Icons     │    │
│                                           │  • ASCII art │    │
│                                           │  • Sentences │    │
│                                           └──────────────┘    │
└────────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
TextPrism/
│
├── app.py                    # FastAPI backend (718 lines)
├── emoji_engine.py           # Vibrancy Ranking Engine (407 lines)
├── shape_it.py               # SHAPE_IT ASCII engine (635 lines)
├── utils.py                  # Shared utilities (normalize_ascii)
│
├── templates/
│   ├── index.html            # Frontend UI (Magic Prompt workflow)
│   └── explanation.html      # Output template (sentence grid + icons)
│
├── static/
│   ├── style.css             # Vibrant Slate & Cobalt theme
│   └── script.js             # Frontend logic
│
├── data/
│   ├── icons/
│   │   ├── openmoji/         # 4,292 OpenMoji PNGs
│   │   └── heroicons/        # 324 Heroicon SVGs
│   ├── clipart/
│   │   ├── module_1/         # OpenClipArt (~26k SVGs)
│   │   ├── module_2/         # Lucide (~5.3k SVGs)
│   │   └── module_3-20/      # 17 more icon packs
│   ├── emoji_index.json      # OpenMoji keyword map
│   ├── heroicon_index.json   # Heroicon keyword map
│   └── clipart_index.json    # Unified clipart map (6.3 MB)
│
├── scripts/
│   ├── build_index.py        # Build all JSON indexes
│   ├── download_clipart.py   # Batch download modules
│   ├── optimize_images.py    # PNG/SVG compression
│   └── flatten_clipart.py    # Flatten nested dirs
│
├── tests/
│   ├── sample_docs/          # Test documents
│   ├── test_ai_render.py     # AI render test
│   └── test_clipart_size.py  # Size estimation
│
├── test_cpp_templates.py     # ⭐ C++ tutorial offline test
├── test_render.py            # Generic standalone render test
│
├── README.md                 # Project documentation
├── IMPLEMENTATION_PLAN.md    # This file
├── PROGRESS.md               # Progress tracker
├── requirements.txt          # Python dependencies
├── .env.example              # API key template
└── .gitignore                # Git exclusions
```

---

## 🔧 Key Components

### 1. `emoji_engine.py` — Vibrancy Ranking Engine

The core of icon selection. Given any word, it finds the **most colorful and relevant** icon from the 90k+ asset library.

**Vibrancy Scoring (0-100+):**

| Source | Base Score | Why |
|--------|-----------|-----|
| OpenClipArt (module_1) | 100 | Multi-color, high-entropy SVGs |
| OpenMoji | 90 | Consistently vibrant emoji PNGs |
| Lucide / 3D | 85 | Clean colored SVGs |
| Doodle | 65 | Sketchy but characterful |
| Heroicons | 10 | Monochrome outlines (last resort) |

**Semantic Remapping** (for abstract terms):
```python
"safety"     → ["shield_color", "security", "safe_box"]
"foundation" → ["pillar", "construction", "bricks"]
"efficiency" → ["rocket", "speed", "bolt"]
"power"      → ["lightning", "energy", "power_color"]
"vibrant"    → ["rainbow", "sparkles", "paint"]
```

**Lookup Strategy (in order):**
1. **Exact match** — Word exists directly in the lexicon
2. **Partial match** — Word is a substring of a lexicon entry
3. **Category fallback** — Word belongs to a known category
4. **Semantic remapping** — Abstract term mapped to concrete visual
5. **Default** — Generic fallback icon

### 2. `utils.py` — ASCII Normalization

Extracted from `app.py` for testability. The `normalize_ascii()` function ensures pixel-perfect ASCII art:

```python
def normalize_ascii(text):
    # 1. Un-escape literal '\n' from LLM JSON output
    # 2. Expand tabs to 4 spaces
    # 3. Trim leading/trailing empty lines
    # 4. Remove common indentation (dedent)
    # 5. Pad all lines to uniform length (fixes broken box borders)
```

### 3. `app.py` — FastAPI Backend

**API Endpoints:**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Serve main UI |
| POST | `/explain` | Text → visual HTML (direct) |
| POST | `/render-magic` | JSON → visual HTML (from Magic Prompt) |
| GET | `/magic-prompt/distill` | Phase 1 prompt generator |
| GET | `/magic-prompt/map` | Phase 2 prompt generator |
| POST | `/shape-it` | Generate ASCII art |
| GET | `/lookup/{word}` | Look up a word in the lexicon |
| POST | `/lookup-many` | Look up multiple words |
| GET | `/lexicon` | Visual Lexicon stats |
| POST | `/export/markdown` | Generate Markdown export |

### 4. `shape_it.py` — SHAPE_IT ASCII Engine

16+ programmatic shape functions:

| Function | Output |
|----------|--------|
| `draw_box(text, style)` | Bordered box (single/double/rounded) |
| `draw_titled_box(title, text)` | Box with title header |
| `draw_flowchart(steps)` | Horizontal flow with arrows |
| `draw_vertical_flow(steps)` | Vertical flow with arrows |
| `draw_pyramid(levels)` | Hierarchy pyramid |
| `draw_diamond(height)` | Diamond shape |
| `draw_triangle(height)` | Triangle shape |
| `draw_separator(text)` | Section divider |
| `draw_banner(text, font)` | Large pyfiglet banner |
| `draw_callout(text)` | Speech/thought bubble |
| `draw_table(headers, rows)` | ASCII table |
| `draw_arrow(direction)` | Directional arrow |
| `draw_hierarchy(items)` | Tree hierarchy |

---

## 🤖 AI Strategy (Multi-Tier)

### Tier 1: Manual AI (Default & Free)
- **Method**: Two-phase copy-paste prompts to any web LLM (ChatGPT/Gemini/Claude).
- **Phase 1 (Distill)**: Raw text → structured sections with ASCII art.
- **Phase 2 (Map)**: Structured text → Visual Lexicon JSON with per-sentence keywords.
- **Pros**: 100% free, uses the smartest public models.

### Tier 2: Free API Keys
- **Method**: Gemini 1.5 Flash via API for automatic mapping.
- **Setup**: Add `GEMINI_API_KEY` to `.env`.
- **Pros**: Automated, no copy-pasting.

### Tier 3: Local AI (Ollama)
- **Method**: Connects to locally running Ollama (Mistral, Llama3, etc.).
- **Pros**: 100% private, offline, no costs.

### Tier 4: Paid APIs
- **Method**: GPT-4, Claude 3.5 Sonnet, etc.
- **Pros**: Maximum reliability and speed.

---

## 📋 Dependencies

```
fastapi          # Web framework
uvicorn          # ASGI server
pyfiglet         # Text banner generation
python-multipart # Form data support
jinja2           # HTML templating
aiofiles         # Async file serving
python-dotenv    # Environment variables
```

**Optional:**
```
google-generativeai  # Gemini API (Tier 2)
requests             # Ollama HTTP client (Tier 3)
```

---

## 📚 Terminology Reference

| Term | Definition |
|------|-----------|
| **Iconographic Annotation** | Pairing icons/emojis with text to enhance readability |
| **Visual Lexicon** | A reusable 90k+ library of concept → icon mappings |
| **Semantic Icon Mapping** | AI/LLM automatically selecting icons based on text meaning |
| **Vibrancy Ranking** | Scoring system that prioritizes colorful, high-quality icons |
| **Granular Mapping** | Assigning a keyword to every individual sentence |
| **SHAPE_IT ASCII** | Generating shapes (boxes, arrows, pyramids) with ASCII/Unicode |
| **normalize_ascii()** | Function that cleans and pads ASCII art for perfect rendering |
| **Magic Prompt** | Two-phase prompt system for manual AI workflow |
| **OpenMoji** | Open-source emoji set (72×72 color PNGs, 4,292 icons) |
| **Heroicons** | Clean outline SVG icons by Tailwind Labs (24×24, 324 icons) |
| **OpenClipArt** | Debian's 26,000+ public domain SVG clipart collection |

---

## 🚀 Implementation Phases

### Phase 1: Foundation ✅
- [x] Collect OpenMoji + Heroicons assets
- [x] Build Visual Lexicon JSON indexes
- [x] Create SHAPE_IT ASCII engine
- [x] Create Visual Lexicon lookup engine

### Phase 2: Backend ✅
- [x] FastAPI server with all endpoints
- [x] Static file serving for all asset types
- [x] Jinja2 HTML template for visual output

### Phase 3: Frontend ✅
- [x] Magic Prompt workflow UI
- [x] Vibrant CSS theme
- [x] Frontend logic & download support

### Phase 4: Integration & Polish ✅
- [x] End-to-end testing with diverse documents
- [x] Markdown export
- [x] LLM API integration (Gemini + Ollama)

### Phase 5: Multi-Tier AI ✅
- [x] Two-stage manual workflow (Distill + Map)
- [x] Ollama local LLM support
- [x] AI tier selection UI

### Phase 6: Clipart Expansion ✅
- [x] 20-module clipart plan (~585 MB)
- [x] Batch download, index, and optimization
- [x] 90,000+ total local assets

### Phase 7: Granular Mapping & Visual Polish ✅
- [x] Sentence-level keyword extraction
- [x] Vibrancy Ranking Engine
- [x] ASCII normalization with normalize_ascii()
- [x] CSS tuning for solid ASCII borders
- [x] Vibrant color theme

### Phase 8: Offline Testing & Modularization ✅
- [x] Extract utils.py (decoupled from app.py)
- [x] C++ Templates tutorial test (test_cpp_templates.py)
- [x] Generic render test (test_render.py)
- [x] Zero API key required for tests

### Phase 9: Future ⏳
- [ ] Migrate `google.generativeai` to `google.genai`
- [ ] PDF export
- [ ] Dark mode toggle in explanation output
- [ ] Live preview in Magic Prompt workflow
