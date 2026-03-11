# TextPrism — Strict Implementation Plan
## Feature A: Explanation Style Variety  |  Feature B: Arabic Language Support

> **For LLM Implementers:** Follow every step exactly and in order. Run the test for each step before proceeding.
> Last Updated: 2026-03-11

---

## 📐 Architecture Overview (READ FIRST)

```
TextPrism/
├── src/
│   ├── app.py                  ← Backend: prompts, routes, parser, export
│   └── emoji_engine.py         ← Icon lookup (no changes needed)
├── templates/
│   ├── index.html              ← UI: input panel, style/language selectors
│   └── explanation.html        ← Output: section rendering, RTL support
├── static/
│   ├── script.js               ← Frontend JS: reads selectors, passes to API
│   └── style.css               ← CSS: RTL classes, style-specific layout
└── tests/
    ├── test_hybrid.py          ← Core parser test (always run this)
    └── test_style_arabic.py    ← [NEW] Tests for these features (create in Phase A.4)
```

**Key Data Flow:**
```
User selects Style + Language
  → JS reads values
  → POST /magic-prompt/unified with {text, chart_format, style, language}
  → app.py builds style-specific prompt
  → LLM returns Hybrid format
  → User pastes response
  → POST /render-magic
  → parse_hybrid_to_visual_data() → visual_data dict
  → explanation.html renders with RTL/style classes
```

---

---

# FEATURE A: Explanation Style Variety

**Goal:** Allow the user to choose an explanation style before generating the prompt.  
**Styles:** `visual` (default) | `narrative` | `frame` | `qa`

---

## Phase A.1 — Backend: Add `style` param to the magic prompt endpoint

**File:** `src/app.py`  
**Function:** `get_magic_prompt_unified` (starts at ~line 192)

### Step A.1.1 — Read `style` from request body

Find the line: `chart_format = data.get("chart_format", "ascii")`  
Add **immediately after** it:
```python
style = data.get("style", "visual")   # visual | narrative | frame | qa
```

### Step A.1.2 — Build the style-specific prompt rules block

Add this block **after** the `chart_rules` block is built (after the `else:` block, before building `prompt`):

```python
style_rules = ""
if style == "narrative":
    style_rules = """
STYLE: NARRATIVE (Storytelling-Driven)
- Write the explanation as a flowing story. Use first-person or third-person narrative voice.
- Each idea section should feel like a chapter with a beginning, middle, and end.
- Use vivid transitions between sentences: "This leads to...", "As a result...", "The story unfolds with..."
- Bullets should read as story facts, not technical specs.
"""
elif style == "frame":
    style_rules = """
STYLE: FRAME-BASED (Sequential Panels)
- Structure each idea section as a PANEL or SCENE in a sequence.
- Title each section as a panel header: "[icon] Panel 1: The Setup", "[icon] Panel 2: The Conflict", etc.
- Each sentence is a caption for that panel. Keep sentences short and punchy (max 20 words each).
- Bullets are scene notes or stage directions.
"""
elif style == "qa":
    style_rules = """
STYLE: Q&A (Socratic Dialogue)
- For every idea, start the section title as a Question: "[icon] What is X?", "[icon] Why does Y matter?"
- Answer the question across 3-5 sentences in a direct, conversational tone.
- Each bullet is a follow-up "Did you know?" fact.
- Use "You" to address the reader directly.
"""
else:  # default: visual
    style_rules = """
STYLE: VISUAL (Default — Icon-Annotated Explanation)
- Write clear, informative explanations for each idea.
- Every sentence starts with a [keyword] tag for icon mapping.
- Bullets are concise supporting details.
"""
```

### Step A.1.3 — Inject `style_rules` into the prompt string

Find the line in the `prompt` f-string:
```
RULES FOR THE EXPLANATION:
```
Add `{style_rules}` as the **first line** inside the rules block:
```python
RULES FOR THE EXPLANATION:
{style_rules}
1. Identify every distinct **idea or concept**...
```

