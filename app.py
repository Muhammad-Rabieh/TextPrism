#!/usr/bin/env python3
"""
TextPrism — FastAPI Backend (app.py)
================================================
Web server that orchestrates the visual explanation pipeline:
1. Serves the frontend UI
2. Accepts document text via POST
3. Uses SHAPE_IT + Visual Lexicon to generate annotated HTML
4. Serves OpenMoji PNGs and Heroicon SVGs

Part of TextPrism.
"""

import os
import json
import re
import traceback
import subprocess
from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import requests
import tempfile
import shutil
import zipfile
from pathlib import Path

from shape_it import (
    draw_box, draw_titled_box, draw_pyramid, draw_diamond,
    draw_flowchart, draw_vertical_flow, draw_separator,
    draw_banner, draw_callout, draw_table, draw_arrow,
    draw_hierarchy, draw_triangle, BOX_STYLES
)
from emoji_engine import EmojiEngine
from utils import normalize_ascii

# ─────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────

load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # Removed

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:7b-instruct-q4_K_M")

# if GEMINI_API_KEY: # Removed
#     try: # Removed
#         genai.configure(api_key=GEMINI_API_KEY) # Removed
#         # Using flash for speed/cost effectiveness for mapping tasks # Removed
#         llm_model = genai.GenerativeModel('gemini-1.5-flash') # Removed
#         print("✅ Gemini AI initialized for semantic mapping") # Removed
#     except Exception as e: # Removed
#         print(f"⚠️ Failed to initialize Gemini: {e}") # Removed
#         llm_model = None # Removed
# else: # Removed
#     llm_model = None # Removed
#     print("ℹ️ GEMINI_API_KEY not found. Using heuristic mapping.") # Removed

app = FastAPI(
    title="Text Explain — Visual Lexicon for Semantic Text Annotation",
    description="Explain documents using SHAPE_IT ASCII, OpenMoji, and Heroicons",
    version="1.0.0",
)

# Mount static asset directories
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
app.mount("/icons/openmoji", StaticFiles(directory=os.path.join(BASE_DIR, "data", "icons", "openmoji")), name="openmoji")
app.mount("/icons/heroicons", StaticFiles(directory=os.path.join(BASE_DIR, "data", "icons", "heroicons")), name="heroicons")
app.mount("/clipart", StaticFiles(directory=os.path.join(BASE_DIR, "data", "clipart")), name="clipart")
app.mount("/output", StaticFiles(directory=os.path.join(BASE_DIR, "output")), name="output")

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Initialize the Visual Lexicon Engine
engine = EmojiEngine()


# ─────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main UI page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/explain", response_class=HTMLResponse)
async def explain(request: Request, text: str = Form(...), ai_tier: str = Form("heuristic")):
    """
    Accept document text and return a visual explanation HTML.
    """
    sections = parse_text_into_sections(text)
    visual_sections = []
    for section in sections:
        visual = generate_visual_section(section, ai_tier=ai_tier)
        visual_sections.append(visual)

    title = sections[0].get('title', "Document Explanation") if sections else "Document Explanation"

    summary_text = sections[0].get('content', text[:200]) if sections else text[:200]
    summary_keywords = get_semantic_keywords_ai(summary_text, count=5, tier=ai_tier)
    summary_icons = engine.lookup_many(summary_keywords, embed=True)

    return templates.TemplateResponse("explanation.html", {
        "request": request,
        "title": title,
        "summary_text": summary_text,
        "summary_icons": summary_icons,
        "sections": visual_sections,
        "original_text": text,
    })


@app.post("/shape-it", response_class=JSONResponse)
async def shape_it_api(
    content: str = Form(""),
    shape: str = Form("box"),
    style: str = Form("double"),
    font: str = Form("standard"),
):
    """Generate SHAPE_IT ASCII art for given text."""
    result = ""
    try:
        if shape == "box":
            result = draw_box(content, style=style)
        elif shape == "titled_box":
            parts = content.split("|", 1)
            title = parts[0].strip()
            body = parts[1].strip() if len(parts) > 1 else ""
            result = draw_titled_box(title, body, style=style)
        elif shape == "banner":
            result = draw_banner(content, font=font)
        elif shape == "callout":
            result = draw_callout(content)
        elif shape == "separator":
            result = draw_separator(content, width=50, style=style)
        elif shape == "pyramid":
            try:
                height = int(content)
            except ValueError:
                height = 5
            result = draw_pyramid(height)
        elif shape == "diamond":
            try:
                height = int(content)
            except ValueError:
                height = 7
            result = draw_diamond(height)
        elif shape == "flowchart":
            steps = [s.strip() for s in content.split("→") if s.strip()]
            if not steps:
                steps = [s.strip() for s in content.split(",") if s.strip()]
            result = draw_flowchart(steps)
        elif shape == "vertical_flow":
            steps = [s.strip() for s in content.split("→") if s.strip()]
            if not steps:
                steps = [s.strip() for s in content.split(",") if s.strip()]
            result = draw_vertical_flow(steps)
        elif shape == "table":
            # Format: header1,header2|row1col1,row1col2|row2col1,row2col2
            parts = content.split("|")
            headers = [h.strip() for h in parts[0].split(",")]
            rows = [[c.strip() for c in row.split(",")] for row in parts[1:] if row.strip()]
            result = draw_table(headers, rows)
        elif shape == "hierarchy":
            items = [s.strip() for s in content.split(",") if s.strip()]
            result = draw_hierarchy(items)
        elif shape == "arrow":
            result = draw_arrow(direction='right', length=20, label=content)
        else:
            result = draw_box(content, style=style)
    except Exception as e:
        result = f"Error generating shape: {str(e)}"

    return {"ascii": result, "shape": shape}


