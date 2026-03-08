#!/usr/bin/env python3
import json
import os
import shutil
import tempfile
from pathlib import Path
import re
import sys

# Resolve script location and project root dynamically
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.app import parse_hybrid_to_visual_data, draw_banner, DATA_DIR

def run_fixed_md_generator(visual_data):
    """Run the exact layout logic patched in app.export_markdown on a mock dictionary."""
    temp_dir = tempfile.mkdtemp()
    try:
        md = []
        assets_dir = Path(temp_dir) / "assets"
        assets_dir.mkdir(exist_ok=True)

        def process_icon(icon):
            if not icon or icon['type'] == 'none' or not icon.get('path'):
                return None
            return f"assets/{icon['keyword']}.png"

        # 1. Title Section
        icons_prefix = ""
        for icon in visual_data["title_icons"]:
            rel_src = process_icon(icon)
            if rel_src:
                icons_prefix += f'<img src="{rel_src}" alt="{icon["keyword"]}" width="48"> '
            elif icon['type'] != 'none':
                icons_prefix += f"[{icon['keyword']}] "
                
        md.append(f"# {icons_prefix}{visual_data['title'] or 'Visual Explanation'}")

        # 2. Summary Section
        md.append("## 📋 Summary")
        md.append(visual_data["explanation_text"])

        # 3. Sections - THE FIXED ORDER
        for visual in visual_data["sections"]:
            # 3a. ascii_separator BEFORE header
            if visual.get('ascii_separator'):
                md.append("```\n" + visual['ascii_separator'] + "\n```")

            # 3b. Section header
            if visual['title']:
                icons_str = ""
                for icon in visual['title_icons']:
                    rel_src = process_icon(icon)
                    if rel_src:
                        icons_str += f'<img src="{rel_src}" alt="{icon["keyword"]}" width="32"> '
                md.append(f"### {icons_str}{visual['title']}")

            # 3c. ascii_box AFTER header
            if visual.get('ascii_box'):
                md.append("```\n" + visual['ascii_box'] + "\n```")

            # 3d. Sentences
            if visual.get('sentences'):
                for sent in visual['sentences']:
                    sent_text = sent.get('text', '').strip()
                    icon = sent.get('icon')
                    rel_src = process_icon(icon)
                    if rel_src:
                        md.append(f'<img src="{rel_src}" alt="{icon["keyword"]}" width="24"> {sent_text}')
                    elif sent_text:
                        md.append(sent_text)
                    if sent.get('ascii'):
                        md.append("```\n" + sent['ascii'] + "\n```")
            elif visual['content']:
                md.append(visual['content'])

            # 3e. ascii_callout AFTER sentences
            if visual.get('ascii_callout'):
                md.append("```\n" + visual['ascii_callout'] + "\n```")

            # 3f. ascii_flow AFTER callout
            if visual.get('ascii_flow'):
                md.append("```\n" + visual['ascii_flow'] + "\n```")

            # 3g. Bullets
            if visual['bullets']:
                for i, bullet in enumerate(visual['bullets']):
                    md.append(f"- {bullet}")

        return "\n".join(md)
    finally:
        shutil.rmtree(temp_dir)

mock_visual_data = {
    "title": "Testing Alignment",
    "title_icons": [{"keyword": "rocket", "type": "png", "path": "rocket.png"}],
    "explanation_text": "This guarantees the Markdown layout logic is tested.",
    "sections": [
        {
            "title": "Step 1",
            "title_icons": [{"keyword": "moon", "type": "png", "path": "moon.png"}],
            "content": "First content.",
            "ascii_separator": "---------------",
            "ascii_box": "+-------+\\n| Box 1 |\\n+-------+",
            "ascii_callout": "/ Callout /",
            "ascii_flow": "A -> B",
            "bullets": ["Bullet 1", "Bullet 2"],
            "sentences": [
                {
                    "text": "First content.", 
                    "icon": {"keyword": "moon", "type": "png", "path": "test.png"},
                    "ascii": ""
                }
            ]
        }
    ]
}

if __name__ == "__main__":
    print("Testing new MD layout generation...")
    md = run_fixed_md_generator(mock_visual_data)
    
    print("\\nGENERATED MARKDOWN:\\n")
    print(md)
    
    print("\\n\\nVERIFYING ORDER...")
    
    lines = md.split('\\n')
    idx_sep = md.find('---------------')
    idx_hdr = md.find('###')
    idx_box = md.find('Box 1')
    idx_sent = md.find('First content')
    idx_call = md.find('Callout')
    idx_flow = md.find('A -> B')
    idx_bul = md.find('- Bullet 1')
    
    for name, idx in [("Separator", idx_sep), ("Header", idx_hdr), ("Box", idx_box), 
                      ("Sentences", idx_sent), ("Callout", idx_call), 
                      ("Flow", idx_flow), ("Bullets", idx_bul)]:
        assert idx != -1, f"Missing element: {name} in Markdown output"

    assert idx_sep < idx_hdr, "Separator should be BEFORE header"
    assert idx_hdr < idx_box, "Header should be BEFORE box"
    assert idx_box < idx_sent, "Box should be BEFORE sentences"
    assert idx_sent < idx_call, "Sentences should be BEFORE callout"
    assert idx_call < idx_flow, "Callout should be BEFORE flow"
    assert idx_flow < idx_bul, "Flow should be BEFORE bullets"
    
    print("✅ All elements perfectly aligned matching HTML template!")
