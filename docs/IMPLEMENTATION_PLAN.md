# TextPrism - Integration Plan

> Last updated: 2026-03-07

## Project Vision

"Empowering LLMs with the visual palettes and style guides to create expressive explanations."

TextPrism is a Visual Mapping Engine that enables LLMs to transform dense text into rich, visual summaries. TextPrism provides the Essential Tools: a massive 1.3 GB Visual Lexicon and a rendering engine that produces premium visual documents.

---

## Core Methodology

### Layer 1: Iconographic Annotation
- Every key concept gets paired with a high-quality icon from the 90k+ asset library.
- The Vibrancy Ranking Engine scores candidate icons (OpenClipArt=100, OpenMoji=90, Lucide=85, Heroicons=10).

### Layer 2: Visual Lexicon
- Reusable, offline systematic assets. Key indexes located in data/.

### Layer 3: Semantic Icon Mapping (AI or Heuristic)
- Granular keywords assigned to every sentence.
- Universal cleaning logic strips [keyword] tags from all output text fields.

### Layer 4: SHAPE_IT ASCII Structural Art
- LLM handles artistic design of boxes and flows.
- TextPrism provides normalize_ascii() for pixel-perfect alignment.

### Layer 5: Server-Side PDF Export (Playwright)
- High-Fidelity Rendering: Uses headless Chromium to generate pixel-perfect PDFs.
- Paint-Box Expansion: Employs CSS padding tricks to prevent Chromium from clipping font descenders.
- Layout Integrity: Standard block layouts in PDF overrides ensure maximum stability over buggy Flexbox print engines.

---

## Project Structure (Reorganized)

```
TextPrism/
|-- app.py                    # Main FastAPI server
|-- emoji_engine.py           # Lexicon and Ranking Engine
|-- shape_it.py               # ASCII structural engine
|-- utils.py                  # Shared utilities
|
|-- data/                     # Substantial 1.3 GB asset library
|-- docs/                     # Project documentation and plans
|-- examples/                 # Sample HTML tutorials and results
|-- scripts/                  # Internal maintenance scripts
|-- static/                   # CSS/JS frontend assets
|-- templates/                # Jinja2 layouts
|-- tests/                    # Comprehensive verification suite
|
|-- README.md                 # Primary documentation
|-- requirements.txt          # Dependencies (including playwright)
+-- .env.example              # Configuration template
```

---

## Key Components

### 1. emoji_engine.py - Vibrancy Ranking Engine
Prioritizes colorful, high-entropy assets. Uses exact, partial, category, and semantic remapping lookups.

### 2. app.py - PDF and Render Logic
Handles the heavy lifting of parsing AI outputs, stripping tags, and orchestrating the Playwright PDF generation pipeline.

---

## Dependencies

- Playwright (Chromium): For server-side high-fidelity PDF export.
- FastAPI / Uvicorn: Backend framework.
- PyFiglet / Jinja2: Drawing and templating.
- PyMuPDF (fitz): (Testing only) For verifying PDF geometric integrity.
