
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
  "title": "Parallel Postulate",
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
A --> B
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

def verify_naming():
    print("🚀 Starting server...")
    proc = subprocess.Popen([sys.executable, "src/app.py"], preexec_fn=os.setsid)
    
    try:
        if not wait_for_server(BASE_URL):
            print("❌ Server failed to start")
            return
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            page.goto(BASE_URL)
            
            # Select Mermaid first
            page.click(".format-option[data-value='mermaid']")
            
            page.fill("#text-input", "Parallel Postulate")
            page.click("#magic-prompt-btn")
            page.wait_for_selector("#magic-prompt-modal", state="visible")
            page.fill("#ai-response-input", PAYLOAD)
            page.click("#process-ai-btn")
            
            # Wait for content
            page.wait_for_selector(".explanation-box")
            
            print("🧪 Verifying HTML Download Name...")
            with page.expect_download() as download_info:
                page.click("#download-html-btn")
            download = download_info.value
            print(f"Suggested HTML filename: {download.suggested_filename}")
            if "_MERMAID.html" in download.suggested_filename:
                print("✅ HTML suffix correct.")
            else:
                print("❌ HTML suffix WRONG.")

            print("🧪 Verifying MD Zip Download Name...")
            with page.expect_download() as download_info:
                page.click("#download-md-btn")
            download = download_info.value
            print(f"Suggested ZIP filename: {download.suggested_filename}")
            if "_MERMAID.zip" in download.suggested_filename:
                print("✅ ZIP suffix correct.")
            else:
                print("❌ ZIP suffix WRONG.")

            # Test switching to SVG
            page.click(".format-option[data-value='svg']")
            print("🧪 Verifying SVG suffix after switch...")
            with page.expect_download() as download_info:
                page.click("#download-html-btn")
            download = download_info.value
            print(f"Suggested SVG HTML filename: {download.suggested_filename}")
            if "_SVG.html" in download.suggested_filename:
                print("✅ SVG suffix correct.")
            else:
                print("❌ SVG suffix WRONG.")

            browser.close()

    finally:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

if __name__ == "__main__":
    verify_naming()
