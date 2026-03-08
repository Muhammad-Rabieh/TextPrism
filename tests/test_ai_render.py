import json
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_render_magic_endpoint():
    """
    Test the /render-magic endpoint with the C++ Templates JSON.
    This verifies that the backend can parse the AI-generated structure
    and return a valid HTML response with visual elements.
    """
    cpp_templates_json = {
        "title": "The Blueprint of C++ Templates",
        "explanation": "[generic] C++ templates are a powerful feature used to write generic, [reusability] reusable code across multiple data types.",
        "explanation_keywords": ["generic", "reusability"],
        "sections": [
            {
                "title": "The Power of Generics",
                "content": "[blueprint] [shape: box] Templates act as a 'cookie cutter' for code, allowing you to write a single function or class that works with any data type. [adaptability] [shape: banner] It adapts to different inputs without rewriting.",
                "bullets": [
                    "Write Once, Use Everywhere.",
                    "Zero Duplication: No copy-paste."
                ]
            },
            {
                "title": "Safety and Customization",
                "content": "[security] Templates are checked by the compiler for errors. [customization] They can be 'specialized' to behave differently for specific types.",
                "bullets": [
                    "Type Safety: Prevents crashes.",
                    "Template Specialization: Custom versions."
                ]
            },
            {
                "title": "The Foundation of Modern C++",
                "content": "[engine] Templates are the engine behind the Standard Template Library (STL). [algorithm] They power vector, map, and universal algorithms.",
                "bullets": [
                    "Smart Containers: std::vector and std::map.",
                    "Universal Algorithms: Sorting and searching."
                ]
            }
        ]
    }

    # Convert to a "Hybrid" string with ASCII sections
    full_ai_response = json.dumps(cpp_templates_json) + "\n\n=== ASCII SECTION 1 ===\n┌─────────────────┐\n│ TEMPLATE BLUEPRINT │\n└─────────────────┘\n"

    # Post to the endpoint
    response = client.post("/render-magic", data={"data": full_ai_response})

    # Assertions
    assert response.status_code == 200
    assert "The Blueprint of C++ Templates" in response.text
    assert "The Power of Generics" in response.text
    assert "Safety and Customization" in response.text
    assert "The Foundation of Modern C++" in response.text
    
    # Verify specific technical content made it through
    assert "std::vector and std::map" in response.text
    assert "Zero Duplication" in response.text
    assert "cookie cutter" in response.text

    # Verify visual generation (Check for box/divider characters)
    assert "═" in response.text or "─" in response.text
    
    # Verify keywords (Check for at least one major keyword used in icons)
    assert "engine" in response.text or "security" in response.text or "logic" in response.text

    print("\n✅ Test Passed: C++ Templates JSON rendered successfully into visual explanation.")

@pytest.mark.parametrize("topic, json_data, expected_keywords", [
    ("Python Decorators", {
        "title": "Python Decorators: Wrapping Logic",
        "explanation": "[wrap] Decorators are a powerful way to modify function behavior without changing source code.",
        "explanation_keywords": ["wrap", "gift"],
        "sections": [
            {
                "title": "The Wrapper Concept",
                "content": "[gift] [shape: box] A decorator is a function that takes another function. [layer] It extends behavior while wrapping it.",
                "bullets": ["Wraps existing functions", "Executed at definition time"]
            },
            {
                "title": "Metaprogramming Power",
                "content": "[magic] [shape: box] They allow developers to write 'code that writes code'. [brain] Automation of repetitive tasks.",
                "bullets": ["Logging automation", "Authentication guards"]
            }
        ]
    }, ["wrap", "magic", "brain"]),
    ("Rust Ownership", {
        "title": "Rust Ownership: Memory Safety Rules",
        "explanation": "[law] Ownership ensures memory safety without a garbage collector via a strict set of rules.",
        "explanation_keywords": ["law", "safety"],
        "sections": [
            {
                "title": "Ownership Rules",
                "content": "[master] [shape: box] Each value has one owner. [safety] When the owner goes out of scope, the value is dropped.",
                "bullets": ["One owner at a time", "Scope-based cleanup"]
            },
            {
                "title": "Borrowing & References",
                "content": "[lend] Data can be lent via references. [link] Borrowing follows strict rules.",
                "bullets": ["Immutable references", "Mutable references"]
            }
        ]
    }, ["law", "Borrowing", "safety"])
])
def test_complex_technical_rendering(topic, json_data, expected_keywords):
    """
    Test the rendering of various complex technical topics.
    """
    json_str = json.dumps(json_data)
    response = client.post("/render-magic", data={"data": json_str})

    assert response.status_code == 200
    assert json_data["title"] in response.text
    
    # Check for visual elements (SHAPE_IT characters)
    assert "═" in response.text or "─" in response.text
    
    # Check for keywords and content
    for kw in expected_keywords:
        assert kw in response.text
    
    assert json_data["sections"][0]["title"] in response.text
    print(f"\n✅ Test Passed: {topic} rendered successfully.")


if __name__ == "__main__":
    # Run the original C++ test if executed directly
    test_render_magic_endpoint()
