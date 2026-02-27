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
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import requests
import google.generativeai as genai

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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:7b-instruct-q4_K_M")

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Using flash for speed/cost effectiveness for mapping tasks
        llm_model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini AI initialized for semantic mapping")
    except Exception as e:
        print(f"⚠️ Failed to initialize Gemini: {e}")
        llm_model = None
else:
    llm_model = None
    print("ℹ️ GEMINI_API_KEY not found. Using heuristic mapping.")

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
async def explain(request: Request, text: str = Form(...), ai_tier: str = Form("gemini")):
    """
    Accept document text and return a visual explanation HTML.
    """
    sections = parse_text_into_sections(text)
    visual_sections = []
    for section in sections:
        visual = generate_visual_section(section, ai_tier=ai_tier)
        visual_sections.append(visual)

    title = sections[0].get('title', "Document Explanation") if sections else "Document Explanation"
    title_banner = draw_banner(title[:30], font='slant')

    summary_text = sections[0].get('content', text[:200]) if sections else text[:200]
    summary_keywords = get_semantic_keywords_ai(summary_text, count=5, tier=ai_tier)
    summary_icons = engine.lookup_many(summary_keywords)

    return templates.TemplateResponse("explanation.html", {
        "request": request,
        "title": title,
        "title_banner": title_banner,
        "summary_text": summary_text,
        "summary_icons": summary_icons,
        "sections": visual_sections,
        "original_text": text,
    })


@app.post("/export-md")
async def export_markdown(text: str = Form(...)):
    """
    Generate a Markdown version of the visual explanation.
    """
    sections = parse_text_into_sections(text)
    md = []

    if sections:
        title = sections[0].get('title', "Document Explanation")
        md.append(f"# {title}")
        md.append("\n```\n" + draw_banner(title[:30]) + "\n```\n")

    md.append("## 📋 Summary")
    summary_text = sections[0].get('content', text[:200]) if sections else text[:200]
    md.append(summary_text[:500])
    md.append("\n---\n")

    for section in sections:
        visual = generate_visual_section(section)

        if visual['ascii_separator']:
            md.append("```\n" + visual['ascii_separator'] + "\n```")

        if visual['title']:
            icons_str = ""
            for icon in visual['title_icons']:
                if icon['type'] == 'openmoji':
                    # We could try to map back to actual unicode emoji here,
                    # but for now we'll just use the keyword as a surrogate
                    icons_str += f"[{icon['keyword']}] "
            md.append(f"### {icons_str}{visual['title']}")

        if visual['content']:
            md.append(visual['content'])

        if visual['bullets']:
            for i, bullet in enumerate(visual['bullets']):
                icon_pref = ""
                if visual['bullet_icons'] and i < len(visual['bullet_icons']):
                    for icon in visual['bullet_icons'][i]:
                        if icon['type'] != 'none':
                            icon_pref += f"[{icon['keyword']}] "
                md.append(f"- {icon_pref}{bullet}")

        md.append("") # Spacer

    md.append("\n---\n*Generated by Text Explain — Visual Lexicon for Semantic Text Annotation*")

    return JSONResponse({"markdown": "\n".join(md)})