### ✅ Test A.1
```bash
cd "/home/muhammad/Desktop/expressive text/TextPrism"
./venv/bin/python3 -c "
import sys; sys.path.insert(0, 'src')
import asyncio
from fastapi.testclient import TestClient
from app import app
client = TestClient(app)

for style in ['visual', 'narrative', 'frame', 'qa']:
    r = client.post('/magic-prompt/unified', json={'text': 'The sun is a star.', 'chart_format': 'ascii', 'style': style})
    assert r.status_code == 200, f'Style {style} returned {r.status_code}'
    prompt = r.json()['prompt']
    if style == 'narrative': assert 'NARRATIVE' in prompt
    if style == 'frame': assert 'FRAME-BASED' in prompt
    if style == 'qa': assert 'Q&A' in prompt
    print(f'✅ Style [{style}] prompt OK')
"
```
**Pass criteria:** All 4 styles return 200 and contain their style keyword in the prompt.

---

## Phase A.2 — Frontend: Add a Style Selector to `index.html`

**File:** `templates/index.html`

### Step A.2.1 — Add the style selector control

Find this block (around line 67–82):
```html
<div class="chart-format-selector" id="chart-format-selector">
```
**Immediately BEFORE it**, insert:
```html
<!-- Style Selector -->
<div class="chart-format-selector" id="style-selector" style="margin-right: 8px;">
    <div class="format-option active" data-value="visual" title="Visual (Default)">
        <img src="/icons/heroicons/photo.svg" alt="Visual" class="format-icon">
        <span>Visual</span>
    </div>
    <div class="format-option" data-value="narrative" title="Narrative Storytelling">
        <img src="/icons/heroicons/book-open.svg" alt="Narrative" class="format-icon">
        <span>Story</span>
    </div>
    <div class="format-option" data-value="frame" title="Frame/Panel Based">
        <img src="/icons/heroicons/squares-2x2.svg" alt="Frame" class="format-icon">
        <span>Frame</span>
    </div>
    <div class="format-option" data-value="qa" title="Q&amp;A Style">
        <img src="/icons/heroicons/chat-bubble-left-right.svg" alt="Q&A" class="format-icon">
        <span>Q&amp;A</span>
    </div>
</div>
```

### ✅ Test A.2

Open `http://localhost:8000` in the browser. Verify that 4 style buttons appear to the left of the chart format selector. All buttons should be styled consistently. Click each one — the active state should toggle.

---

## Phase A.3 — Frontend: Wire style into the JS prompt request

**File:** `static/script.js`

### Step A.3.1 — Capture selected style

Find the code that reads `chart_format` before the `/magic-prompt/unified` API call. It will look like:
```javascript
const chartFormat = document.querySelector('#chart-format-selector .format-option.active')?.dataset.value || 'ascii';
```
**Immediately after** that line, add:
```javascript
const explanationStyle = document.querySelector('#style-selector .format-option.active')?.dataset.value || 'visual';
```

### Step A.3.2 — Pass `style` in the API request body

Find the `fetch('/magic-prompt/unified', ...)` call.  
In the `body` JSON, add `"style": explanationStyle`:
```javascript
body: JSON.stringify({
    text: inputText,
    chart_format: chartFormat,
    style: explanationStyle      // ← ADD THIS LINE
})
```

### Step A.3.3 — Wire style selector click events (same pattern as chart format)

Find the code block that handles click events for `#chart-format-selector .format-option`.  
Just below that block, add:
```javascript
document.querySelectorAll('#style-selector .format-option').forEach(opt => {
    opt.addEventListener('click', () => {
        document.querySelectorAll('#style-selector .format-option').forEach(o => o.classList.remove('active'));
        opt.classList.add('active');
    });
});
```

### ✅ Test A.3

