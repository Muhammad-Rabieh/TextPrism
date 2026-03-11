import os
import sys

# Add src to path
# Resolve script location and project root dynamically
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.append(project_root)
if os.path.join(project_root, 'src') not in sys.path:
    sys.path.append(os.path.join(project_root, 'src'))

from src.app import detect_chart_type, parse_hybrid_to_visual_data

def test_mermaid_formatting():
    # Case 1: Same line flowchart
    bad_mermaid = "flowchart TD    A[Start] --> B[End]"
    ctype = detect_chart_type(bad_mermaid)
    print(f"Chart Type for same-line: {ctype}")
    
    # Simulate what app.py does
    # parse_hybrid_to_visual_data results
    raw_hybrid = f"""{{
  "title": "Test",
  "explanation": "Test",
  "sections": [
    {{
      "title": "Sec",
      "content": "Content"
    }}
  ]
}}
=== CHART SECTION 1 ===
{bad_mermaid}
"""
    data = parse_hybrid_to_visual_data(raw_hybrid)
    section = data['sections'][0]
    print(f"Detected Section Chart Type: {section['chart_type']}")
    print(f"ASCII Box Content:\n'{section['ascii_box']}'")

if __name__ == "__main__":
    test_mermaid_formatting()