@app.post("/magic-prompt/unified", response_class=JSONResponse)
async def get_magic_prompt_unified(request: Request):
    """Unified Phase: Generate a prompt to both structure text and map icons in one go."""
    data = await request.json()
    text = data.get("text", "")
    prompt = fr"""
I want you to act as a Document Architect. Your job is to take the text below and transform it into a vibrant, high-impact **Visual Explanation** in a **Single Phase**. 
**CRITICAL: Your goal is an in-depth EXPLANATION, not a summary. Provide a detailed narrative for each part so the reader truly learns the material.**

I want you to output a **Hybrid Format**: a single JSON object followed by raw text ASCII blocks. 
Crucially, I want you to perform **Granular Semantic Mapping** — identifying a visual keyword for EVERY sentence using an inline tag. 

RULES FOR THE EXPLANATION: 
1. Organize the material into 3-5 key sections. 
2. For each section, provide a short title. 
3. For the content of each section, write 3-5 sentences of **in-depth explanation**. Ensure you cover nuances and details.
4. **STRICT VISUAL PARITY: At the start of EVERY sentence, insert exactly ONE general keyword in square brackets [keyword].** 
5. **GENERAL KEYWORDS: Use high-level English nouns like [rocket], [shield], [engine]. NO implementation details like 'doodle_'.** 
6. **SECTION PARITY: EVERY section title MUST have its own [keyword] tag at the start.** 
7. Separate section details into bullet points. 

RULES FOR THE ASCII ART: 
7. Use your creative judgment to 'draw' a layout for each section using the shape-it ASCII style. 
8. **CRITICAL: DO NOT put the ASCII art inside the JSON.** 
9. Instead, AFTER the JSON block, output each section's ASCII art wrapped in ```text ... ``` code fences. 
10. Separate them by `=== ASCII SECTION X ===` markers. 

REQUIRED JSON STRUCTURE:
```json
{{
  "title": "Main Document Title",
  "explanation": "[vision] Detailed overall explanation starting with a keyword tag.",
  "explanation_keywords": ["keyword1", "keyword2"],
  "sections": [
    {{
      "title": "[keyword] Section Title",
      "content": "[keyword] Detailed sentence providing explanation. [keyword] Further detail expanding on the point.",
      "bullets": ["Technical detail 1", "Technical detail 2"]
    }}
  ]
}}
```

TEXT TO TRANSFORM:
{text[:10000]}
"""
    return {"prompt": prompt.strip()}


@app.post("/magic-prompt/distill", response_class=JSONResponse)
async def get_magic_prompt_distill(request: Request):
    """Legacy Phase 1: Use unified instead."""
    return await get_magic_prompt_unified(request)



@app.post("/magic-prompt", response_class=JSONResponse)
async def magic_prompt_fallback(request: Request):
    """Fallback alias for older frontend versions."""
    return await get_magic_prompt_distill(request)


@app.post("/magic-prompt/map", response_class=JSONResponse)
async def get_magic_prompt_map(request: Request):
    """Phase 2: Generate a prompt to map distilled text to our Visual Lexicon JSON."""
    data = await request.json()
    distilled_text = data.get("distilled_text", "")
    prompt = fr"""
I want you to map the document structure below into a Hybrid Format: a single JSON object followed by raw text ASCII blocks.
**CRITICAL: Your goal is an in-depth EXPLANATION, not a summary. Expand on the ideas to ensure clarity.**

RULES FOR JSON:
1. Provide a comprehensive explanation for each section.
2. For EVERY sentence, insert exactly ONE [keyword] tag at the start.
3. Keep the JSON structure valid and began with ```json ... ``` markers.

RULES FOR ASCII ART:
4. For each section, provided a custom high-quality ASCII art block using the shape-it style.
5. **CRITICAL: DO NOT put the ASCII art inside the JSON.**
6. Instead, AFTER the JSON block, output each section's ASCII art. You MUST wrap EVERY ASCII block in ```text ... ``` code fences.
7. Separate them clearly: `=== ASCII SECTION X ===`.

HYBRID STRUCTURE TO FOLLOW:

```json
{{
  "title": "Document Title",
  "explanation": "[vision] Detailed explanation of the document's core purpose and scope.",
  "explanation_keywords": ["vibrant1", "vibrant2"],
  "sections": [
    {{
      "title": "[keyword] Section Title",
      "sentences": [
        {{
          "text": "The primary insight explained thoroughly.",
          "keyword": "vivid_concept1"
        }},
        {{
          "text": "Detailed supporting sentence that provides necessary depth.",
          "keyword": "depth"
        }}
      ],
      "bullets": ["Technical detail.", "Key nuance."]
    }}
  ]
}}
```

=== ASCII SECTION 1 ===
```text
THE ASCII ART DRAWING FOR THIS SECTION
```

TEXT TO MAP:
{distilled_text[:10000]}
"""
    return {"prompt": prompt.strip()}