1. Start the server: `./venv/bin/python3 src/app.py`
2. Open browser DevTools → Network tab
3. Select "Story" style, paste any text, click "Explain & Map with AI"
4. In the Network tab, find the `/magic-prompt/unified` POST request
5. Check the **Request Payload** — it must contain `"style": "narrative"`

**Pass criteria:** The request payload contains the correct style value.

---

## Phase A.4 — Create the automated test file

**File:** `tests/test_style_arabic.py` (NEW FILE)

Create this test file:
```python
"""
Tests for Explanation Style Variety and Arabic Language Support.
Run with: PYTHONPATH=. ./venv/bin/python3 tests/test_style_arabic.py
"""
import sys
sys.path.insert(0, 'src')
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_all_styles_generate_prompt():
    """Each style must return a 200 with the style keyword in the prompt."""
    for style, keyword in [('visual', 'VISUAL'), ('narrative', 'NARRATIVE'), ('frame', 'FRAME-BASED'), ('qa', 'Q&A')]:
        r = client.post('/magic-prompt/unified', json={'text': 'Test text.', 'chart_format': 'ascii', 'style': style})
        assert r.status_code == 200, f"Style [{style}] failed with {r.status_code}"
        assert keyword in r.json()['prompt'], f"Style keyword [{keyword}] not found for style [{style}]"
    print("✅ test_all_styles_generate_prompt PASSED")

def test_arabic_prompt_contains_language_instructions():
    """Arabic language selection must inject arabic instruction into prompt."""
    r = client.post('/magic-prompt/unified', json={'text': 'Test text.', 'chart_format': 'ascii', 'style': 'visual', 'language': 'arabic'})
    assert r.status_code == 200, f"Arabic request failed: {r.status_code}"
    prompt = r.json()['prompt']
    assert 'Arabic' in prompt or 'العربية' in prompt, "Arabic instruction missing from prompt"
    print("✅ test_arabic_prompt_contains_language_instructions PASSED")

def test_english_is_default():
    """No language param must default to English — prompt must NOT contain Arabic instruction."""
    r = client.post('/magic-prompt/unified', json={'text': 'Test text.', 'chart_format': 'ascii', 'style': 'visual'})
    assert r.status_code == 200
    prompt = r.json()['prompt']
    assert 'العربية' not in prompt, "Arabic instruction appeared in default (English) prompt"
    print("✅ test_english_is_default PASSED")

if __name__ == "__main__":
    test_all_styles_generate_prompt()
    test_arabic_prompt_contains_language_instructions()
    test_english_is_default()
    print("\n🎉 All style + language tests PASSED")
```

### ✅ Run the test (it will fail for Arabic until Feature B is done — that is expected):
```bash
cd "/home/muhammad/Desktop/expressive text/TextPrism"
PYTHONPATH=. ./venv/bin/python3 tests/test_style_arabic.py
```

---

---

# FEATURE B: Arabic Language Support

**Goal:** Allow the user to choose output language: `english` (default) or `arabic`.  
**Rules:** Arabic output uses full RTL layout. English is always the fallback.

---

## Phase B.1 — Backend: Add `language` param to the magic prompt

**File:** `src/app.py`  
**Function:** `get_magic_prompt_unified`

### Step B.1.1 — Read `language` from request body

Find the line added in A.1.1:
```python
style = data.get("style", "visual")
```
**Immediately after** add:
```python
language = data.get("language", "english")  # english | arabic
```

### Step B.1.2 — Build the language rules block

After the `style_rules` block, add:
```python
language_rules = ""
if language == "arabic":
    language_rules = """
LANGUAGE: ARABIC OUTPUT (مخرجات عربية)
- Write the ENTIRE explanation in Modern Standard Arabic (MSM / الفصحى).
- This includes: the document title, all section titles, all sentence content, and all bullet points.
- The JSON `title`, `explanation`, all `content` fields, and all `bullets` MUST be in Arabic.
- Keep [keyword] tags in English (e.g., [rocket], [shield]) because they are used for icon lookup only.
- Do NOT mix Arabic and English sentences. Each sentence must be fully in one language.
- CRITICAL: Write Arabic text right-to-left naturally. Do not add any RTL markers manually.
"""
else:
    language_rules = """
LANGUAGE: ENGLISH OUTPUT (Default)
- Write the entire explanation in clear, professional English.
"""
```

