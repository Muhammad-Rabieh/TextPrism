import os
import time
import requests
import subprocess
import signal
import sys
from playwright.sync_api import sync_playwright, expect

# Config
BASE_URL = "http://localhost:8000"
TEST_TEXT = r"""
{
  "title": "E2E Export Test",
  "explanation": "[test] Verifying that ASCII, Mermaid, and SVG work across all exports.",
  "explanation_keywords": ["test", "verification"],
  "sections": [
    {
      "title": "[box] ASCII Section",
      "content": "[code] This section contains an ASCII box.",
      "bullets": ["Check alignment", "Check borders"]
    },
    {
      "title": "[share] Mermaid Section",
      "content": "[graph] This section contains a Mermaid diagram.",
      "bullets": ["Check nodes", "Check edges"]
    },
    {
      "title": "[paint-brush] SVG Section",
      "content": "[art] This section contains a raw SVG chart.",
      "bullets": ["Check paths", "Check colors"]
    }
  ]
}

=== CHART SECTION 1 ===
```text
+-----------+
| ASCII BOX |
+-----------+
```

=== CHART SECTION 2 ===
```mermaid
graph TD
    A[Start] --> B[Process]
    B --> C[End]
```

=== CHART SECTION 3 ===
```svg
<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="40" stroke="green" stroke-width="4" fill="yellow" />
</svg>
```
"""

def wait_for_server(url, timeout=15):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except requests.ConnectionError:
            pass
        time.sleep(1)
    return False

def run_e2e_test():
    # Start server
    print("🚀 Starting TextPrism server...")
    proc = subprocess.Popen([sys.executable, "src/app.py"], preexec_fn=os.setsid)
    
    try:
        if not wait_for_server(BASE_URL):
            raise RuntimeError("Server failed to start in time")
        
        print("✅ Server is up. Starting Playwright tests...")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(BASE_URL)

            # 1. Trigger Magic Prompt Workflow
            print("📝 Injecting test content...")
            # Fill main text input first, or the button will just focus it
            page.fill("#text-input", "Triggering E2E test")
            page.click("#magic-prompt-btn")
            page.wait_for_selector("#magic-prompt-modal", state="visible")
            
            # Paste the test content into the modal's input
            page.fill("#ai-response-input", TEST_TEXT)
            page.click("#process-ai-btn")
            
            # Wait for rendering to complete
            page.wait_for_selector(".explanation-box", timeout=15000)

            # 2. Verify Rendering
            print("🔍 Verifying rendering...")
            # Check ASCII
            expect(page.locator(".ascii-box").first).to_contain_text("ASCII BOX")
            
            # Check Mermaid
            expect(page.locator(".mermaid")).to_be_visible()
            
            # Check SVG
            expect(page.locator(".svg-container svg circle")).to_be_visible()
            print("✅ Rendering verified (ASCII, Mermaid, SVG)")

            # 3. Verify HTML Export
            print("💾 Testing HTML Export...")
            with page.expect_download() as download_info:
                page.click("#download-html-btn")
            download = download_info.value
            path = download.path()
            with open(path, "r") as f:
                html_content = f.read()
                assert "E2E Export Test" in html_content
                assert "ASCII BOX" in html_content
                assert "mermaid" in html_content
                assert "<svg" in html_content
            print(f"✅ HTML Export verified: {download.suggested_filename}")

            # 4. Verify Markdown Export
            print("💾 Testing Markdown Export...")
            with page.expect_download() as download_info:
                page.click("#download-md-btn")
            download = download_info.value
            path = download.path()
            import zipfile
            with zipfile.ZipFile(path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                md_file = [f for f in file_list if f.endswith(".md")][0]
                with zip_ref.open(md_file) as f:
                    md_content = f.read().decode('utf-8')
                    assert "E2E Export Test" in md_content
                    assert "ASCII BOX" in md_content
                    assert "```mermaid" in md_content
                    assert "```xml" in md_content
            print(f"✅ Markdown Export verified: {download.suggested_filename}")

            # 5. Verify PDF Export
            print("💾 Testing PDF Export...")
            with page.expect_download() as download_info:
                page.click("#download-pdf-btn")
            download = download_info.value
            path = download.path()
            with open(path, "rb") as f:
                header = f.read(4)
                assert header == b"%PDF"
            print(f"✅ PDF Export verified: {download.suggested_filename}")

            browser.close()
            print("🎉 All E2E tests passed!")

    finally:
        # Shutdown server
        print("🛑 Shutting down server...")
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

if __name__ == "__main__":
    try:
        run_e2e_test()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