def extract_json_balanced(text):
    """
    Finds and extracts the first balanced JSON object { ... } from a string.
    This is highly resilient to conversational text or ASCII art surrounding the JSON.
    """
    start_idx = text.find('{')
    if start_idx == -1:
        return None

    count = 0
    for i in range(start_idx, len(text)):
        if text[i] == '{':
            count += 1
        elif text[i] == '}':
            count -= 1
            if count == 0:
                return text[start_idx:i+1]
    return None

def clean_json_garbage(json_str):
    """Deep cleanup for common LLM JSON mistakes like trailing commas."""
    # Remove trailing commas before closing braces/brackets
    json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
    # Ensure quotes are double for basic JSON
    if "'" in json_str and '"' not in json_str:
        json_str = json_str.replace("'", '"')
    return json_str

def extract_rich_tags(text):
    """
    Extracts [keyword] or [keyword] [shape: something] tags from text.
    Returns (cleaned_text, list_of_keywords, list_of_shapes).
    """
    if not text:
        return "", [], []
    
    # Matches [keyword] followed optionally by [shape: shape_name]
    # Also matches standalone [shape: shape_name] or [keyword]
    pattern = re.compile(r'\[([^\]]+)\]')
    
    keywords = []
    shapes = []
    
    def tag_replacer(match):
        raw_inner = match.group(1).strip()
        if raw_inner.lower().startswith("shape:"):
            shape_val = raw_inner[6:].strip()
            if shape_val:
                shapes.append(shape_val)
            return ""
        else:
            keywords.append(raw_inner)
            return ""

    # Clear out the tags and collect them
    clean_text = pattern.sub(tag_replacer, text).strip()
    # Collapse multiple spaces
    clean_text = re.sub(r'\s+', ' ', clean_text)
    
    return clean_text, keywords, shapes

def extract_inline_tags(text):
    """Legacy wrapper for extract_rich_tags."""
    clean, kws, _ = extract_rich_tags(text)
    return clean, kws

@app.get("/lookup/{word}", response_class=JSONResponse)
async def lookup_word(word: str, prefer: str = "emoji"):
    """Look up a word in the visual lexicon."""
    result = engine.lookup(word, prefer=prefer)
    return result

@app.post("/lookup-many", response_class=JSONResponse)
async def lookup_many(words: str = Form(...)):
    """Look up multiple words (comma-separated)."""
    word_list = [w.strip() for w in words.split(",") if w.strip()]
    results = engine.lookup_many(word_list)
    return {"results": results}

@app.get("/lexicon", response_class=JSONResponse)
async def get_lexicon():
    """Return Visual Lexicon stats."""
    return engine.stats()

