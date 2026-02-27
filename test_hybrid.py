import requests
import re
from fastapi.testclient import TestClient
from app import app
import builtins

client = TestClient(app)

hybrid_payload = """
Sure! Here is the mapped visual explanation:

```json
{
  "title": "Computer Networks",
  "summary": "Networks connect computers together.",
  "summary_keywords": ["globe", "network"],
  "sections": [
    {
      "title": "Local Area Network",
      "sentences": [
        {
          "text": "A LAN connects computers in a small area.",
          "keyword": "office"
        }
      ],
      "bullets": ["Fast", "Private"]
    },
    {
      "title": "Wide Area Network",
      "sentences": [
        {
          "text": "A WAN spans large geographical distances.",
          "keyword": "earth"
        }
      ],
      "bullets": ["Slower", "Public"]
    }
  ]
}
```

=== ASCII SECTION 1 ===
  +-------+    +-------+
  | PC 1  |----| PC 2  |
  +-------+    +-------+

=== ASCII SECTION 2 ===
    ___
  /     \  
 | World |
  \ ___ /
"""

response = client.post("/render-magic", data={"data": hybrid_payload})
print(f"Status: {response.status_code}")
if response.status_code == 200:
    html = response.text
    if "PC 1" in html and "World" in html and "Local Area Network" in html:
        print("✅ Success: JSON and ASCII blocks both rendered!")
    else:
        print("❌ HTML did not contain expected content.")
        if "PC 1" not in html: print("  Missing ASCII 1")
        if "World" not in html: print("  Missing ASCII 2")
        if "Local Area Network" not in html: print("  Missing JSON content")
else:
    print(f"Error: {response.text}")
