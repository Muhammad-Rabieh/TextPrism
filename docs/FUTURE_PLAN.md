# TextPrism - Future Plan & Roadmap

This document outlines planned improvements to the TextPrism architecture to enhance maintainability, readability, and performance.

## 🏗️ Architectural Refactor: Modularization

The current monolithic structure (large files like `app.py`) will be decomposed into smaller, specialized modules. This will make the codebase easier to navigate for both human developers and AI assistants.

### 1. Backend Decomposition (`src/app.py`)
- **`src/server.py`**: FastAPI application setup, middleware, and exception handlers.
- **`src/routes/`**: Directory containing route handlers grouped by feature (e.g., `magic_prompt.py`, `render.py`, `export.py`).
- **`src/engines/parsing.py`**: Logic for extracting JSON, ASCII blocks, and rich tags from LLM responses.
- **`src/engines/export.py`**: PDF (Playwright), Markdown (ZIP), and HTML export orchestration.

### 2. Asset Engine Refactor (`src/emoji_engine.py`)
- **`src/engines/lexicon_search.py`**: Core fuzzy search and keyword association logic.
- **`src/engines/lexicon_ranking.py`**: Vibrancy ranking and asset prioritization.
- **`src/engines/asset_loader.py`**: Index loading and file system management for JSON indexes.

### 3. Drawing System Refactor (`src/shape_it.py`)
- **`src/drawing/boxes.py`**: Titled boxes, borders, and callouts.
- **`src/drawing/diagrams.py`**: Flowcharts, pyramids, and structural diagrams.
- **`src/drawing/banners.py`**: Section separators and decorative banners.

## 🚀 Feature Roadmap

- **Enhanced ASCII Precision**: Integration of specialized character-sets for higher-density diagrams.
- **Client-Side Mermaid Customization**: Allow users to toggle Mermaid themes (Dark/Forest/Neutral) before export.
- **Asynchronous Processing Queue**: For very large documents, offload export tasks to background workers with progress tracking.
- **API Versioning**: Transition to `/v1/` prefixed routes for future-proofing.

## ✨ Explanation Style Variety

We aim to expand beyond the default "Visual Hybrid" style to offer customized output formats based on user preference or content type.

| Style | Description | Sub-Types |
| :--- | :--- | :--- |
| **📖 Narrative** | Storytelling-driven flow | Prose, Snapshots, Scene Text |
| **🖼️ Visual** | Pure graphical emphasis | ASCII Art, Unicode Art, Emoji Scenes |
| **🎬 Frame-Based** | Sequential panels/storyboards | Panels, Comic Strips, Play Scripts |
| **🔁 Interactive** | Hybrid maps and choices | Text + Map, Path Stories, Adventures |
| **❓ Q&A Style** | Dialogue and exploration | FAQ, Socratic Method, Interview Style |

### Conceptual Diagram
```text
  🎨 EXPRESSIVE TEXT
                           │
 ┌───────────────┬───────────────┬───────────────┬───────────────┐
 │               │               │               │               │
📖 Narrative     🖼️ Visual       🎬 Frame-Based   🔁 Interactive  ❓ Q&A Style
Storytelling     Illustration    / Panels        / Hybrid        (Dialogue)
 │               │               │               │               │
 │               │               │               │               │
 ├─ Prose        ├─ ASCII Art    ├─ Storyboards  ├─ Text + Map   ├─ FAQ Format
 ├─ Snapshots    ├─ Unicode Art  ├─ Comic Strip  ├─ Path Stories ├─ Socratic Method
 └─ Scene Text   └─ Emoji Scene  └─ Play Script  └─ Adventure    └─ Interview Style
```

---
*Last Updated: 2026-03-08T18:36:00*
