import sys
import os
import json
import base64
import re
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
      "explanation": "[power] Resilient systems with [safety] generic structural safety.",
      "explanation_keywords": ["power", "safety", "vibrant"],
      "sections": [
        {
          "title": "Structural Blueprint",
          "content": "[power] The core of the system is designed for modular power.",
          "bullets": ["Modular setup.", "High efficiency."]
        },
        {
          "title": "Type Safety Shield",
          "content": "[safety] Strong safety guarantees are provided at compile time.",
          "bullets": ["No runtime crashes.", "Strict typing."]
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
        # 3. New Parser for Inline Tags
        processed_sentences = []
        all_kw = []
        parts = re.split(r'\[([\w\s_-]+)\]', section.get('content', ''))
        
        if parts[0].strip():
            processed_sentences.append({'text': parts[0].strip(), 'icon': None})
            
        for i in range(1, len(parts), 2):
            kw = parts[i].strip()
            text = parts[i+1].strip() if i+1 < len(parts) else ""
            all_kw.append(kw)
            res = engine.lookup(kw)
            
            # Embed image data so it works locally
            encoded_img = get_base64_image(res['path']) if res['path'] else ""
            
            processed_sentences.append({
                "text": text,
                "icon": {
                    "type": res["type"],
                    "src": res["path"],
                    "data_uri": encoded_img
                }
            })

        # Section title icons
        title_icons = engine.lookup_many(all_kw[:2])
        for icon in title_icons:
            if icon.get('path'):
                icon['src'] = get_base64_image(icon['path'])

        normalized_art = normalize_ascii(ascii_blocks[idx] if idx < len(ascii_blocks) else "")

        visual_sections.append({
            'title': section.get('title', ''),
            'sentences': processed_sentences,
            'bullets': section.get('bullets', []),
            'type': 'h2',
            'ascii_box': normalized_art,
            'title_icons': title_icons,
            'bullet_icons': []
        })

    # Summary icons
    summary_text = json_data.get('explanation', '')
    summary_icons = engine.lookup_many(json_data.get('explanation_keywords', []))
    for icon in summary_icons:
        if icon.get('path'):
            icon['src'] = get_base64_image(icon['path'])

    # Render
    response = templates.TemplateResponse("explanation.html", {
        "request": MockRequest(),
        "title": json_data['title'],
        "explanation_text": summary_text,
        "explanation_icons": summary_icons,
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
