import json
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_render_magic_endpoint():
    """
    Test the /render-magic endpoint with the C++ Templates JSON.
    This verifies that the backend can parse the AI-generated structure
    and return a valid HTML response with visual elements.
    """
    cpp_templates_json = {
        "title": "The Blueprint of C++ Templates",
        "summary": "C++ templates are a powerful feature used to write generic, reusable code across three primary functional areas.",
        "sections": [
            {
                "title": "The Power of Generics",
                "content": "Templates act as a 'cookie cutter' for code, allowing you to write a single function or class that works with any data type without rewriting it.",
                "keywords": ["generic", "blueprint", "reusability", "adaptability"],
                "bullets": [
                    "Write Once, Use Everywhere: Create a single logic flow that adapts to different inputs.",
                    "Zero Duplication: Eliminates the need to copy-paste code just to change a variable type."
                ]
            },
            {
                "title": "Safety and Customization",
                "content": "Unlike older programming methods, templates are checked by the compiler for errors and can be 'specialized' to behave differently for specific types.",
                "keywords": ["security", "compiler", "logic", "customization"],
                "bullets": [
                    "Type Safety: The compiler ensures your data types match, preventing common crashes.",
                    "Template Specialization: You can create a 'custom version' of a template for a unique data type if the general logic doesn't fit."
                ]
            },
            {
                "title": "The Foundation of Modern C++",
                "content": "Templates are the engine behind the Standard Template Library (STL), providing the most common tools developers use daily.",
                "keywords": ["engine", "storage", "algorithm", "utility"],
                "bullets": [
                    "Smart Containers: Powers objects like std::vector and std::map that store your data efficiently.",
                    "Universal Algorithms: Enables sorting and searching functions that work across any collection of data."
                ]
            }
        ]
    }

    # Convert to JSON string
    json_str = json.dumps(cpp_templates_json)

    # Post to the endpoint
    response = client.post("/render-magic", data={"data": json_str})

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
        "summary": "Decorators are a powerful way to modify function behavior without changing source code.",
        "sections": [
            {
                "title": "The Wrapper Concept",
                "content": "A decorator is a function that takes another function and extends its behavior while wrapping it.",
                "keywords": ["wrap", "gift", "layer", "logic"],
                "bullets": ["Wraps existing functions", "Executed at definition time"]
            },
            {
                "title": "Metaprogramming Power",
                "content": "They allow developers to write 'code that writes code', abstracting repetitive tasks.",
                "keywords": ["magic", "brain", "code", "automation"],
                "bullets": ["Logging automation", "Authentication guards"]
            }
        ]
    }, ["wrap", "magic", "brain"]),
    ("Rust Ownership", {
        "title": "Rust Ownership: Memory Safety Rules",
        "summary": "Ownership ensures memory safety without a garbage collector via a strict set of rules.",
        "sections": [
            {
                "title": "Ownership Rules",
                "content": "Each value has one owner. When the owner goes out of scope, the value is dropped.",
                "keywords": ["law", "master", "control", "safety"],
                "bullets": ["One owner at a time", "Scope-based cleanup"]
            },
            {
                "title": "Borrowing & References",
                "content": "Data can be lent via references (&) following the 'one writer or many readers' rule.",
                "keywords": ["lend", "share", "temporary", "link"],
                "bullets": ["Immutable references", "Mutable references"]
            }
        ]
    }, ["law", "lend", "safety"])
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