@app.post("/shape-it", response_class=JSONResponse)
async def shape_it_api(
    text: str = Form(...),
    shape: str = Form("box"),
    style: str = Form("double"),
    font: str = Form("slant"),
):
    """Generate SHAPE_IT ASCII art for given text."""
    result = ""
    try:
        if shape == "box":
            result = draw_box(text, style=style)
        elif shape == "titled_box":
            parts = text.split("|", 1)
            title = parts[0].strip()
            body = parts[1].strip() if len(parts) > 1 else ""
            result = draw_titled_box(title, body, style=style)
        elif shape == "banner":
            result = draw_banner(text, font=font)
        elif shape == "callout":
            result = draw_callout(text)
        elif shape == "separator":
            result = draw_separator(text, width=50, style=style)
        elif shape == "pyramid":
            try:
                height = int(text)
            except ValueError:
                height = 5
            result = draw_pyramid(height)
        elif shape == "diamond":
            try:
                height = int(text)
            except ValueError:
                height = 7
            result = draw_diamond(height)
        elif shape == "flowchart":
            steps = [s.strip() for s in text.split("→") if s.strip()]
            if not steps:
                steps = [s.strip() for s in text.split(",") if s.strip()]
            result = draw_flowchart(steps)
        elif shape == "vertical_flow":
            steps = [s.strip() for s in text.split("→") if s.strip()]
            if not steps:
                steps = [s.strip() for s in text.split(",") if s.strip()]
            result = draw_vertical_flow(steps)
        elif shape == "table":
            # Format: header1,header2|row1col1,row1col2|row2col1,row2col2
            parts = text.split("|")
            headers = [h.strip() for h in parts[0].split(",")]
            rows = [[c.strip() for c in row.split(",")] for row in parts[1:] if row.strip()]
            result = draw_table(headers, rows)
        elif shape == "hierarchy":
            items = [s.strip() for s in text.split(",") if s.strip()]
            result = draw_hierarchy(items)
        elif shape == "arrow":
            result = draw_arrow(direction='right', length=20, label=text)
        else:
            result = draw_box(text, style=style)
    except Exception as e:
        result = f"Error generating shape: {str(e)}"

    return {"ascii": result, "shape": shape}


@app.post("/magic-prompt/distill", response_class=JSONResponse)
async def get_magic_prompt_distill(request: Request):
    """Phase 1: Generate a prompt to distill/summarize raw text."""
    data = await request.json()
    text = data.get("text", "")
    prompt = f"""
I want you to act as a Document Architect. Your job is to take the text below and transform it into a vibrant, high-impact overview.

COMMAND:
Explain the following using shape-it ascii art style:

RULES:
1. Distill the text into 3-5 key sections.
2. For each section, provide a short title and 1-2 sentences of clear content.
3. Break down details into bullet points.
4. Use your creative judgment to 'draw' the layout using the shape-it ASCII style (boxes, flows, separators).

OUTPUT FORMAT:
# [Catchy Main Title]

## [Section 1 Title]
Content: [Simple explanation]
Bullets:
- [Point A]
- [Point B]

[Repeat for other sections...]

DOCUMENT TEXT:
{text[:10000]}
"""
    return {"prompt": prompt.strip()}


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
Crucially, I want you to perform **Granular Semantic Mapping** — identifying a visual keyword for EVERY sentence.

RULES FOR JSON:
1. For each section, break the 'content' into individual sentences.
2. For EVERY sentence, identify exactly ONE high-impact English keyword (noun) that represents that specific thought.
3. Ensure the output begins with a VALID JSON block inside ```json ... ``` markers.
4. **VISUAL TIP: We have a massive library of 90,000+ Clipart and Doodles. To get VIBRANT images, use descriptive keywords like 'doodle robot', 'sketched idea', 'colorful building', or 'vivid heart'. Use 'doodle' as a prefix for a high-impact hand-drawn look.**
5. **SEMANTIC TIP: If a concept is abstract (like 'safety' or 'duplication'), choose a VIVID keyword that represents it (e.g., 'shield' for safety, 'copy' or 'stack' for duplication).**

RULES FOR ASCII ART:
6. **CRITICAL: DO NOT put the ASCII art inside the JSON.**
7. Instead, AFTER the JSON block, output each section's ASCII art. You MUST wrap EVERY ASCII block in ```text ... ``` code fences so the spaces are preserved. Separate them by `=== ASCII SECTION X ===` markers.
8. Copy the ASCII blocks EXACTLY. Do NOT truncate lines, do NOT remove underscores, and do NOT 'summarize' the drawing. It must be a 1:1 character match.

HYBRID STRUCTURE TO FOLLOW:

```json
{{
  "title": "Document Title",
  "summary": "Overall summary",
  "summary_keywords": ["vibrant1", "vibrant2"],
  "sections": [
    {{
      "title": "Section Title",
      "sentences": [
        {{
          "text": "The first sentence.",
          "keyword": "vivid_concept1"
        }}
      ],
      "bullets": ["Point 1", "Point 2"]
    }}
  ]
}}
```

