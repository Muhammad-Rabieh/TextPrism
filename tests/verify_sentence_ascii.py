import json
import re
from app import engine, normalize_ascii
from shape_it import draw_box, draw_callout, draw_banner, draw_separator

def test_render_magic_logic(raw_content, raw_text=""):
    # 2. Extract ASCII Blocks
    ascii_blocks = {}
    pattern = re.compile(r'(?:=+|-+|#+|\*\*)\s*ASCII (?:SECTION|FOR SENTENCE)\s+([\d\.]+)\s*(?:=+|-+|#+|\*\*)', flags=re.IGNORECASE)
    parts = pattern.split(raw_text)
    for i in range(1, len(parts) - 1, 2):
        key = parts[i].strip()
        block = parts[i+1].strip('\r\n')
        block = re.sub(r'^```[\w]*\s*\n', '', block)
        block = re.sub(r'\n```\s*$', '', block)
        ascii_blocks[key] = block

    processed_sentences = []
    tag_pattern = re.compile(r'\[([\w\s_-]+)\]\s*(?:\[shape:\s*([\w_-]+)\])?')
    
    last_pos = 0
    for match in tag_pattern.finditer(raw_content):
        pre_text = raw_content[last_pos:match.start()].strip()
        if pre_text and processed_sentences:
            processed_sentences[-1]['text'] += " " + pre_text
        elif pre_text:
             processed_sentences.append({'text': pre_text, 'icon': None, 'ascii': ''})
        
        kw = match.group(1).strip()
        shape = match.group(2).strip() if match.group(2) else "none"
        last_pos = match.end()
        
        icon = engine.lookup(kw) if kw else None
        processed_sentences.append({
            'text': '', 
            'icon': icon,
            'shape': shape,
            'ascii': ''
        })

    text_parts = tag_pattern.split(raw_content)
    cursor = 1
    sent_idx = 0
    while cursor < len(text_parts) and sent_idx < len(processed_sentences):
        txt = text_parts[cursor+2].strip() if cursor+2 < len(text_parts) else ""
        processed_sentences[sent_idx]['text'] = txt
        
        # Resolve ASCII
        ai_key = f"1.{sent_idx+1}" # Hardcoded section 1 for test
        ai_drawn = ascii_blocks.get(ai_key)
        
        if ai_drawn:
            processed_sentences[sent_idx]['ascii'] = normalize_ascii(ai_drawn)
        else:
            shape = processed_sentences[sent_idx].get('shape', 'none')
            if shape != 'none' and txt:
                if shape == 'box':
                    processed_sentences[sent_idx]['ascii'] = normalize_ascii(draw_box(txt, padding=1))
        
        cursor += 3
        sent_idx += 1
    
    return processed_sentences

# Test Payload with MIXED AI-drawn and generated
test_content = "[rocket] [shape: box] AI-drawn block. [shield] [shape: box] Backend-generated block."
test_raw_text = """
=== ASCII FOR SENTENCE 1.1 ===
```text
+--------------+
| AI CUSTOM ART|
+--------------+
```
"""

results = test_render_magic_logic(test_content, test_raw_text)

for i, res in enumerate(results):
    print(f"--- Sentence {i+1} ---")
    print(f"Text: {res['text']}")
    print(f"Shape: {res.get('shape')}")
    if res['ascii']:
        print("ASCII Rendering:")
        print(res['ascii'])
    print("\n")