### Step B.1.3 — Inject `language_rules` into the prompt string

In the `prompt` f-string, add `{language_rules}` **before** the JSON schema block:
```
{style_rules}
{language_rules}

REQUIRED JSON STRUCTURE:
```

### ✅ Test B.1
```bash
cd "/home/muhammad/Desktop/expressive text/TextPrism"
PYTHONPATH=. ./venv/bin/python3 tests/test_style_arabic.py
```
**Pass criteria:** `test_arabic_prompt_contains_language_instructions` and `test_english_is_default` both PASS.

---

## Phase B.2 — Pass `language` through to the render pipeline

**File:** `src/app.py`  
**Function:** `render_magic` (around line 723) and `parse_hybrid_to_visual_data`

The visual_data dict returned by `parse_hybrid_to_visual_data` must carry a `language` field so the template can activate RTL mode.

### Step B.2.1 — Pass language from render_magic into visual_data

Find `render_magic`:
```python
async def render_magic(request: Request, data: str = Form(...)):
```

This endpoint receives the raw AI text. We need to also receive `language`:
```python
async def render_magic(request: Request, data: str = Form(...), language: str = Form("english")):
```

Then pass it into the template context:
```python
return templates.TemplateResponse("explanation.html", {
    "request": request,
    ...
    "language": language,          # ← ADD THIS
})
```

### Step B.2.2 — Pass language from the frontend

**File:** `static/script.js`

Find the `fetch('/render-magic', ...)` call. In the `FormData` body, add:
```javascript
formData.append('language', currentLanguage);  // currentLanguage is read from selector
```
Where `currentLanguage` is a variable capturing the active language option (see Phase B.3).

### ✅ Test B.2 (manual)

1. Start the server, open browser
2. Select "Arabic", paste text, get prompt, run through LLM, paste response, click Render
3. Open DevTools → Network → find `/render-magic` POST
4. Verify Request Payload contains `language=arabic`

---

## Phase B.3 — Frontend: Add Language Selector to `index.html`

**File:** `templates/index.html`

### Step B.3.1 — Add language toggle

**Immediately BEFORE** the style selector added in Phase A.2.1, insert:
```html
<!-- Language Selector -->
<div class="chart-format-selector" id="language-selector" style="margin-right: 8px;">
    <div class="format-option active" data-value="english" title="English (Default)">
        <span style="font-size:1.1em;">🇬🇧</span>
        <span>EN</span>
    </div>
    <div class="format-option" data-value="arabic" title="Arabic / عربي">
        <span style="font-size:1.1em;">🇸🇦</span>
        <span>AR</span>
    </div>
</div>
```

### Step B.3.2 — Wire language selector in JS

**File:** `static/script.js`

Add a `currentLanguage` variable at the top of the main script scope:
```javascript
let currentLanguage = 'english';
```

Add click handlers (same pattern as style selector):
```javascript
document.querySelectorAll('#language-selector .format-option').forEach(opt => {
    opt.addEventListener('click', () => {
        document.querySelectorAll('#language-selector .format-option').forEach(o => o.classList.remove('active'));
        opt.classList.add('active');
        currentLanguage = opt.dataset.value;
    });
});
```

Pass `language` in the `/magic-prompt/unified` fetch body:
```javascript
body: JSON.stringify({
    text: inputText,
    chart_format: chartFormat,
    style: explanationStyle,
    language: currentLanguage      // ← ADD THIS
})
```

### ✅ Test B.3 (visual)

1. Open `http://localhost:8000`
2. Verify 🇬🇧 EN and 🇸🇦 AR buttons appear
3. Click AR — the button activates
4. Click EN — switches back

---

