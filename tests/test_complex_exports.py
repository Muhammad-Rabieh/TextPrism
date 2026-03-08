import os
import time
import requests
import subprocess
import signal
import sys
import zipfile
from playwright.sync_api import sync_playwright, expect

# Config
BASE_URL = "http://localhost:8000"

# Dataset from user
EXAMPLES = {
    "ASCII": r"""
{
  "title": "Understanding Euclid’s Parallel Postulate (ASCII)",
  "explanation": "[compass] The parallel postulate is historically significant...",
  "explanation_keywords": ["compass", "map"],
  "sections": [
    {
      "title": "[compass] Original Statement",
      "content": "[road] Fifth postulate describes how lines behave...",
      "bullets": ["Appears as fifth postulate"]
    }
  ]
}
=== ASCII SECTION 1 ===
```text
        (TRANSVERSAL)
              |
--------------+----------------
      Line A           Line B
```
""",
    "MERMAID": r"""
{
  "title": "Parallel Postulate (Mermaid)",
  "explanation": "[vision] Detailed overall explanation...",
  "explanation_keywords": ["vision"],
  "sections": [
    {
      "title": "[pillar] The Fifth Postulate",
      "content": "[scroll] In classical geometry...",
      "bullets": ["axiom in Euclid"]
    }
  ]
}
=== CHART SECTION 1 ===
```mermaid
%% Leading comment to test detection robustness
flowchart TD
    A["Transversal Line"] --> B["Intersects Line 1"]
```
""",
    "SVG": r"""
{
  "title": "Parallel Postulate (SVG)",
  "explanation": "[compass] Foundational statements...",
  "explanation_keywords": ["compass"],
  "sections": [
    {
      "title": "[pillar] The Fifth Postulate",
      "content": "[scroll] In Euclid’s Elements...",
      "bullets": ["axiom 5"]
    }
  ]
}
=== CHART SECTION 1 ===
```xml
<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg">
  <line x1="10" y1="50" x2="190" y2="50" stroke="black" stroke-width="2"/>
</svg>
```
"""
}

def wait_for_server(url, timeout=15):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200: return True
        except: pass
        time.sleep(1)
    return False

def run_complex_e2e():
    print("🚀 Starting TextPrism server [Complex Tests]...")
    proc = subprocess.Popen(
        [sys.executable, "src/app.py"], 
        preexec_fn=os.setsid,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Give it a moment and then check if it's still running
        time.sleep(2)
        if proc.poll() is not None:
            out, err = proc.communicate()
            print(f"❌ Server died immediately!\nSTDOUT: {out}\nSTDERR: {err}")
            return

        if not wait_for_server(BASE_URL, timeout=20):
            out, err = proc.communicate(timeout=1)
            print(f"❌ Server timeout!\nSTDOUT: {out}\nSTDERR: {err}")
            raise RuntimeError("Server failed to start")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 800})
            
            for chart_type, test_data in EXAMPLES.items():
                print(f"🧪 Testing {chart_type} Rendering & Exports...")
                page = context.new_page()
                page.goto(BASE_URL)
                
                # Input and Process
                page.fill("#text-input", f"Complex {chart_type} Test")
                page.click("#magic-prompt-btn")
                page.wait_for_selector("#magic-prompt-modal", state="visible")
                page.fill("#ai-response-input", test_data)
                page.click("#process-ai-btn")
                
                # Wait for specific rendering
                page.wait_for_selector(".explanation-box", timeout=15000)
                
                if chart_type == "ASCII":
                    expect(page.locator(".ascii-box")).to_be_visible()
                elif chart_type == "MERMAID":
                    # Wait for Mermaid.js to process the div
                    page.wait_for_selector(".mermaid[data-processed='true']", timeout=15000)
                    expect(page.locator(".mermaid svg")).to_be_visible()
                elif chart_type == "SVG":
                    expect(page.locator(".svg-container svg")).to_be_visible()

                # Verify PDF (Check for PDF header)
                with page.expect_download() as download_info:
                    page.click("#download-pdf-btn")
                pdf_path = download_info.value.path()
                with open(pdf_path, "rb") as f:
                    assert f.read(4) == b"%PDF"
                
                # Verify Markdown
                with page.expect_download() as download_info:
                    page.click("#download-md-btn")
                zip_path = download_info.value.path()
                with zipfile.ZipFile(zip_path, 'r') as z:
                    md_name = [f for f in z.namelist() if f.endswith(".md")][0]
                    content = z.read(md_name).decode('utf-8')
                    if chart_type == "MERMAID": 
                        assert "```mermaid" in content
                        # Check for blank lines before AND after (join with \n in app.py + my markers)
                        assert "\n\n```mermaid\n" in content
                        assert "\n```\n\n" in content
                        
                        # Check for trailing padding inside the block
                        mermaid_lines = content.split("```mermaid")[1].split("```")[0].strip().splitlines()
                        for line in mermaid_lines:
                            if line.strip():
                                assert not line.endswith("  "), f"Line '{line}' has excessive padding"
                    
                    if chart_type == "SVG": 
                        assert "```xml" in content
                        assert "\n\n```xml\n" in content
                        assert "\n```\n\n" in content
                
                print(f"✅ {chart_type} verified.")
                page.close()

            browser.close()
            print("🎉 Complex E2E tests successful!")

    finally:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

if __name__ == "__main__":
    run_complex_e2e()
