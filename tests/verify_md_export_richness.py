import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
import re

# Mocking parts of app.py to test the logic in isolation
import sys
project_root = "/home/muhammad/Desktop/expressive text/TextPrism"
if project_root not in sys.path:
    sys.path.append(project_root)

from app import parse_hybrid_to_visual_data, draw_box, draw_banner, DATA_DIR

def simulate_export_markdown(raw_text):
    """Simplified version of app.export_markdown for testing."""
    temp_dir = tempfile.mkdtemp()
    try:
        visual_data = parse_hybrid_to_visual_data(raw_text)
        md = []
        assets_dir = Path(temp_dir) / "assets"
        assets_dir.mkdir(exist_ok=True)

        def process_icon(icon):
            if not icon or icon['type'] == 'none' or not icon.get('path'):
                return None
            src_path = os.path.join(DATA_DIR, icon['path'])
            if not os.path.exists(src_path):
                return None
            ext = os.path.splitext(src_path)[1]
            safe_kw = re.sub(r'[^\w\s-]', '', icon['keyword']).strip().replace(' ', '_')
            target_filename = f"{safe_kw}_{hash(icon['path']) % 10000}{ext}"
            target_path = assets_dir / target_filename
            shutil.copy2(src_path, target_path)
            return f"assets/{target_filename}"

        # 1. Title
        icons_prefix = ""
        for icon in visual_data["title_icons"]:
            rel_src = process_icon(icon)
            if rel_src:
                icons_prefix += f'<img src="{rel_src}" width="48"> '
        md.append(f"# {icons_prefix}{visual_data['title'] or 'Visual Explanation'}")
        
        if visual_data.get('title_ascii'):
            md.append("```\n" + visual_data['title_ascii'] + "\n```")
        elif visual_data['title']:
            md.append("```\n" + draw_banner(visual_data['title'][:30]) + "\n```")

        # 2. Summary
        md.append("## 📋 Summary")
        if visual_data.get('explanation_ascii'):
            md.append("```\n" + visual_data['explanation_ascii'] + "\n```")
        md.append(visual_data["explanation_text"])
        
        # 3. Sections
        for visual in visual_data["sections"]:
            md.append(f"### {visual['title']}")
            if visual.get('ascii_box'):
                md.append("```\n" + visual['ascii_box'] + "\n```")
            
            if visual.get('sentences'):
                for sent in visual['sentences']:
                    icon = sent.get('icon')
                    rel_src = process_icon(icon)
                    prefix = f'<img src="{rel_src}" width="24"> ' if rel_src else ""
                    md.append(f"{prefix}{sent.get('text', '')}")
                    if sent.get('ascii'):
                        md.append("```\n" + sent['ascii'] + "\n```")

        md_content = "\n\n".join(md)
        return md_content, list(assets_dir.glob("*"))
    finally:
        shutil.rmtree(temp_dir)

# THE TEST CASE: Rich AI Hybrid Input
test_input = """
{
  "title": "[rocket] Exploring Mars",
  "explanation": "Humanity's journey to the red planet.",
  "sections": [
    {
      "title": "Historical Context",
      "content": "Mars has been a [telescope] focus of study for centuries.",
      "sentences": [
        "Mars has been a [telescope] focus of study for centuries."
      ]
    }
  ]
}

=== ASCII SECTION 1 ===
+--------------+
| ANCIENT MARS |
+--------------+
"""

print("🚀 Running MD Export Richness Verification...")
md, assets = simulate_export_markdown(test_input)

# Verify results
print("\n--- Generated Markdown Snippet ---")
print(md[:500] + "...")

print("\n--- Asset Verification ---")
print(f"Total assets copied: {len(assets)}")
for asset in assets:
    print(f" - {asset.name}")

# ASSERTIONS
assert "# " in md and "Exploring Mars" in md, "Title missing or incorrect"
assert "assets/" in md, "Asset links missing"
assert "```" in md, "ASCII code blocks missing"
assert "ANCIENT MARS" in md, "AI-drawn ASCII block missing"
assert len(assets) > 0, "No assets were copied"

print("\n✅ SUCCESS: Markdown export richness verified!")