def parse_hybrid_to_visual_data(raw_text):
    """
    Parses TextPrism Hybrid format (JSON + ASCII + Tags) into a structured dictionary
    suitable for both HTML and Markdown rendering.
    """
    # 1. Extract JSON block using brace balancing
    json_str = extract_json_balanced(raw_text)
    
    if not json_str:
        # Fallback to markdown code block
        json_match = re.search(r'```json\s*(.*?)\s*```', raw_text, re.DOTALL | re.IGNORECASE)
        if json_match:
            json_str = json_match.group(1)

    if not json_str:
        # NOT a hybrid format, treat as plain text sections
        sections_raw = parse_text_into_sections(raw_text)
        # Convert simple sections to visual sections
        visual_sections = []
        for s in sections_raw:
            # Strip tags for the visual section result
            s_title, s_title_kws = extract_inline_tags(s.get('title', ''))
            s['title'] = s_title # Update to clean title
            v = generate_visual_section(s)
            
            # If no icons were found by heuristic, use the tags!
            if not v['title_icons'] and s_title_kws:
                v['title_icons'] = engine.lookup_many(s_title_kws, embed=True)
            visual_sections.append(v)
            
        first_title_raw = sections_raw[0].get('title', 'Analysis') if sections_raw else "Analysis"
        title, title_kws = extract_inline_tags(first_title_raw)
        
        raw_ext = visual_sections[0]['content'] if visual_sections else raw_text[:300]
        explanation_text, exp_kws = extract_inline_tags(raw_ext)
        if not exp_kws:
            exp_kws = extract_keywords(explanation_text, 3)

        return {
            "title": title,
            "title_icons": engine.lookup_many(title_kws, embed=True) if title_kws else [],
            "explanation_text": explanation_text,
            "explanation_icons": engine.lookup_many(exp_kws, embed=True),
            "sections": visual_sections
        }

    # --- HYBRID JSON CASE ---
    try:
        ai_data = json.loads(clean_json_garbage(json_str))
    except json.JSONDecodeError as first_err:
        print(f"⚠️ Initial JSON Decode Error in parse_hybrid_to_visual_data: {first_err}. Attempting cleanup...")
        try:
            cleaned_str = clean_json_garbage(json_str)
            ai_data = json.loads(cleaned_str)
        except json.JSONDecodeError as second_err:
            print(f"❌ Final JSON Decode Error in parse_hybrid_to_visual_data: {second_err}")
            snippet = json_str[:150] + "..." if len(json_str) > 150 else json_str
            raise ValueError(f"Invalid JSON format. Check for unescaped characters or trailing commas. Snippet: {snippet}")
    
    # Extract ASCII Blocks
    ascii_blocks = {}
    pattern = re.compile(r'(?:=+|-+|#+|\*\*)\s*ASCII (?:SECTION|FOR SENTENCE|FOR CONCEPT)\s+([\d\.]+)\s*(?:=+|-+|#+|\*\*)', flags=re.IGNORECASE)
    parts = pattern.split(raw_text)
    for i in range(1, len(parts) - 1, 2):
        try:
            key = parts[i].strip()
            block = parts[i+1].strip('\r\n')
            block = re.sub(r'^```[\w]*\s*\n', '', block)
            block = re.sub(r'\n```\s*$', '', block)
            ascii_blocks[key] = block
        except Exception: pass
    
    # Process sections
    visual_sections = []
    for idx, section in enumerate(ai_data.get('sections', [])):
        sec_title_raw = section.get('title', '')
        sec_title, sec_title_kws, sec_title_shapes = extract_rich_tags(sec_title_raw)
        
        raw_content = section.get('content', '')
        sec_bullets_raw = section.get('bullets', [])
        
        processed_sentences = []
        all_sec_keywords = []
        
        # New robust sentence splitting that respects tags
        # We split by sentence endings followed by spaces, but don't split tokens like [keyword]
        sentence_splits = re.split(r'(?<=[.!?])\s+', raw_content)
        for s_idx, s_raw in enumerate(sentence_splits):
            s_clean, s_kws, s_shapes = extract_rich_tags(s_raw)
            if not s_clean and not s_kws and not s_shapes: continue
            
            all_sec_keywords.extend(s_kws)
            sent_icon = engine.lookup(s_kws[0], embed=True) if s_kws else None
            sent_shape = s_shapes[0] if s_shapes else "none"
            
            sent_ascii = ""
            ai_key = f"{idx+1}.{s_idx+1}"
            ai_drawn_ascii = ascii_blocks.get(ai_key)
            
            if ai_drawn_ascii:
                sent_ascii = normalize_ascii(ai_drawn_ascii)
            elif sent_shape != 'none':
                # Draw even if s_clean is relatively short
                draw_text = s_clean if s_clean else (s_kws[0] if s_kws else "Concept")
                try:
                    if sent_shape == 'box': sent_ascii = normalize_ascii(draw_box(draw_text, padding=1))
                    elif sent_shape == 'callout': sent_ascii = normalize_ascii(draw_callout(draw_text))
                    elif sent_shape == 'banner': sent_ascii = normalize_ascii(draw_banner(draw_text[:30]))
                    elif sent_shape == 'separator': sent_ascii = normalize_ascii(draw_separator(draw_text))
                except: pass
            
            processed_sentences.append({
                'text': s_clean,
                'icon': sent_icon,
                'shape': sent_shape,
                'ascii': sent_ascii
            })

        reconstructed_content = " ".join([s.get('text', '') for s in processed_sentences]) or raw_content
        sec_key = str(idx + 1)
        raw_ai_ascii = ascii_blocks.get(sec_key, section.get('raw_ascii', ''))
        ascii_box = normalize_ascii(raw_ai_ascii) if raw_ai_ascii else ""

        if not sec_title_kws and sec_title:
            sec_title_kws = extract_keywords(sec_title, 2)
        
        clean_bullets = []
        bullet_icons_list = []
        for b_raw in sec_bullets_raw:
            b_clean, b_kws, _ = extract_rich_tags(b_raw)
            if not b_kws and b_clean: b_kws = extract_keywords(b_clean, 2)
            clean_bullets.append(b_clean)
            bullet_icons_list.append(engine.lookup_many(b_kws, embed=True))

        visual_sections.append({
            'title': sec_title, 'content': reconstructed_content, 'sentences': processed_sentences,
            'bullets': clean_bullets, 'type': 'h2', 'ascii_separator': '', 'ascii_box': ascii_box,
            'ascii_flow': '', 'ascii_callout': '',
            'title_icons': engine.lookup_many(sec_title_kws, embed=True) if sec_title_kws else engine.lookup_many(all_sec_keywords[:2], embed=True),
            'bullet_icons': bullet_icons_list
        })

    # Global mapping
    raw_title = ai_data.get('title', 'AI Analysis')
    title, title_kws, title_shapes = extract_rich_tags(raw_title)
    title_icons = engine.lookup_many(title_kws, embed=True) if title_kws else []
    
    # Title Banner if shape specified
    title_ascii = ""
    if title_shapes and title_shapes[0] == 'banner':
        title_ascii = normalize_ascii(draw_banner(title[:30]))

    raw_explanation = ai_data.get('explanation') or ai_data.get('summary', '')
    explanation_text, exp_kws, exp_shapes = extract_rich_tags(raw_explanation)
    if not exp_kws:
        exp_kws = ai_data.get('explanation_keywords') or ai_data.get('summary_keywords', [])
    if not exp_kws:
        exp_kws = extract_keywords(explanation_text, 5)
    
    explanation_ascii = ""
    if exp_shapes:
        shape = exp_shapes[0]
        try:
            if shape == 'banner': explanation_ascii = normalize_ascii(draw_banner(explanation_text[:30]))
            elif shape == 'box': explanation_ascii = normalize_ascii(draw_box(explanation_text[:100]))
            elif shape == 'callout': explanation_ascii = normalize_ascii(draw_callout(explanation_text[:80]))
        except: pass
        
    return {
        "title": title,
        "title_icons": title_icons,
        "title_ascii": title_ascii,
        "explanation_text": explanation_text,
        "explanation_icons": engine.lookup_many(exp_kws, embed=True),
        "explanation_ascii": explanation_ascii,
        "sections": visual_sections
    }

