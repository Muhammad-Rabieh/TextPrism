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
        if r.status_code != 200:
            print(f"❌ Server returned status {r.status_code}")
            sys.exit(1)
            
        html = r.text
        
        # Check for Base64 data URIs
        # Standard icon src in TextPrism: data:image/...;base64,...
        base64_pattern = re.compile(r'src="data:image\/[^;]+;base64,')
        matches = base64_pattern.findall(html)
        
        print(f"Found {len(matches)} Base64 embedded icons.")
        
        if len(matches) < 4: 
            print(f"❌ Insufficient Base64 icons found (expected at least 4, found {len(matches)})")
            print("--- HTML SNIPPET (END) ---")
            print(html[-3000:]) # Show body content
            sys.exit(1)
            
        # Also check that there are NO relative paths to /icons/ or /clipart/ in img tags
        relative_pattern = re.compile(r'<img[^>]+src="/(icons|clipart)/')
        rel_matches = relative_pattern.findall(html)
        
        if rel_matches:
            print(f"❌ Found {len(rel_matches)} non-embedded relative icon paths: {rel_matches}")
            sys.exit(1)
            
        print("✅ PASS: All icons are successfully embedded as Base64.")
        sys.exit(0)
        
    except Exception as e:
        print(f"☢️ Error during test: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_base64_embedding()
