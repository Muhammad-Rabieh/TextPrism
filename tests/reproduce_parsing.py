
import re
import json

def detect_chart_type(content):
    if not content:
        return 'ascii'
    c = content.strip()
    if c.startswith('<svg') or c.startswith('<?xml'):
        return 'svg'
    first_word = c.split()[0].lower() if c.split() else ""
    mermaid_kws = {'graph', 'flowchart', 'sequencediagram', 'pie', 'classdiagram', 'statediagram', 'statediagram-v2', 'gantt', 'erdiagram', 'journey', 'gitgraph', 'mindmap', 'timeline'}
    if first_word in mermaid_kws:
        return 'mermaid'
    return 'ascii'

raw_text = r"""
{
  "title": "The Parallel Postulate and the Architecture of Geometric Worlds",
  "explanation": "...",
  "sections": [
    {
      "title": "[pillar] Euclid’s Fifth Postulate",
      "content": "...",
      "bullets": ["..."]
    }
  ]
}

=== CHART SECTION 1 ===

flowchart TD

A[Parallel Postulate Context] --> B[Transversal Line]
"""

# Extract ASCII/Chart Blocks
ascii_blocks = {}
pattern = re.compile(r'(?:=+|-+|#+|\*\*)\s*(?:ASCII|CHART)\s+(?:SECTION|FOR SENTENCE|FOR CONCEPT)\s+([\d\.]+)\s*(?:=+|-+|#+|\*\*)', flags=re.IGNORECASE)
parts = pattern.split(raw_text)

print(f"Parts found: {len(parts)}")
for i in range(1, len(parts) - 1, 2):
    key = parts[i].strip()
    block = parts[i+1].strip('\r\n')
    # Cleanup code fences if present
    block = re.sub(r'^```[\w]*\s*\n', '', block)
    block = re.sub(r'\n```\s*$', '', block)
    ascii_blocks[key] = block
    print(f"Key: [{key}] Block: [{block!r}]")
    print(f"Detected Type: {detect_chart_type(block)}")

json_str = raw_text.split('===')[0].strip()
ai_data = json.loads(json_str)
for idx, section in enumerate(ai_data.get('sections', [])):
    sec_key = str(idx + 1)
    raw_ai_ascii = ascii_blocks.get(sec_key)
    print(f"Section {idx+1} raw_ai_ascii: {raw_ai_ascii!r}")
    if raw_ai_ascii:
        print(f"Section {idx+1} detected type: {detect_chart_type(raw_ai_ascii)}")
