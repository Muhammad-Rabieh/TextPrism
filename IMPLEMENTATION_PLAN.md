# 📖 Text Explain Project — Implementation Plan

## 🎯 Project Vision

**"Building a visual lexicon of icons for semantic text annotation."**

This project transforms dense, hard-to-read documents into beautiful, easy-to-understand
visual explanations by combining three techniques:

| Technique                    | What It Does                                           | Tool Used        |
|------------------------------|--------------------------------------------------------|------------------|
| **Iconographic Annotation**  | Pairs icons/emojis with text concepts                  | OpenMoji + Heroicons |
| **Visual Lexicon Mapping**   | Builds a reusable library of concept → icon pairings   | `emoji_engine.py`   |
| **Semantic Icon Mapping**    | AI/LLM automatically selects icons from text meaning   | LLM (online)        |

Additionally, **SHAPE_IT ASCII Art** provides structural visual elements (borders, flowcharts,
pyramids, separators) that organize and frame the annotated content.

---

## 🧠 Core Methodology

### Layer 1: Iconographic Annotation

> *Assigning a small, simple visual (icon, emoji, SVG) to a concept, word, or object.*
> *Enhances readability, memory retention, and comprehension.*

**How we do it:**
- Every key concept in the document gets paired with an **OpenMoji** emoji (72×72 PNG)
- Every structural element (section type, category) gets a **Heroicon** SVG (24×24)
- Examples: 🪑 Chair, 📖 Book, 🔬 Science, 💡 Idea

### Layer 2: Visual Lexicon (Reusable Vocabulary)

> *A systematic set of visuals/icons representing a vocabulary of terms or concepts.*

**How we do it:**
- `emoji_index.json` — Maps 4,292 OpenMoji icons to English keywords
- `heroicon_index.json` — Maps 324 Heroicons to category keywords
- This vocabulary is **reusable** across any document the system processes
- The lexicon grows as more mappings are added

### Layer 3: Semantic Icon Mapping (AI-Powered)

> *Mapping text labels to semantically meaningful images automatically via LLM.*

**How we do it:**
- The LLM (me) reads the input document
- Extracts key concepts, sections, relationships
- **Automatically selects** the best emoji/icon for each concept from the visual lexicon
- No manual icon selection needed — the AI understands meaning

### Layer 4: SHAPE_IT ASCII Structural Art

> *Programmatic generation of shapes using ASCII/Unicode characters for visual structure.*

**How we do it:**
- Title banners, section separators, bordered boxes frame the content
- Flowchart diagrams show relationships between concepts
- Pyramids/hierarchies show ranked information
- Callout bubbles highlight critical points
- All generated algorithmically, not hand-drawn

---

## 📦 Available Assets (Offline)

| Asset             | Location                        | Format       | Count  | Role                          |
|-------------------|---------------------------------|--------------|--------|-------------------------------|
| OpenMoji (color)  | `openmoji-72x72-color/`         | PNG 72×72    | 4,292  | Iconographic annotation       |
| Heroicons         | `heroicons_24x24/`              | SVG 24×24    | 324    | Structural/category icons     |
| SHAPE_IT ASCII    | Programmatically generated      | Text/Unicode | ∞      | Visual structure & framing    |

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        USER WORKFLOW (AI-POWERED)                          │
│                                                                            │
│  1. INPUT: User pastes document text into the app.                         │
│  2. PROCESSING: Choose AI Strategy (Free, API, or Local).                  │
│  3. SEMANTIC MAPPING:                                                      │
│     • PHASE 1: DISTILL - AI summarizes and structures raw text.             │
│     • PHASE 2: MAP - AI maps distilled text to VISUAL LEXICON.             │
│  4. RENDERING: App generates ICONOGRAPHICALLY ANNOTATED output.            │
│     • Icons (Emojis/SVGs) + SHAPE_IT ASCII art + Formatted text.           │
│  5. OUTPUT: User downloads beautiful HTML/Markdown explanation.             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
                         ┌──────────────────┐
                         │  VISUAL LEXICON   │
                         │  emoji_index.json │
                         │  hero_index.json  │
                         └────────┬─────────┘
                                  │ lookup
                                  ▼