## Phase B.4 — Template: RTL Layout for Arabic Output

**File:** `templates/explanation.html`

### Step B.4.1 — Add RTL direction to `<html>` tag

Find line 2:
```html
<html lang="en">
```
Replace with:
```html
<html lang="{{ 'ar' if language == 'arabic' else 'en' }}" dir="{{ 'rtl' if language == 'arabic' else 'ltr' }}">
```

### Step B.4.2 — Add RTL-specific CSS

Inside the `<style>` block, add at the end:
```css
/* RTL Support for Arabic */
[dir="rtl"] body {
    font-family: 'Segoe UI', 'Noto Sans Arabic', 'Tahoma', sans-serif;
    text-align: right;
}

[dir="rtl"] .sentence-item {
    border-left: none;
    border-right: 4px solid var(--accent);
    flex-direction: row-reverse;
}

[dir="rtl"] .sentence-item:hover {
    transform: translateX(-8px);
}

[dir="rtl"] .section-header {
    flex-direction: row-reverse;
}

[dir="rtl"] .bullet-list li {
    border-left: none;
    border-right: 3px solid var(--accent2);
    flex-direction: row-reverse;
}

[dir="rtl"] .summary-icons {
    flex-direction: row-reverse;
}
```

### Step B.4.3 — Load Arabic font for RTL mode

In the `<head>`, find the Google Fonts link. Add `Noto+Sans+Arabic` to the import:
```html
href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;500&family=Noto+Sans+Arabic:wght@400;600;700&display=swap"
```

### ✅ Test B.4 (browser visual test)

1. Start server. Pick "AR" language, paste Arabic text or run a translated LLM output through render
2. Inspect the rendered `<html>` tag — must have `dir="rtl"` and `lang="ar"`
3. Text must flow right-to-left
4. Sentence cards must have their accent border on the RIGHT side (not left)
5. Icons must appear on the RIGHT of text

**Pass criteria:** Entire layout is mirrored. No left-to-right elements visible.

---

## Phase B.5 — Run Full Test Suite

```bash
cd "/home/muhammad/Desktop/expressive text/TextPrism"
# Core test
PYTHONPATH=. ./venv/bin/python3 tests/test_hybrid.py

# New Style + Arabic test
PYTHONPATH=. ./venv/bin/python3 tests/test_style_arabic.py
```

**All tests must print ✅ before the feature is considered complete.**

---

---

# 📋 Implementation Completion Checklist

## Feature A — Style Variety
- [ ] A.1.1: `style = data.get("style", "visual")` added to `get_magic_prompt_unified`
- [ ] A.1.2: `style_rules` block implemented for all 4 styles
- [ ] A.1.3: `{style_rules}` injected into prompt f-string
- [ ] A.2.1: Style selector HTML added to `index.html`
- [ ] A.3.1: `explanationStyle` captured in `script.js`
- [ ] A.3.2: `style` passed in fetch body
- [ ] A.3.3: Style click events wired
- [ ] A.4: `tests/test_style_arabic.py` created and passing

## Feature B — Arabic Language Support
- [ ] B.1.1: `language = data.get("language", "english")` added
- [ ] B.1.2: `language_rules` block implemented
- [ ] B.1.3: `{language_rules}` injected into prompt
- [ ] B.2.1: `language` passed through `render_magic` → template
- [ ] B.2.2: `language` added to `/render-magic` FormData in JS
- [ ] B.3.1: Language selector HTML added to `index.html`
- [ ] B.3.2: Language selector wired in `script.js`
- [ ] B.4.1: `<html dir="rtl">` conditional in `explanation.html`
- [ ] B.4.2: RTL CSS block added
- [ ] B.4.3: Noto Sans Arabic font loaded
- [ ] B.5: All tests passing (`test_hybrid.py` + `test_style_arabic.py`)

---

*TextPrism Implementation Plan — STYLE_ARABIC_PLAN.md*  
*Last Updated: 2026-03-11T16:59:00+02:00*