=== ASCII SECTION 1 ===
```text
THE EXACT ASCII ART BLOCK FROM PHASE 1 - DO NOT ALTER
```

=== ASCII SECTION 2 ===
```text
THE EXACT ASCII ART BLOCK FROM PHASE 1 - DO NOT ALTER
```

TEXT TO MAP:
{distilled_text[:10000]}
"""
    return {"prompt": prompt.strip()}


@app.post("/render-magic", response_class=HTMLResponse)
async def render_magic(request: Request, data: str = Form(...)):
    """Render a visual explanation from AI-generated Hybrid format."""
    try:
        raw_text = data.strip()
        
        # 1. Extract JSON block using regex
        json_match = re.search(r'```json\s*(.*?)\s*```', raw_text, re.DOTALL | re.IGNORECASE)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Fallback: find first { and last }
            start = raw_text.find('{')
            end = raw_text.rfind('}')
            if start != -1 and end != -1:
                json_str = raw_text[start:end+1]
            else:
                raise ValueError("Could not find JSON block in output.")
        
        try:
            ai_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            # Deep fallback for broken trailing commas or quotes
            print(f"⚠️ JSON Decode Error: {e}. Attempting basic fix...")
            json_str = json_str.replace("'", '"')
            ai_data = json.loads(json_str)
        
        # 2. Extract ASCII Blocks
        ascii_blocks = {}
        # Highly resilient regex: matches == ASCII SECTION 1 ==, ### ASCII SECTION 1 ###, etc.
        pattern = re.compile(r'(?:=+|-+|#+|\*\*)\s*ASCII SECTION\s+(\d+)\s*(?:=+|-+|#+|\*\*)', flags=re.IGNORECASE)
        parts = pattern.split(raw_text)
        
        # parts will be: [preamble, '1', block_1_text, '2', block_2_text, ...]
        for i in range(1, len(parts) - 1, 2):
            try:
                sec_num = int(parts[i].strip())
                # CRITICAL FIX: Use .strip('\r\n') instead of .strip() to preserve leading spaces on the first line!
                block = parts[i+1].strip('\r\n')
                
                # Remove markdown code block wrappers if the LLM added them around the ASCII art
                block = re.sub(r'^```[\w]*\s*\n', '', block)
                block = re.sub(r'\n```\s*$', '', block)
                
                # 0-indexed internally
                ascii_blocks[sec_num - 1] = block
            except ValueError:
                pass
        
        # Transform AI data into our visual_sections format
        visual_sections = []
        for idx, section in enumerate(ai_data.get('sections', [])):
            sec_title = section.get('title', '')
            sec_sentences = section.get('sentences', [])
            sec_bullets = section.get('bullets', [])
            
            # Reconstruct content from sentences for ASCII art and legacy support
            reconstructed_content = " ".join([s.get('text', '') for s in sec_sentences])
            if not reconstructed_content:
                reconstructed_content = section.get('content', '')

            # Process sentence-level icons
            processed_sentences = []
            all_sec_keywords = []
            for sent in sec_sentences:
                kw = sent.get('keyword', '')
                if kw:
                    all_sec_keywords.append(kw)
                    icon = engine.lookup(kw)
                else:
                    icon = None
                processed_sentences.append({
                    'text': sent.get('text', ''),
                    'icon': icon
                })

            # USE ORIGINAL RAW ASCII FROM HYBRID OUTPUT
            # Get the block from the parsed ascii_blocks (0-indexed) or fallback to 'raw_ascii' from old JSON
            raw_ai_ascii = ascii_blocks.get(idx, section.get('raw_ascii', ''))
            raw_ai_ascii = normalize_ascii(raw_ai_ascii)
            
            # Only fallback to app-generated if AI provided none
            ascii_box = raw_ai_ascii
            if not ascii_box and reconstructed_content:
                 ascii_box = draw_titled_box(sec_title or f'Section {idx+1}', reconstructed_content[:120], style='double', padding=1)

            visual = {
                'title': sec_title,
                'content': reconstructed_content,
                'sentences': processed_sentences,
                'bullets': sec_bullets,
                'type': 'h2',
                'ascii_separator': '',  # Removed: User wants no app-injected changes
                'ascii_box': ascii_box,
                'ascii_flow': '',       # Removed: Prioritize LLM's own flow/art
                'ascii_callout': '',    # Removed: Prioritize LLM's own callouts
                'title_icons': engine.lookup_many(all_sec_keywords[:2]),
                'bullet_icons': []
            }
            for bullet in visual['bullets']:
                bullet_words = extract_keywords(bullet, 2)
                visual['bullet_icons'].append(engine.lookup_many(bullet_words))
            
            visual_sections.append(visual)

        title = ai_data.get('title', 'AI Analysis')
        title_banner = draw_banner(title[:30], font='slant')
        
        summary_text = ai_data.get('summary', '')
        summary_keywords = ai_data.get('summary_keywords', [])
        if not summary_keywords:
            summary_keywords = extract_keywords(summary_text, 5)
        summary_icons = engine.lookup_many(summary_keywords)

        return templates.TemplateResponse("explanation.html", {
            "request": request,
            "title": title,
            "title_banner": title_banner,
            "summary_text": summary_text,
            "summary_icons": summary_icons,
            "sections": visual_sections,
            "original_text": "Manual AI Input"
        })
    except Exception as e:
        return HTMLResponse(content=f"<p style='color:red;'>Error processing AI JSON: {str(e)}</p>", status_code=400)


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


# ─────────────────────────────────────────────────────────────
# Text Processing Helpers
# ─────────────────────────────────────────────────────────────

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


def get_semantic_keywords_ai(text, count=5, tier="gemini"):
    """
    Use selected AI Strategy to choose the best iconographic keywords.
    """
    if tier == "manual":
        return extract_keywords(text, count)
    
    if tier == "ollama":
        return get_semantic_keywords_ollama(text, count)

    if not llm_model:
        return extract_keywords(text, count)

    prompt = f"""
    Analyze the following text and select the {count} most important concept keywords
    that would best describe it visually using simple icons or emojis.

    RULES:
    - Return ONLY a JSON list of strings.
    - Choose keywords that are common objects, actions, or simple concepts.
    - Example: For text about "learning to code", you might return ["study", "computer", "code", "brain"].

    TEXT:
    {text}
    """

    try:
        response = llm_model.generate_content(prompt)
        content = response.text.strip()
        # Clean up JSON if LLM added markdown wrappers
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
             content = content.replace("```", "").strip()

        keywords = json.loads(content)
        return keywords[:count]
    except Exception as e:
        print(f"⚠️ AI mapping error: {e}")
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


def generate_visual_section(section, ai_tier="gemini"):
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
    }

    # Generate separator for headers
    if visual['title']:
        visual['ascii_separator'] = draw_separator(visual['title'], width=55)

        # Look up icons for the title
        title_keywords = get_semantic_keywords_ai(visual['title'], count=3, tier=ai_tier)
        visual['title_icons'] = engine.lookup_many(title_keywords)

    # Generate a titled box showing the section content
    if visual['content']:
        visual['ascii_box'] = draw_titled_box(visual['title'] or 'Section', visual['content'][:120], style='double', padding=1)
        
        # If content is very short, add a callout
        if len(visual['content']) < 80:
            visual['ascii_callout'] = draw_callout(visual['content'])

        content_keywords = get_semantic_keywords_ai(visual['content'], count=5, tier=ai_tier)
        visual['content_icons'] = engine.lookup_many(content_keywords)

    # Generate a flowchart from bullets if there are 2+
    if len(visual['bullets']) >= 2:
        visual['ascii_flow'] = draw_flowchart(visual['bullets'][:5], style='single')

    # Generate icons for bullets
    for bullet in visual['bullets']:
        bullet_keywords = get_semantic_keywords_ai(bullet, count=2, tier=ai_tier)
        icons = engine.lookup_many(bullet_keywords)
        visual['bullet_icons'].append(icons)

    return visual


# ─────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    import uvicorn
    print("=" * 60)
    print("🚀 Text Explain Project — Starting Server")
    print("=" * 60)
    print(f"📊 Visual Lexicon: {engine.stats()}")
    print(f"🌐 Open: http://localhost:8000")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
