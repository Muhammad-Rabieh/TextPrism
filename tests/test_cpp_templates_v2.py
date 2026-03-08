import json
import re
from fastapi.testclient import TestClient
from src.app import app
from src.emoji_engine import EmojiEngine

client = TestClient(app)
engine = EmojiEngine()

def test_visual_density_cpp_templates():
    """
    STRICT VISUAL DENSITY TEST (2nd Stage)
    Ensures that EVERY sentence and EVERY section in the C++ Templates 
    document has a corresponding graphic element.
    """
    print("\n--- Starting 2nd Stage Visual Density Test: C++ Templates ---")
    
    # Payload with high-density inline tags
    cpp_payload = {
        "title": "C++ Templates: The Architect's Blueprint",
        "explanation": "[blueprint] C++ templates allow you to write generic code that [rocket] accelerates development and [shield] ensures type safety.",
        "explanation_keywords": ["blueprint", "rocket", "shield"],
        "sections": [
            {
                "title": "[factory] Generic Factory",
                "content": "[factory] A template acts as a blueprint for multiple data types. [gears] The compiler generates specific versions automatically.",
                "bullets": ["One definition", "Multiple types"]
            },
            {
                "title": "[shield] Code Safety Layer",
                "content": "[security] Templates are checked at compile time for errors. [lock] This prevents runtime type mismatches.",
                "bullets": ["Zero overhead", "Static checks"]
            },
            {
                "title": "[engine] STL Engines",
                "content": "[engine] Templates power the Standard Template Library. [briefcase] They provide efficient containers for any data structure.",
                "bullets": ["std::vector", "std::map"]
            }
        ]
    }

    # 1. Post to API
    json_str = json.dumps(cpp_payload)
    response = client.post("/render-magic", data={"data": json_str})
    
    assert response.status_code == 200, "API failed to render"
    html = response.text
    
    # 2. Extract DOM Sections for Granular Validation
    
    # A. Validate Explanation Icons
    print("Checking Explanation Box icons...")
    explanation_clause = re.search(r'<div class="explanation-box">.*?</div>', html, re.DOTALL)
    if explanation_clause:
        icons = re.findall(r'<span class="icon-chip">.*?<img.*?>.*?</span>', explanation_clause.group(0), re.DOTALL)
        print(f"  Found {len(icons)} explanation icons.")
        assert len(icons) >= 2, "Explanation box missing expected icons"
    else:
        print("  [!] Explanation box not found!")
        assert False, "Explanation box container missing from HTML"

    # B. Validate Sentence Icons (1:1 per sentence)
    print("Checking Sentence-level icons...")
    # Find all sentence items
    sentence_items = re.findall(r'<div class="sentence-item">.*?</div>', html, re.DOTALL)
    print(f"  Found {len(sentence_items)} sentence items.")
    
    # We expected 2 sentences per section * 3 sections = 6 sentences
    assert len(sentence_items) == 6, f"Expected 6 sentence items, found {len(sentence_items)}"
    
    for idx, item in enumerate(sentence_items):
        # Every sentence must have an image
        has_img = re.search(r'<img src=".*?"', item)
        assert has_img, f"Sentence {idx+1} is missing its icon!"
        # Check src is not empty
        src = re.search(r'src="(.*?)"', has_img.group(0)).group(1)
        assert src and src != "/", f"Sentence {idx+1} has an empty or invalid img src"
        print(f"  ✅ Sentence {idx+1}: Graphic confirmed.")

    # C. Validate Section Header Icons (Strict Parity)
    print("Checking Section Header icons (Strict Parity)...")
    section_headers = re.findall(r'<div class="section-header">.*?</div>', html, re.DOTALL)
    assert len(section_headers) == 3, f"Expected 3 sections, found {len(section_headers)}"
    
    for idx, header in enumerate(section_headers):
        # Every header MUST have exactly at least one icon (parity with the [tag] in the title)
        header_icons = re.findall(r'<img src=".*?"', header)
        print(f"  Section {idx+1} header icons: {len(header_icons)}")
        assert len(header_icons) >= 1, f"Section {idx+1} header is missing its mandatory icon!"
        
    print("\n✅ 2ND STAGE TEST PASSED: Strict Visual Parity Confirmed.")

if __name__ == "__main__":
    test_visual_density_cpp_templates()
