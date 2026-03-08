import sys
import os

# Ensure we can import app
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from src.app import detect_chart_type

def test_detect_chart_type():
    # Test ASCII
    assert detect_chart_type("   +---------+\n   | Hello   |\n   +---------+") == "ascii"
    assert detect_chart_type("This is just text") == "ascii"

    # Test SVG
    assert detect_chart_type("<svg width=\"100\" height=\"100\"><circle cx=\"50\" cy=\"50\" r=\"40\"/></svg>") == "svg"
    assert detect_chart_type("   <svg viewBox=\"0 0 100 100\">\n  </svg> ") == "svg"

    # Test Mermaid
    assert detect_chart_type("graph TD;\n    A-->B;") == "mermaid"
    assert detect_chart_type("pie title Pets\n    \"Dogs\" : 386\n    \"Cats\" : 85") == "mermaid"
    assert detect_chart_type("sequenceDiagram\n    Alice->>John: Hello John, how are you?") == "mermaid"

    print("✅ All chart detection tests passed!")

if __name__ == "__main__":
    test_detect_chart_type()