@app.post("/render-magic", response_class=HTMLResponse)
async def render_magic(request: Request, data: str = Form(...)):
    """Render a visual explanation from AI-generated Hybrid format."""
    try:
        raw_text = data.strip()
        visual_data = parse_hybrid_to_visual_data(raw_text)

        return templates.TemplateResponse("explanation.html", {
            "request": request,
            "title": visual_data["title"],
            "title_icons": visual_data["title_icons"],
            "explanation_text": visual_data["explanation_text"],
            "explanation_icons": visual_data["explanation_icons"],
            "sections": visual_data["sections"],
            "original_text": "Manual AI Input"
        })
    except Exception as e:
        print(f"❌ Render Magic Error: {e}")
        import traceback
        traceback.print_exc()
        return HTMLResponse(content=f"Error rendering visual explanation: {str(e)}", status_code=400)

@app.post("/export-md")
async def export_markdown(background_tasks: BackgroundTasks, text: str = Form(...)):
    """Generate a Markdown version of the visual explanation bundled in a ZIP with assets."""
    temp_dir = tempfile.mkdtemp()
    try:
        visual_data = parse_hybrid_to_visual_data(text.strip())
        md = []
        
        assets_dir = Path(temp_dir) / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        # Helper to handle icons: copy to assets and return relative path
        def process_icon(icon):
            if not icon or icon['type'] == 'none' or not icon.get('path'):
                return None
            
            # Source path on server
            src_path = os.path.join(DATA_DIR, icon['path'])
            if not os.path.exists(src_path):
                return None
            
            # Target path in zip
            ext = os.path.splitext(src_path)[1]
            safe_kw = re.sub(r'[^\w\s-]', '', icon['keyword']).strip().replace(' ', '_')
            target_filename = f"{safe_kw}_{hash(icon['path']) % 10000}{ext}"
            target_path = assets_dir / target_filename
            
            # Copy file
            shutil.copy2(src_path, target_path)
            return f"assets/{target_filename}"

        # 1. Title Section
        icons_prefix = ""
        for icon in visual_data["title_icons"]:
            rel_src = process_icon(icon)
            if rel_src:
                icons_prefix += f'<img src="{rel_src}" alt="{icon["keyword"]}" width="48"> '
                # Fallback for old viewers
                icons_prefix += f'<!-- ![{icon["keyword"]}]({rel_src}) -->'
            elif icon['type'] != 'none':
                icons_prefix += f"[{icon['keyword']}] "
                
        md.append(f"# {icons_prefix}{visual_data['title'] or 'Visual Explanation'}")
        if visual_data.get('title_ascii'):
            md.append("\n```\n" + visual_data['title_ascii'] + "\n```\n")
        elif visual_data['title']:
            md.append("\n```\n" + draw_banner(visual_data['title'][:30]) + "\n```\n")

        # 2. Summary Section
        md.append("## 📋 Summary")
        if visual_data.get('explanation_ascii'):
            md.append("\n```\n" + visual_data['explanation_ascii'] + "\n```\n")
            
        icons_line = ""
        for icon in visual_data["explanation_icons"]:
            rel_src = process_icon(icon)
            if rel_src:
                icons_line += f'<img src="{rel_src}" alt="{icon["keyword"]}" width="32"> '
            
        md.append(visual_data["explanation_text"][:2000]) # Increased length
        if icons_line:
            md.append("\n" + icons_line)
        md.append("\n---\n")

        # 3. Sections — order matches explanation.html template:
        #    ascii_separator → header → ascii_box → sentences → ascii_callout → ascii_flow → bullets
        for visual in visual_data["sections"]:
            # 3a. ascii_separator BEFORE header (decorative divider)
            if visual.get('ascii_separator'):
                md.append("```\n" + visual['ascii_separator'] + "\n```")

            # 3b. Section header
            if visual['title']:
                icons_str = ""
                for icon in visual['title_icons']:
                    rel_src = process_icon(icon)
                    if rel_src:
                        icons_str += f'<img src="{rel_src}" alt="{icon["keyword"]}" width="32"> '
                    elif icon['type'] != 'none':
                        icons_str += f"[{icon['keyword']}] "
                md.append(f"### {icons_str}{visual['title']}")

            # 3c. ascii_box AFTER header (main diagram)
            if visual.get('ascii_box'):
                md.append("```\n" + visual['ascii_box'] + "\n```")

            # 3d. Sentences with granular icon mapping
            if visual.get('sentences'):
                for sent in visual['sentences']:
                    sent_text = sent.get('text', '').strip()
                    
                    icon = sent.get('icon')
                    rel_src = process_icon(icon)
                    
                    if rel_src:
                        md.append(f'<img src="{rel_src}" alt="{icon["keyword"]}" width="24"> {sent_text} <!-- ![{icon["keyword"]}]({rel_src}) -->')
                    elif icon and icon['type'] != 'none':
                        md.append(f"[{icon['keyword']}] {sent_text}")
                    elif sent_text:
                        md.append(sent_text)
                    
                    if sent.get('ascii'):
                        md.append("\n```\n" + sent['ascii'] + "\n```\n")
                    
                    md.append("") # Ensure paragraphs are separated by a blank line
            elif visual['content']:
                md.append(visual['content'])

            # 3e. ascii_callout AFTER sentences
            if visual.get('ascii_callout'):
                md.append("```\n" + visual['ascii_callout'] + "\n```")

            # 3f. ascii_flow AFTER callout (flow diagrams from bullets)
            if visual.get('ascii_flow'):
                md.append("```\n" + visual['ascii_flow'] + "\n```")

            # 3g. Bullets
            if visual['bullets']:
                for i, bullet in enumerate(visual['bullets']):
                    icon_pref = ""
                    if visual['bullet_icons'] and i < len(visual['bullet_icons']):
                        for icon in visual['bullet_icons'][i]:
                            rel_src = process_icon(icon)
                            if rel_src:
                                icon_pref += f'<img src="{rel_src}" alt="{icon["keyword"]}" width="24"> '
                            elif icon['type'] != 'none':
                                icon_pref += f"[{icon['keyword']}] "
                    md.append(f"- {icon_pref}{bullet}")

            md.append("") # Spacer

        md.append("\n---\n*Generated by TextPrism — Visual Lexicon for Semantic Text Annotation*")
        
        # Generate dynamic filename from title
        raw_title = visual_data['title'] or "Visual_Explanation"
        words = [w for w in re.split(r'\W+', raw_title) if w]
        base_name = "_".join(words[:3]) if words else "TextPrism_Export"
        md_filename = f"{base_name}.md"
        
        # Write markdown file
        md_file_path = Path(temp_dir) / md_filename
        with open(md_file_path, "w") as f:
            f.write("\n".join(md))
            
        # Create ZIP
        zip_buffer = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        zip_path = zip_buffer.name
        zip_buffer.close()
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add markdown
            zf.write(md_file_path, md_filename)
            # Add assets
            for root, dirs, files in os.walk(assets_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zf.write(file_path, os.path.join("assets", file))
        
        # Helper to delete file
        def cleanup_zip(path):
            if os.path.exists(path):
                os.remove(path)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        
        background_tasks.add_task(cleanup_zip, zip_path)

        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename="text_prism_export.zip",
            background=None # We'll clean up later
        )

    except Exception as e:
        print(f"❌ Markdown Export Error: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=400)
    finally:
        # Note: shutil.rmtree(temp_dir) should ideally happen after response
        # But for now we'll rely on system temp cleanup or a more complex approach if needed
        pass
def parse_text_into_sections(text):
    """
    Parse input text into logical sections.
    Looks for headers, paragraphs, and bullet points.
    """
    lines = text.strip().split('\n')
    sections = []
    current_section = {'title': '', 'content': '', 'bullets': [], 'type': 'text'}

    for line in lines:
        stripped = line.strip()

        if not stripped:
            # Empty line = section break
            if current_section['title'] or current_section['content'] or current_section['bullets']:
                sections.append(current_section)
                current_section = {'title': '', 'content': '', 'bullets': [], 'type': 'text'}
            continue

        # Check if it's a header (starts with #, is ALL CAPS, or is short + followed by content)
        if stripped.startswith('#'):
            if current_section['title'] or current_section['content']:
                sections.append(current_section)
            level = len(stripped) - len(stripped.lstrip('#'))
            current_section = {
                'title': stripped.lstrip('#').strip(),
                'content': '',
                'bullets': [],
                'type': f'h{min(level, 6)}',
            }
        elif stripped.startswith(('-', '•', '*', '–')) and len(stripped) > 2:
            # Bullet point
            bullet_text = stripped.lstrip('-•*– ').strip()
            current_section['bullets'].append(bullet_text)
        elif stripped.isupper() and len(stripped) < 80:
            # ALL CAPS = likely a header
            if current_section['title'] or current_section['content']:
                sections.append(current_section)
            current_section = {
                'title': stripped.title(),
                'content': '',
                'bullets': [],
                'type': 'h2',
            }
        elif stripped.endswith(':') and len(stripped) < 60:
            # Ends with colon = likely a sub-header
            if current_section['title'] or current_section['content']:
                sections.append(current_section)
            current_section = {
                'title': stripped.rstrip(':'),
                'content': '',
                'bullets': [],
                'type': 'h3',
            }
        else:
            # Regular content
            if current_section['content']:
                current_section['content'] += '\n' + stripped
            else:
                current_section['content'] = stripped

    # Don't forget the last section
    if current_section['title'] or current_section['content'] or current_section['bullets']:
        sections.append(current_section)

    # If no sections were created, make one from the whole text
    if not sections:
        sections = [{'title': 'Document', 'content': text.strip(), 'bullets': [], 'type': 'text'}]

    return sections


def get_semantic_keywords_ai(text, count=5, tier="heuristic"):
    """
    Use selected Strategy to choose the best iconographic keywords.
    """
    if tier == "manual":
        return extract_keywords(text, count)
    
    if tier == "ollama":
        return get_semantic_keywords_ollama(text, count)

    return extract_keywords(text, count)


def get_semantic_keywords_ollama(text, count=5):
    """
    Use local Ollama to choose concepts.
    """
    prompt = f"""
    Analyze the following text and select the {count} most important concept keywords
    that would best describe it visually using simple icons or emojis.

    RULES:
    - Return ONLY a JSON list of strings.
    - Choose keywords that are common objects, actions, or simple concepts.
    - Example: ["study", "computer", "code", "brain"].

    TEXT:
    {text}
    """
    
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        response = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload, timeout=30)
        data = response.json()
        content = data.get("response", "").strip()
        keywords = json.loads(content)
        # handle different JSON formats LLMs might return
        if isinstance(keywords, dict):
            # look for a list in any key
            for val in keywords.values():
                if isinstance(val, list):
                    return val[:count]
        return keywords[:count] if isinstance(keywords, list) else extract_keywords(text, count)
    except Exception as e:
        print(f"⚠️ Ollama mapping error: {e}")
        return extract_keywords(text, count)


