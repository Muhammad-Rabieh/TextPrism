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
    for p in [path, os.path.join('data', path)]:
        full_path = os.path.join(os.getcwd(), p)
        if os.path.exists(full_path):
            ext = os.path.splitext(p)[1][1:].lower()
            try:
                if ext == 'svg':
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        return f"data:image/svg+xml;base64,{base64.b64encode(content.encode()).decode()}"
                else:
                    with open(full_path, 'rb') as f:
                        return f"data:image/{ext};base64,{base64.b64encode(f.read()).decode()}"
            except Exception as e:
                print(f"Error encoding {path}: {e}")
    return ""


# ══════════════════════════════════════════════════════════════
# ASCII ART BLOCKS — Exact 1:1 character-match from user input
# Using raw triple-quoted strings to preserve every character.
# ══════════════════════════════════════════════════════════════

ASCII_SECTION_1 = """\
┌──────────────────────────────┐
│        TEMPLATE = MOLD       │
│   One Pattern → Many Types   │
└──────────────────────────────┘"""

ASCII_SECTION_2 = """\
 Without Templates              With Templates
 ┌───────────────┐             ┌────────────────┐
 │ func_int      │             │   func<T>      │
 │ func_float    │   ─────▶    │  One Generic   │
 │ func_double   │             │    Function    │
 └───────────────┘             └────────────────┘"""

ASCII_SECTION_3 = """\
        [ Type Safety ]
              ▲
              │
   Templates ─┼─ Compile-Time Checks
              │
              ▼
        [ Specialization ]"""

ASCII_SECTION_4 = """\
        ┌───────────────┐
        │   Templates   │
        └───────┬───────┘
                │
     ┌──────────┼──────────┐
     ▼          ▼          ▼
  [vector]    [map]     [sort]"""


def generate_cpp_templates_test():
    """
    C++ Templates Tutorial — fully offline visual explanation.
    No LLM, no API key, no network required.
    """

    json_data = {
      "title": "GENERIC MACHINES: How C++ Templates Multiply Power",
      "summary": "C++ templates enable generic, reusable, and type-safe programming across multiple data types. They eliminate duplication, enforce compile-time safety, and power the STL ecosystem.",
      "summary_keywords": ["gear", "lightning"],
      "sections": [
        {
          "title": "The Generic Blueprint",
          "sentences": [
            {
              "text": "A C++ template is a tool for building generic classes or functions.",
              "keyword": "blueprint"
            },
            {
              "text": "It lets the same logic adapt to any data type without rewriting the code.",
              "keyword": "recycle"
            }
          ],
          "bullets": [
            "Create flexible functions.",
            "Create reusable classes.",
            "Automatically generate type-specific versions at compile time."
          ]
        },
        {
          "title": "One Definition, Zero Duplication",
          "raw_ascii": ASCII_SECTION_2,
          "sentences": [
            {
              "text": "Templates remove repeated code by allowing one function or class to handle many types.",
              "keyword": "layers"
            },
            {
              "text": "Instead of copying logic, you generalize it.",
              "keyword": "sparkles"
            }
          ],
          "bullets": [
            "Eliminate multiple nearly identical functions.",
            "Keep source code compact.",
            "Make maintenance easier."
          ]
        },
        {
          "title": "Safe and Customizable Power",
          "sentences": [
            {
              "text": "Templates enforce strong type safety during compilation.",
              "keyword": "safety"
            },
            {
              "text": "They can also be specialized to handle specific data types differently when needed.",
              "keyword": "wrench"
            }
          ],
          "bullets": [
            "Safer than void* pointers.",
            "More reliable than macros.",
            "Allows custom behavior for special cases."
          ]
        },
        {
          "title": "Backbone of the STL",
          "sentences": [
            {
              "text": "Templates form the foundation of the Standard Template Library.",
              "keyword": "foundation"
            },
            {
              "text": "Core containers and algorithms rely on them to operate across all compatible data types.",
              "keyword": "rocket"
            }
          ],
          "bullets": [
            "vector stores elements generically.",
            "map manages key–value pairs.",
            "sort works on many container types."
          ]
        }
      ]
    }

    # ── Process sections ──────────────────────────────────────
    visual_sections = []
    print("\n── Icon Mapping Audit ──")
    for section in json_data.get('sections', []):
        sec_sentences = section.get('sentences', [])
        processed_sentences = []
        all_kw = []
        for sent in sec_sentences:
            kw = sent.get('keyword', '')
            if kw:
                all_kw.append(kw)
                icon = engine.lookup(kw)
                src = ""
                if icon.get('path'):
                    src = get_base64_image(icon['path'])
                    if src:
                        icon['src'] = src
                print(f"  {kw:15} → {icon.get('type', 'none'):10} | {'✅ embedded' if src else '❌ missing'} | {icon.get('path', 'N/A')}")
            else:
                icon = None
            processed_sentences.append({'text': sent.get('text', ''), 'icon': icon})

        title_icons = engine.lookup_many(all_kw[:2])
        for icon in title_icons:
            if icon.get('path'):
                src = get_base64_image(icon['path'])
                if src: icon['src'] = src

        # Process bullets with icons too
        bullet_icons = []
        for bullet in section.get('bullets', []):
            first_word = bullet.split()[0].lower().rstrip('.,!')
            bicon = engine.lookup(first_word)
            if bicon.get('path'):
                src = get_base64_image(bicon['path'])
                if src: bicon['src'] = src
            bullet_icons.append(bicon)

        visual_sections.append({
            'title': section.get('title', ''),
            'sentences': processed_sentences,
            'bullets': section.get('bullets', []),
            'type': 'h2',
            'ascii_box': normalize_ascii(section.get('raw_ascii', '')),
            'title_icons': title_icons,
            'bullet_icons': bullet_icons
        })

    # ── Summary icons ─────────────────────────────────────────
    summary_icons = engine.lookup_many(json_data.get('summary_keywords', []))
    for icon in summary_icons:
        if icon.get('path'):
            src = get_base64_image(icon['path'])
            if src: icon['src'] = src

    # ── Banner ────────────────────────────────────────────────
    banner_text = draw_banner("C++ TEMPLATES", font='slant')

    # ── Render ────────────────────────────────────────────────
    response = templates.TemplateResponse("explanation.html", {
        "request": MockRequest(),
        "title": json_data['title'],
        "title_banner": banner_text,
        "summary_text": json_data['summary'],
        "summary_icons": summary_icons,
        "sections": visual_sections,
        "original_text": "C++ Templates Tutorial (Offline Test)"
    })

    output_path = "cpp_templates_tutorial.html"
    with open(output_path, "wb") as f:
        f.write(response.body)

    print(f"\n✅ Generated: {output_path}")
    print(f"   Open in browser: file://{os.path.abspath(output_path)}")
    return output_path

if __name__ == "__main__":
    generate_cpp_templates_test()
