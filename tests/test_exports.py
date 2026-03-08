#!/usr/bin/env python3
import os
import time
import json
import subprocess
import requests
from playwright.sync_api import sync_playwright

def test_markdown_export():
    print("\n--- Testing Markdown Export ---")
    url = "http://127.0.0.1:8000/export-md"
    payload = "This is a test document about Python and AI."
    
    try:
        response = requests.post(url, data={"text": payload})
        assert response.status_code == 200, f"Markdown export failed with status {response.status_code}"
        
        output_file = "test_output.zip"
        with open(output_file, "wb") as f:
            f.write(response.content)
        
        assert os.path.exists(output_file), f"{output_file} was not created"
        assert os.path.getsize(output_file) > 10, f"{output_file} is too small"
        print(f"✅ Markdown export verified on disk: {output_file}")
    except Exception as e:
        print(f"❌ Markdown test failed: {e}")
        raise

def test_full_flow_pdf_export():
    print("\n--- Testing Full Flow PDF Export (Home Page) ---")
    with sync_playwright() as p:
        try:
            # Slow mo to ensure animations/renders finish
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()
            
            # Capture console logs
            page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.text}"))
            page.on("pageerror", lambda exc: print(f"BROWSER ERROR: {exc}"))

            # 1. Load Home Page
            page.goto("http://127.0.0.1:8000")
            
            # 2. Verify all buttons exist but are disabled
            print("Verifying initial button states...")
            assert page.is_disabled("#download-pdf-btn")
            assert page.is_disabled("#download-html-btn")
            assert page.is_disabled("#download-md-btn")
            assert "PDF" in page.text_content("#download-pdf-btn")
            assert "MD" in page.text_content("#download-md-btn")
            
            # 3. Simulate AI Response injection (like script.js does)
            json_payload = {
                "title": "Home Page Integration Test",
                "explanation": "Testing PDF visibility next to HTML and MD.",
                "sections": [{"title": "Test Section", "content": "Content"}]
            }
            
            print("Injecting AI response via prompt modal simulation...")
            page.evaluate(f"""
                (async () => {{
                    const input = document.getElementById('ai-response-input');
                    input.value = JSON.stringify({json.dumps(json_payload)});
                    document.getElementById('process-ai-btn').click();
                }})();
            """)
            
            # Wait for render to finish and buttons to enable
            page.wait_for_selector("#download-pdf-btn:not([disabled])", timeout=10000)
            
            print("Verifying buttons enabled after render...")
            pdf_btn_text = page.text_content("#download-pdf-btn")
            print(f"PDF Button Text: '{pdf_btn_text.strip()}'")
            assert "PDF" in pdf_btn_text
            
            # Take a screenshot to see the layout
            page.screenshot(path="debug_layout.png")
            print("Screenshot saved to debug_layout.png")
            
            # 4. Trigger PDF Download
            print("Triggering PDF export from home page action bar...")
            with page.expect_download() as download_info:
                page.click("#download-pdf-btn")
                
            download = download_info.value
            path = "home_test_output.pdf"
            download.save_as(path)
            
            assert os.path.exists(path), f"{path} was not created"
            assert os.path.getsize(path) > 1000, "PDF looks corrupted or empty"
            print(f"✅ Home page PDF export verified: {path}")
            
            browser.close()
        except Exception as e:
            print(f"❌ Full flow PDF test failed: {e}")
            raise

if __name__ == "__main__":
    print("🚀 Starting export test suite (Home Page focus)...")
    
    server_process = subprocess.Popen(
        ["python3", "-m", "uvicorn", "src.src.app:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    time.sleep(5)
    
    try:
        test_markdown_export()
        test_full_flow_pdf_export()
        print("\n✨ All integrated export tests passed!")
    except Exception as e:
        print(f"\n☢️ Test suite failed: {e}")
    finally:
        print("Cleaning up...")
        server_process.terminate()
        server_process.wait()
        if os.path.exists("test_output.zip"): os.remove("test_output.zip")
        if os.path.exists("home_test_output.pdf"): os.remove("home_test_output.pdf")
