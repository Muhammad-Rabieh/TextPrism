# TextPrism Code Map

A quick-reference guide to the components of the TextPrism Visual Mapping Engine.

## 🏗️ Core Architecture

| Component | File | Responsibility |
| :--- | :--- | :--- |
| **Orchestrator** | [app.py](../src/app.py) | FastAPI server, AI orchestration, PDF high-fidelity export. |
| **Lexicon Engine** | [emoji_engine.py](../src/emoji_engine.py) | Keyword association, Vibrancy Ranking, 90k+ asset lookup. |
| **ASCII Engine** | [shape_it.py](../src/shape_it.py) | Programmatic ASCII art drawing (boxes, banners, flows). |
| **Utilities** | [utils.py](../src/utils.py) | String normalization, file system helpers. |

## 📁 Directory Structure

-   `data/`: The Visual Lexicon (1.3 GB). Includes `clipart/`, `icons/`, and `clipart_index.json`.
-   `docs/`: Persistent documentation (`PROGRESS.md`, `WORKFLOW.md`, `CODE_MAP.md`).
-   `static/`: Frontend assets (`style.css`, `script.js`).
-   `templates/`: Jinja2 templates for UI (`index.html`) and documents (`explanation.html`).
-   `tests/`: Verification suite. Includes `test_e2e_exports.py` for full pipeline checks.

## 🛠️ Key Logic Flows

1.  **Input Parsing**: `app.py` -> `parse_hybrid_to_visual_data()`
2.  **Keyword Mapping**: `app.py` -> `EmojiEngine.lookup_many()`
3.  **Drawing**: `shape_it.py` -> programmatic functions called by Rendering engine.
4.  **Export**:
    -   **PDF**: Headless Playwright/Chromium print-to-pdf.
    -   **Markdown**: Server-side string concatenation + ZIP bundling of assets.

---
*Last Updated: 2026-03-08T12:35:00*
