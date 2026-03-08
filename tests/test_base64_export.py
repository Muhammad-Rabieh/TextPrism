import requests
import sys
import os
import re

def test_base64_embedding():
    print("--- Testing Base64 Asset Embedding ---")
    
    # Simple Magic Prompt payload
    payload = {
        "data": """
{
  "title": "[rocket] Portability Test",
  "explanation": "[shield] This is a test of Base64 embedding.",
  "sections": [
    {
      "title": "[gear] Section One",
      "content": "[package] Every icon should be embedded."
    }
  ]
}
"""
    }
    
    try:
        r = requests.post("http://127.0.0.1:8000/render-magic", data=payload)
        assert r.status_code == 200, f"Server returned status {r.status_code}"
            
        html = r.text
        
        # Check for Base64 data URIs
        # Standard icon src in TextPrism: data:image/...;base64,...
        base64_pattern = re.compile(r'src="data:image\/[^;]+;base64,')
        matches = base64_pattern.findall(html)
        
        print(f"Found {len(matches)} Base64 embedded icons.")
        
        if len(matches) < 4: 
            print("--- HTML SNIPPET (END) ---")
            print(html[-3000:]) # Show body content
            assert False, f"Insufficient Base64 icons found (expected at least 4, found {len(matches)})"
            
        # Also check that there are NO relative paths to /icons/ or /clipart/ in img tags
        relative_pattern = re.compile(r'<img[^>]+src="/(icons|clipart)/')
        rel_matches = relative_pattern.findall(html)
        
        assert not rel_matches, f"Found {len(rel_matches)} non-embedded relative icon paths: {rel_matches}"
        
        print("✅ PASS: All icons are successfully embedded as Base64.")
        
    except requests.exceptions.ConnectionError:
        print("Server not running on port 8000. Skipping live test.")
    except Exception as e:
        assert False, f"Error during test: {e}"

if __name__ == "__main__":
    test_base64_embedding()