┌──────────┐     ┌───────────────────────────────┐     ┌──────────────┐
│  Input   │────►│  LLM: Semantic Icon Mapping   │────►│   Output     │
│  Text    │     │  • Extract concepts            │     │   HTML with: │
└──────────┘     │  • Select icons per concept    │     │  • Emojis    │
                 │  • Choose SHAPE_IT structures  │     │  • Heroicons │
                 │  • Generate explanation text    │     │  • ASCII art │
                 └───────────────────────────────┘     └──────────────┘
```

---

## 📂 Project Structure

```
text_explain_project/
│
├── 📁 openmoji-72x72-color/          # 4,292 OpenMoji PNG icons (EXISTING)
├── 📁 heroicons_24x24/               # 324 Heroicon SVGs (EXISTING)
│
├── 📁 data/                           # Visual Lexicon (generated once)
│   ├── emoji_index.json              # keyword → OpenMoji filename mapping
│   └── heroicon_index.json           # keyword → Heroicon filename mapping
│
├── 📁 static/                         # Frontend UI
│   ├── index.html                    # Main web UI (paste text input)
│   ├── style.css                     # Premium dark glassmorphism theme
│   └── script.js                     # Frontend logic & rendering
│
├── 📁 templates/                      # Output templates
│   └── explanation.html              # Jinja2 template for visual output
│
├── 📁 output/                         # Generated explanation files
│   └── (generated HTML files go here)
│
├── app.py                             # FastAPI backend server
├── shape_it.py                        # SHAPE_IT ASCII engine
├── emoji_engine.py                    # Visual Lexicon lookup engine
├── build_index.py                     # One-time script: build visual lexicon
├── requirements.txt                   # Python dependencies
├── README.md                          # Project documentation
└── IMPLEMENTATION_PLAN.md             # This file
```

---

## 🔧 Components

### 1. `build_index.py` — Visual Lexicon Builder (Run Once)

**Purpose:** Scan the offline asset folders and create the **visual lexicon** —
JSON lookup tables that map **English keywords** to **icon filenames**.

**OpenMoji Indexing:**
- File names are Unicode codepoints (e.g., `1F600.png` = 😀 grinning face)
- We build a curated mapping of ~500+ common English words to their best emoji match
- Categories: emotions, objects, nature, food, activities, symbols, flags, etc.
- Example: `{ "happy": "1F600.png", "book": "1F4D6.png", "fire": "1F525.png" }`

**Heroicon Indexing:**
- File names are already descriptive (e.g., `light-bulb.svg`, `document-text.svg`)
- We parse filenames into searchable keywords automatically
- Example: `{ "document": "document-text.svg", "light": "light-bulb.svg", "star": "star.svg" }`

**Output:** `data/emoji_index.json` + `data/heroicon_index.json`

---

### 2. `shape_it.py` — SHAPE_IT ASCII Art Engine

**Purpose:** Programmatically generate geometric shapes, visual containers, borders,
flowcharts, and decorative elements using ASCII and Unicode box-drawing characters.

**What SHAPE_IT ASCII means:**
Creating shapes using text characters — both simple ASCII (/, \, *, |, _, -)
and extended Unicode box-drawing characters (┌, ─, ┐, │, └, ┘, ═, ║, ╔, ╗, ╚, ╝).
All shapes are generated **algorithmically**, not hand-drawn.

**Features:**

1.  **Geometric Shapes** — Pyramids, diamonds, triangles
    ```
        *           /\          ┌────────┐
       ***         /  \         │  Title │
      *****       /    \        └────────┘
     *******     /______\
    ```

2.  **Box-Drawing Borders** — Frames around text (single, double, rounded)
    ```
    ╔═══════════════════════════╗       ┌───────────────────────────┐
    ║   Important Concept!      ║       │   Light border style      │
    ╠═══════════════════════════╣       ├───────────────────────────┤
    ║  Explanation goes here    ║       │  Also looks great         │
    ╚═══════════════════════════╝       └───────────────────────────┘
    ```

3.  **Flowchart Diagrams** — Process flows with boxes and arrows
    ```
    ┌──────────┐     ┌──────────┐     ┌──────────┐
    │  Input   │────►│ Process  │────►│  Output  │
    └──────────┘     └──────────┘     └──────────┘
          │                                 │
          └─────────── feedback ────────────┘
    ```

4.  **Decorative Separators** — Section dividers and banners
    ```
    ═══════════════════════════════════════
    ░░░░░ Chapter 1: Introduction ░░░░░░░
    ═══════════════════════════════════════
    ```

5.  **Callout Bubbles** — Thought/speech bubbles for highlights
    ```
       .──────────────────────.
      ( This is a key point!   )
       `──────────────────────'
             \
              ★
    ```

