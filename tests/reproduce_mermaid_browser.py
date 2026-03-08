
import os
import time
import requests
import subprocess
import signal
import sys
from playwright.sync_api import sync_playwright, expect

BASE_URL = "http://localhost:8000"

PAYLOAD = r"""
{
  "title": "Mermaid Test",
  "explanation": "Test",
  "sections": [
    {
      "title": "Section 1",
      "content": "Content",
      "bullets": []
    }
  ]
}

=== CHART SECTION 1 ===

flowchart TD

A[Start] --> B[End]
"""

def wait_for_server(url, timeout=15):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200: return True
        except: pass
        time.sleep(1)
    return False

def reproduce():
    print("🚀 Starting server...")
    proc = subprocess.Popen([sys.executable, "src/app.py"], preexec_fn=os.setsid)
    
    try:
        if not wait_for_server(BASE_URL):
            print("❌ Server failed to start")
            return
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Capture console logs
            page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.text}"))
            page.on("pageerror", lambda err: print(f"BROWSER ERROR: {err}"))
            
            page.goto(BASE_URL)
            page.fill("#text-input", "Mermaid Repro")
            page.click("#magic-prompt-btn")
            page.wait_for_selector("#magic-prompt-modal", state="visible")
            page.fill("#ai-response-input", PAYLOAD)
            page.click("#process-ai-btn")
            
            # Wait for content to render
            page.wait_for_selector(".explanation-box")
            
            # Check for mermaid div
            mermaid_div = page.locator(".mermaid")
            if mermaid_div.count() == 0:
                print("❌ Mermaid div NOT found in DOM")
            else:
                print("✅ Mermaid div found in DOM")
                # Wait a bit for Mermaid.js to process
                time.sleep(3)
                
                # Check for data-processed attribute
                attr = mermaid_div.get_attribute("data-processed")
                print(f"Mermaid data-processed: {attr}")
                
                # Check for SVG inside
                has_svg = mermaid_div.locator("svg").count() > 0
                print(f"Mermaid contains SVG: {has_svg}")
                
                # Log the content of the div
                raw_html = page.evaluate("el => el.innerHTML", mermaid_div.element_handle())
                print(f"Raw innerHTML: {raw_html!r}")
                
                # Check the whole page content for the chart string
                full_content = page.content()
                if "flowchart TD" in full_content:
                    start = full_content.find("flowchart TD")
                    print(f"Source snippet: {full_content[start:start+100]!r}")
                
                if "--&gt;" in raw_html:
                    print("❌ HTML is STILL ESCAPED")
                elif "-->" in raw_html:
                    print("✅ HTML is NOT ESCAPED")
                
                # Check for mermaid errors in console if possible
                # (Simple check: is there a div with error class?)
                if page.locator(".mermaid svg").count() == 0:
                     print("Checking for error message in div...")
                     print(f"Text content: {mermaid_div.text_content()!r}")

            browser.close()

    finally:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

if __name__ == "__main__":
    reproduce()
