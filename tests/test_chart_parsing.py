import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from src.app import parse_hybrid_to_visual_data

def test_svg_and_mermaid_hybrid_parsing():
    """
    Test that the hybrid parser correctly extracts and identifies SVG and Mermaid charts.
    """
    mock_hybrid_response = """
```json
{
  "title": "Chart Testing",
  "explanation": "Testing various chart types.",
  "sections": [
    {
      "title": "SVG Section",
      "content": "This section has an SVG."
    },
    {
      "title": "Mermaid Section",
      "content": "This section has a Mermaid graph."
    }
  ]
}
```

=== CHART SECTION 1 ===
```xml
<svg width="100" height="100">
  <circle cx="50" cy="50" r="40" stroke="green" stroke-width="4" fill="yellow" />
</svg>
```

=== CHART SECTION 2 ===
```mermaid
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
```
"""

    visual_data = parse_hybrid_to_visual_data(mock_hybrid_response)

    assert len(visual_data['sections']) == 2
    
    # Section 1 should be SVG
    sec1 = visual_data['sections'][0]
    assert sec1['title'] == "SVG Section"
    assert sec1['chart_type'] == "svg"
    assert "<svg" in sec1['ascii_box']

    # Section 2 should be Mermaid
    sec2 = visual_data['sections'][1]
    assert sec2['title'] == "Mermaid Section"
    assert sec2['chart_type'] == "mermaid"
    assert "graph TD;" in sec1['ascii_box'] or "graph TD;" in sec2['ascii_box']
    
    print("✅ Hybrid parsing of SVG and Mermaid charts passed successfully!")

if __name__ == "__main__":
    test_svg_and_mermaid_hybrid_parsing()