6.  **Text Banners** — Large stylized text (via `pyfiglet`)
    ```
     ____
    / ___|  _   _  _ __ ___   _ __ ___    __ _  _ __ _   _
    \___ \ | | | || '_ ` _ \ | '_ ` _ \  / _` || '__| | | |
     ___) || |_| || | | | | || | | | | || (_| || |  | |_| |
    |____/  \__,_||_| |_| |_||_| |_| |_| \__,_||_|   \__, |
                                                       |___/
    ```

7.  **ASCII Tables** — Bordered data tables
    ```
    ┌──────────┬────────────┬──────────┐
    │  Term    │  Meaning   │  Icon    │
    ├──────────┼────────────┼──────────┤
    │  API     │  Interface │   🔌     │
    │  LLM     │  AI Model  │   🤖     │
    └──────────┴────────────┴──────────┘
    ```

8.  **Hierarchy/Pyramid** — Layered information (top = most important)
    ```
          /\
         /  \
        / #1 \
       /──────\
      / #2     \
     /──────────\
    / #3         \
   /──────────────\
    ```

**API Functions:**
- `draw_box(text, style='double')` — Wrap text in a bordered box
- `draw_pyramid(levels, char='*')` — Generate a pyramid with labels
- `draw_diamond(height, char='*')` — Generate a diamond shape
- `draw_flowchart(steps)` — Generate a horizontal/vertical flowchart
- `draw_separator(text, width, style='double')` — Section dividers with text
- `draw_banner(text, font='slant')` — pyfiglet text banner
- `draw_callout(text)` — Speech/thought bubble around text
- `draw_table(headers, rows)` — ASCII table with borders
- `draw_arrow(direction, length)` — Directional arrows
- `draw_hierarchy(items)` — Pyramid/hierarchy diagram

---

### 3. `emoji_engine.py` — Visual Lexicon Lookup Engine

**Purpose:** Given a word or concept, find the best matching icon from the visual lexicon.
This is the core of **Iconographic Annotation** — pairing concepts with visuals.

**Lookup Strategy (in order):**
1.  **Exact match** — Word exists directly in the lexicon
2.  **Partial match** — Word is a substring of a lexicon entry
3.  **Category match** — Word belongs to a known category (emotion → face emoji)
4.  **Heroicon fallback** — Use a structural Heroicon if no emoji fits
5.  **Default** — Return a generic icon (e.g., ❓ or 📌)

**Returns:** `{ "type": "openmoji"|"heroicon", "filename": "1F600.png", "path": "openmoji-72x72-color/1F600.png" }`

---

### 4. `app.py` — FastAPI Backend

**Purpose:** Web server that orchestrates the entire pipeline.

**API Endpoints:**
| Method | Endpoint                         | Purpose                          |
|--------|----------------------------------|----------------------------------|
| GET    | `/`                              | Serve the main UI                |
| POST   | `/explain`                       | Accept text → return visual HTML |
| GET    | `/openmoji-72x72-color/{name}`   | Serve OpenMoji PNGs              |
| GET    | `/heroicons_24x24/{name}`        | Serve Heroicon SVGs              |
| POST   | `/shape-it`                      | Generate ASCII art for text      |
| GET    | `/lexicon`                       | Return the visual lexicon (JSON) |

---

### 5. Frontend (`static/index.html` + `style.css` + `script.js`)

**Purpose:** Premium dark-themed UI where users paste text and see iconographically
annotated explanations.

**Design:**
- Dark background with glassmorphism cards
- Text input area (paste or type document text)
- "Explain" button → sends text to backend/LLM
- Result area renders: ASCII art + inline emojis + Heroicons + formatted text
- Download as HTML or Markdown
- Responsive layout

---

## 🎨 Output Format — Visual Explanation Structure

The generated explanation HTML combines all three annotation layers:

| # | Element                  | Uses                        | Purpose                                |
|---|--------------------------|-----------------------------|-----------------------------------------|
| 1 | **Title Banner**         | SHAPE_IT (pyfiglet banner)  | Large eye-catching document title       |
| 2 | **Summary Box**          | SHAPE_IT (bordered box) + OpenMoji | Key points with emoji annotations  |
| 3 | **Section Separators**   | SHAPE_IT (decorative lines) | Visual separation between topics        |
| 4 | **Concept Cards**        | OpenMoji + Heroicons        | Each concept gets icon + explanation    |
| 5 | **Key Terms Table**      | SHAPE_IT (ASCII table) + OpenMoji | Glossary with icons per term       |
| 6 | **Process Flows**        | SHAPE_IT (flowchart)        | Relationships and sequences             |
| 7 | **Callout Highlights**   | SHAPE_IT (callout bubble)   | Critical points that stand out          |
| 8 | **Hierarchy Pyramids**   | SHAPE_IT (pyramid)          | Ranked/layered information              |

### Example Output Snippet

```html
<!-- SHAPE_IT: Title Banner -->
<pre class="ascii-banner">
 _____         _     _____           _       _
|_   _|____  _| |_  | ____|_  ___ __|  __ _(_)_ __
  | |/ _ \ \/ / __| |  _| \ \/ / '_ \| / _` | | '_ \
  | |  __/>  <| |_  | |___ >  <| |_) | | (_| | | | | |
  |_|\___/_/\_\\__| |_____/_/\_\ .__/|_|\__,_|_|_| |_|
                                |_|
</pre>

<!-- SHAPE_IT: Summary Box + OpenMoji Annotation -->
<pre class="ascii-box">
╔══════════════════════════════════════════════════════╗
║  📖 This document explains the water cycle.         ║
║  🌧️ Key topics: evaporation, condensation, rain    ║
║  🔬 Level: Beginner-friendly                        ║
╚══════════════════════════════════════════════════════╝
</pre>

<!-- Iconographic Annotation: Concept + Icon Pair -->
<div class="concept-card">
  <img src="/openmoji-72x72-color/2600.png" alt="sun" class="emoji-icon">
  <img src="/heroicons_24x24/light-bulb.svg" alt="concept" class="hero-icon">
  <p><strong>Evaporation</strong>: The sun heats water, turning it into vapor.</p>
</div>

<!-- SHAPE_IT: Flowchart -->
<pre class="ascii-flow">
┌──────────────┐     ┌────────────────┐     ┌──────────────┐
│ ☀️ Evaporation│────►│ ☁️ Condensation│────►│ 🌧️ Rain      │
└──────────────┘     └────────────────┘     └──────────────┘
       ▲                                           │
       └───────────── 🔄 Water Cycle ──────────────┘
</pre>
```

---

## 🚀 Implementation Phases

### Phase 1: Foundation ← START HERE
- [x] Collect OpenMoji assets (4,292 PNGs)
- [x] Collect Heroicons assets (324 SVGs)
- [ ] Create `build_index.py` — build visual lexicon JSON files
- [ ] Create `shape_it.py` — SHAPE_IT ASCII engine with all shape functions
- [ ] Create `emoji_engine.py` — visual lexicon lookup engine
- [ ] Set up virtual environment & install dependencies

### Phase 2: Backend
- [ ] Create `app.py` — FastAPI server
- [ ] Implement `/explain` endpoint (accepts text, returns annotated HTML)
- [ ] Implement static file serving for OpenMoji and Heroicons
- [ ] Create Jinja2 HTML template for visual explanations

### Phase 3: Frontend
- [ ] Design & build `index.html` with glassmorphism theme
- [ ] Implement `style.css` — premium dark design
- [ ] Build `script.js` — text submission, result display, download

### Phase 4: Integration & Polish
- [ ] Connect all components end-to-end
- [ ] Test with various document types (technical, educational, legal)
- [ ] Optimize icon loading & rendering performance
- [ ] Add Markdown export option
- [ ] Expand visual lexicon with more word → icon mappings

### Phase 5: Multi-Tier AI & Multi-Stage Workflow ← IN PROGRESS
- [x] Implement Basic "Magic Prompt" (Manual AI V1)
- [ ] Implement **Two-Stage Manual AI Workflow**:
  - Phase 1 Prompt: Raw Text → Structured Summary
  - Phase 2 Prompt: Structured Summary → Mapping JSON
- [ ] Integrate **Ollama Support** (Local/Offline LLM)
- [ ] Implement **Multi-Tier AI Selection** in UI:
  1. **Tier 1 (Default)**: Manual AI (Free for everyone)
  2. **Tier 2**: Free API Tiers (Gemini, Groq, etc.)
  3. **Tier 3**: Local AI (Ollama)
  4. **Tier 4**: Paid APIs (OpenAI/Claude)
- [x] Enhance SHAPE_IT rendering for AI-generated layouts
- [ ] Add "One-Click PDF" export option

---

## 📝 Usage Flow

2. **Open browser:** `http://localhost:8000`
3. **Paste your document text** into the input area
4. **Click "Explain"** → The system:
   - LLM reads and understands the text (Semantic Icon Mapping)
   - Extracts key concepts, sections, relationships
   - Looks up the Visual Lexicon for matching icons (Iconographic Annotation)
   - Generates SHAPE_IT ASCII structures (boxes, flowcharts, etc.)
   - Renders a beautiful HTML explanation
5. **View inline** or **download** the visual explanation (HTML/Markdown)

---

## 🔑 AI Strategy (Multi-Tier)

The project aims to be **Free & Accessible**. We support four tiers of "Intelligence":

### Tier 1: Manual AI (Default & Free)
*   **Method**: Copy-paste prompts into ChatGPT/Gemini web interfaces.
*   **Workflow**: Two-stage distillation for high accuracy without API costs.
*   **Pros**: 100% free, uses the smartest public models.

### Tier 2: Free API Keys
*   **Method**: Uses free tiers of Gemini or Groq directly via API.
*   **Setup**: Add `GEMINI_API_KEY` to `.env`.
*   **Pros**: Automated, no copy-pasting.

### Tier 3: Local AI (Ollama)
*   **Method**: Connects to a locally running Ollama instance (e.g., Llama3 or Mistral).
*   **Pros**: 100% private, offline, no costs.

### Tier 4: Paid APIs
*   **Method**: High-performance models (GPT-4, Claude 3.5 Sonnet).
*   **Pros**: Maximum reliability and speed.

---

## 📋 Dependencies

```
fastapi          # Web framework
uvicorn          # ASGI server
pyfiglet         # Text banner generation (part of SHAPE_IT engine)
python-multipart # File upload support
jinja2           # HTML templating
aiofiles         # Async file serving
python-dotenv    # Environment variables (for API keys)
```

---

## 📚 Terminology Reference

| Term                         | Definition                                                              |
|------------------------------|-------------------------------------------------------------------------|
| **Iconographic Annotation**  | Pairing icons/emojis with text to enhance readability and comprehension |
| **Visual Lexicon**           | A reusable library of concept → icon mappings                           |
| **Semantic Icon Mapping**    | AI/LLM automatically selecting icons based on text meaning              |
| **SHAPE_IT ASCII**           | Generating shapes (boxes, arrows, pyramids) with ASCII/Unicode chars    |
| **OpenMoji**                 | Open-source emoji set (72×72 color PNGs, 4,292 icons)                   |
| **Heroicons**                | Clean outline SVG icons by Tailwind Labs (24×24, 324 icons)             |

### Phase 6: Visual Clipart Expansion (Open Source Clipart) ← NEW
- [x] **Research Starter Packs**:
    - [x] **OpenClipart 2.5**: 19.8 MB (Verified stable release).
    - [x] **GNOME Adwaita**: 16.3 MB (Clean symbolic clipart).
    - [x] **Tango Project**: ~5-10 MB (Classic open-source clipart).
- [x] **Size Estimation**:
    - [x] Total Estimated: **~45-55 MB** (Well within "Low Size" limits).
- [ ] **Quality Test (Sample Download)**:
    - [ ] Download 5 sample SVGs from each pack to verify "Clipart-only" status.
- [ ] **Library Integration**:
    - [ ] Download complete curated ZIPs.
    - [ ] Update `build_index.py` to index the new clipart libraries.
    - [ ] Update `emoji_engine.py` to prioritize Clipart for educational/structural concepts.
- [ ] **Optimization**:
    - [ ] Batch resize/optimize large PNGs to 128px or lower.
    - [ ] Ensure all assets remain local and offline for Privacy.
