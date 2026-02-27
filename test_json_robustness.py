import json
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_messy_ai_output():
    """
    Test that the backend correctly extracts JSON even when 
    surrounded by conversational noise and ASCII art.
    """
    print("\n--- Testing Robust JSON Extraction from Messy Output ---")
    
    messy_payload = """
Sure! Here is the visual explanation for Python Decorators:

{
  "title": "Python Decorators",
  "explanation": "[magic] Decorators allow you to wrap functions and [rocket] extend their behavior.",
  "sections": [
    {
      "title": "[gift] Wrapper Pattern",
      "content": "[ribbon] A decorator takes a function and returns a new one. [box] This adds functionality without changing code.",
      "bullets": ["Syntactic sugar", "Code reuse"],
    }
  ],
}

And here is some ASCII art for you:
== ASCII SECTION 1 ==
  +-------+
  | Gift  |
  +-------+
"""
    
    # Post to API
    response = client.post("/render-magic", data={"data": messy_payload})
    
    # Assert successful render
    if response.status_code == 200:
        print("✅ Successfully parsed messy output with conversational noise and trailing commas!")
    else:
        print(f"❌ Failed to parse messy output. Status: {response.status_code}")
        print(f"Response: {response.text}")
        assert False

if __name__ == "__main__":
    test_messy_ai_output()
