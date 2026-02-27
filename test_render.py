import sys
import os
import json
import base64
from fastapi.templating import Jinja2Templates

# Add current dir to path
sys.path.append(os.getcwd())

from emoji_engine import EmojiEngine
from utils import normalize_ascii
from shape_it import draw_banner

class MockRequest:
    def __init__(self):
        self.scope = {}

templates = Jinja2Templates(directory="templates")
engine = EmojiEngine()

def get_base64_image(path):
    """Helper to embed images in standalone HTML for portability."""
    # Try direct path, then try within 'data' folder
    for p in [path, os.path.join('data', path)]:
        full_path = os.path.join(os.getcwd(), p)
        if os.path.exists(full_path):
            ext = os.path.splitext(p)[1][1:].lower()
            try:
                if ext == 'svg':
                    with open(full_path, 'r') as f:
                        return f"data:image/svg+xml;base64,{base64.b64encode(f.read().encode()).decode()}"
                else:
                    with open(full_path, 'rb') as f:
                        return f"data:image/{ext};base64,{base64.b64encode(f.read()).decode()}"
            except: pass
    return ""

def test_mapping_and_ascii():
    """Bypass UI to verify absolute correctness of mapping and ASCII reservation."""
    
    # Simulate LLM output: real newlines or escaped literals?
    # In my prompt I demand strict 1:1 match.
    json_data = {
      "title": "VIBRANT CORE",
      "summary": "Resilient systems with generic structural safety.",
      "summary_keywords": ["power", "safety", "vibrant"],
      "sections": [
        {
          "title": "Structural Blueprint",
          "sentences": [
            {
              "text": "The core of the system is designed for modular power.",
              "keyword": "power"
            }
          ]
        },
        {
          "title": "Type Safety Shield",
          "sentences": [
            {
              "text": "Strong safety guarantees are provided at compile time.",
              "keyword": "safety"
            }
          ]
        }
      ]
    }

    visual_sections = []
    # Provide dummy ASCII blocks as expected by Hybrid Format
    ascii_blocks = [
        "┌────────────────┐\n│   [ CORE ]     │\n│   VIBRANT art  │\n└────────────────┘",
        "      /----------\\\n     /  [SAFE]    \\\n    |--------------|\n    |    [____]    |\n    |    |____|    |\n    |______________|"
    ]

    for idx, section in enumerate(json_data["sections"]):
        # 1. Process Sentences
        processed_sentences = []
        all_kw = [] # Collect all keywords for title icons
        for sent in section["sentences"]:
            kw = sent["keyword"]
            all_kw.append(kw)
            res = engine.lookup(kw)
            
            # Embed image data so it works locally without server
            encoded_img = get_base64_image(res['path']) if res['path'] else ""
            
            processed_sentences.append({
                "text": sent["text"],
                "icon": {
                    "type": res["type"],
                    "src": res["path"],
                    "data_uri": encoded_img
                }
            })
            print(f"  {kw:<15} → {res['type']:<10} | {res['path']}")

        # 2. Extract ASCII (from hybrid blocks)
        raw_ai_ascii = ascii_blocks[idx] if idx < len(ascii_blocks) else ""
        normalized_art = normalize_ascii(raw_ai_ascii)

        # 3. Section title icons
        title_icons = engine.lookup_many(all_kw[:2]) # Use first two keywords for title icons
        for icon in title_icons:
            if icon.get('path'):
                icon['src'] = get_base64_image(icon['path'])

        # FIX FOR NEWLINES: Ensure they are real newlines
        raw_art = section.get('raw_ascii', '')
        normalized_art = normalize_ascii(raw_art)

        visual_sections.append({
            'title': section.get('title', ''),
            'sentences': processed_sentences,
            'bullets': [],
            'type': 'h2',
            'ascii_box': normalized_art,
            'title_icons': title_icons,
            'bullet_icons': []
        })

    # Summary icons
    summary_icons = engine.lookup_many(json_data.get('summary_keywords', []))
    for icon in summary_icons:
        if icon.get('path'):
            icon['src'] = get_base64_image(icon['path'])

    # Render
    response = templates.TemplateResponse("explanation.html", {
        "request": MockRequest(),
        "title": json_data['title'],
        "summary_text": json_data['summary'],
        "summary_icons": summary_icons,
        "sections": visual_sections,
        "original_text": "Manual Pipeline Debug"
    })

    output_path = "standalone_test_result.html"
    # Portability hack: replace src="/..." with src="base64..."
    # Since we put b64 in 'src' key, it will be rendered if we fix the template or use it
    content = response.body.decode()
    # Replace the templates icon path logic with a placeholder if path is empty
    # But better: just let the template use icon.path or icon.src
    with open(output_path, "wb") as f:
        f.write(response.body)
    
    print(f"✅ Rendered to {output_path}")

if __name__ == "__main__":
    test_mapping_and_ascii()