def extract_keywords(text, max_keywords=10):
    """
    Extract meaningful keywords from text for icon matching.
    Simple approach: filter out common stop words and short words.
    """
    stop_words = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'shall', 'can', 'need', 'must',
        'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as',
        'into', 'through', 'during', 'before', 'after', 'above', 'below',
        'and', 'but', 'or', 'nor', 'not', 'so', 'yet', 'both', 'either',
        'neither', 'each', 'every', 'all', 'any', 'few', 'more', 'most',
        'other', 'some', 'such', 'than', 'too', 'very', 'just', 'also',
        'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them',
        'their', 'we', 'us', 'our', 'you', 'your', 'he', 'she', 'him',
        'her', 'his', 'i', 'my', 'me', 'what', 'which', 'who', 'whom',
        'when', 'where', 'why', 'how', 'if', 'then', 'else', 'about',
        'up', 'out', 'off', 'over', 'under', 'again', 'further',
    }

    import re
    words = re.findall(r'[a-zA-Z]+', text.lower())
    keywords = []
    seen = set()

    for word in words:
        if word not in stop_words and len(word) >= 3 and word not in seen:
            keywords.append(word)
            seen.add(word)
            if len(keywords) >= max_keywords:
                break

    return keywords


def generate_visual_section(section, ai_tier="heuristic"):
    """
    Generate visual elements for a section.
    Returns a dict with ASCII art and icon data.
    """
    visual = {
        'title': section.get('title', ''),
        'content': section.get('content', ''),
        'bullets': section.get('bullets', []),
        'type': section.get('type', 'text'),
        'ascii_separator': '',
        'ascii_box': '',
        'ascii_flow': '',
        'ascii_callout': '',
        'title_icons': [],
        'content_icons': [],
        'bullet_icons': [],
        'sentences': section.get('sentences', []), # Use existing if present (hybrid case)
    }
    
    # Heuristic sentence splitting for granular mapping in simple text
    if not visual['sentences'] and visual['content']:
        import re
        sents = re.split(r'(?<=[.!?])\s+', visual['content'])
        processed_sents = []
        for s in sents:
            if not s.strip(): continue
            # Basic keyword extraction for each sentence
            kw = extract_keywords(s, 1)
            icon = engine.lookup(kw[0], embed=True) if kw else None
            processed_sents.append({
                'text': s,
                'icon': icon,
                'shape': 'none',
                'ascii': ''
            })
        visual['sentences'] = processed_sents

    # Generate separator for headers
    if visual['title']:
        visual['ascii_separator'] = draw_separator(visual['title'], width=55)

        # Look up icons for the title
        title_keywords = get_semantic_keywords_ai(visual['title'], count=3, tier=ai_tier)
        visual['title_icons'] = engine.lookup_many(title_keywords, embed=True)

    # Generate a titled box showing the section content
    if visual['content']:
        visual['ascii_box'] = draw_titled_box(visual['title'] or 'Section', visual['content'][:120], style='double', padding=1)
        
        # If content is very short, add a callout
        if len(visual['content']) < 80:
            visual['ascii_callout'] = draw_callout(visual['content'])

        content_keywords = get_semantic_keywords_ai(visual['content'], count=5, tier=ai_tier)
        visual['content_icons'] = engine.lookup_many(content_keywords, embed=True)

    # Generate a flowchart from bullets if there are 2+
    if len(visual['bullets']) >= 2:
        visual['ascii_flow'] = draw_flowchart(visual['bullets'][:5], style='single')

    # Generate icons for bullets
    for bullet in visual['bullets']:
        bullet_keywords = get_semantic_keywords_ai(bullet, count=2, tier=ai_tier)
        icons = engine.lookup_many(bullet_keywords, embed=True)
        visual['bullet_icons'].append(icons)

    return visual


