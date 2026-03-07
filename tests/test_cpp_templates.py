import sys
import os
import json
import base64
import re
from fastapi.testclient import TestClient

# Add current dir to path
sys.path.append(os.getcwd())

# Import our FastAPI app
from app import app

client = TestClient(app)

def inline_images_in_html(html_str):
    """
    Finds all relative src="/..." image tags in the HTML output
    and replaces them with embedded base64 data URIs so the file
    can be viewed locally without running the FastAPI server.
    """
    def replacer(match):
        img_path = match.group(1)
        # remove leading slash
        if img_path.startswith('/'):
            img_path = img_path[1:]
        
        # Try finding it in local data dir or directly
        for p in [img_path, os.path.join('data', img_path)]:
            full_path = os.path.join(os.getcwd(), p)
            if os.path.exists(full_path):
                ext = os.path.splitext(p)[1][1:].lower()
                try:
                    if ext == 'svg':
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            return f'src="data:image/svg+xml;base64,{base64.b64encode(content.encode()).decode()}"'
                    else:
                        with open(full_path, 'rb') as f:
                            return f'src="data:image/{ext};base64,{base64.b64encode(f.read()).decode()}"'
                except Exception as e:
                    print(f"Error encoding {p}: {e}")
        return match.group(0)

    # find src="/..."
    return re.sub(r'src="(/[^"]+)"', replacer, html_str)


# ══════════════════════════════════════════════════════════════
# ASCII ART BLOCKS — Exact 1:1 character-match from user input
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
    C++ Templates Tutorial — tests the fully integrated /render-magic endpoint.
    It builds a mock LLM Hybrid Response and POSTs it to the app.
    """

    json_data = {
      "title": "GENERIC MACHINES: How C++ Templates Multiply Power",
      "explanation": "[gear] C++ templates enable generic, reusable, and type-safe programming across multiple data types. [lightning] They eliminate duplication, enforce compile-time safety, and power the STL ecosystem.",
      "explanation_keywords": ["gear", "lightning"],
      "sections": [
        {
          "title": "The Generic Blueprint",
          "content": "[blueprint] A C++ template is a tool for building generic classes or functions. [recycle] It lets the same logic adapt to any data type without rewriting the code.",
          "bullets": [
            "Create flexible functions.",
            "Create reusable classes.",
            "Automatically generate type-specific versions at compile time."
          ]
        },
        {
          "title": "One Definition, Zero Duplication",
          "content": "[layers] Templates remove repeated code by allowing one function or class to handle many types. [sparkles] Instead of copying logic, you generalize it.",
          "bullets": [
            "Eliminate multiple nearly identical functions.",
            "Keep source code compact.",
            "Make maintenance easier."
          ]
        },
        {
          "title": "Safe and Customizable Power",
          "content": "[safety] Templates enforce strong type safety during compilation. [wrench] They can also be specialized to handle specific data types differently when needed.",
          "bullets": [
            "Safer than void* pointers.",
            "More reliable than macros.",
            "Allows custom behavior for special cases."
          ]
        },
        {
          "title": "Backbone of the STL",
          "content": "[foundation] Templates form the foundation of the Standard Template Library. [rocket] Core containers and algorithms rely on them to operate across all compatible data types.",
          "bullets": [
            "vector stores elements generically.",
            "map manages key–value pairs.",
            "sort works on many container types."
          ]
        }
      ]
    }
    # 1. Build the Hybrid Response Payload (Markdown Fences + ASCII Blocks)
    hybrid_payload = f"""```json\n{json.dumps(json_data, indent=2)}\n```

=== ASCII SECTION 1 ===
```text
{ASCII_SECTION_1}
```

=== ASCII SECTION 2 ===
```text
{ASCII_SECTION_2}
```

=== ASCII SECTION 3 ===
```text
{ASCII_SECTION_3}
```

=== ASCII SECTION 4 ===
```text
{ASCII_SECTION_4}
```
"""

    print("── Invoking /render-magic via API TestClient ──")
    response = client.post("/render-magic", data={"data": hybrid_payload})
    
    if response.status_code != 200:
        print(f"❌ Error {response.status_code}")
        print(response.text)
        return

    # 2. Extract HTML Output
    html_output = response.text

    # 3. Inline images for local portability without running FastAPI server
    print("── Inlining base64 assets for portability ──")
    portable_html = inline_images_in_html(html_output)

    output_path = "cpp_templates_tutorial.html"
    with open(output_path, "w", encoding='utf-8') as f:
        f.write(portable_html)

    print(f"\n✅ Generated successfully via API: {output_path}")
    print(f"   Open in browser: file://{os.path.abspath(output_path)}")
    return output_path

if __name__ == "__main__":
    generate_cpp_templates_test()