# ─────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────

def kill_process_on_port(port):
    """Attempt to clear the port using fuser -k."""
    try:
        # fuser -k <port>/tcp sends SIGKILL to processes using the port
        cmd = f"fuser -k {port}/tcp"
        subprocess.run(cmd, shell=True, check=False, capture_output=True)
        print(f"🔄 Port {port} cleared (if occupied).")
    except Exception as e:
        print(f"⚠️  Could not clear port {port}: {e}")

@app.post("/export-pdf")
async def export_pdf(request: Request):
    """
    Server-side PDF generation using Playwright's Chrome print engine.
    This properly respects CSS page-break-inside: avoid rules, unlike
    html2pdf.js which rasterizes via html2canvas and blindly slices.
    """
    try:
        data = await request.json()
        html_content = data.get("html", "")
        if not html_content:
            return JSONResponse({"error": "No HTML content provided"}, status_code=400)

        # Import playwright (async version for FastAPI)
        from playwright.async_api import async_playwright

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            page = await browser.new_page()

            # DEBUG LISTENERS
            page.on("console", lambda msg: print(f"🖥️ Playwright Console: {msg.text}"))
            page.on("requestfailed", lambda req: print(f"❌ Playwright Failed Req: {req.url} -> {req.failure}"))
            page.on("pageerror", lambda err: print(f"💥 Playwright Page Error: {err}"))

            # Set the content and wait for all assets to load
            await page.set_content(html_content, wait_until="networkidle")

            # Small delay for fonts/images to fully render
            await page.wait_for_timeout(1000)

            # Generate PDF using Chrome's native print engine
            # This properly respects CSS page-break-inside: avoid
            pdf_bytes = await page.pdf(
                format="A4",
                print_background=True,
                margin={
                    "top": "15mm",
                    "right": "12mm",
                    "bottom": "15mm",
                    "left": "12mm"
                }
            )

            await browser.close()

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=export.pdf"}
        )

    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


if __name__ == '__main__':
    import uvicorn
    # 1. Clear the port before starting to prevent bind errors
    kill_process_on_port(8000)
    
    print("=" * 60)
    print("🚀 Text Explain Project — Starting Server")
    print("=" * 60)
    print(f"📊 Visual Lexicon: {engine.stats()}")
    print(f"🌐 Open: http://localhost:8000")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
