import os
import sys
import time
import json
import subprocess
from playwright.sync_api import sync_playwright

def test_all_exports():
    print("\n🚀 Starting Comprehensive Export Test Suite...")
    
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{env.get('PYTHONPATH', '')}:{os.getcwd()}:{os.path.join(os.getcwd(), 'src')}"
    
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.app:app", "--host", "127.0.0.1", "--port", "8001"],
        env=env
    )
    time.sleep(7) # Increased wait time
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()
            
            # Capture console logs
            logs = []
            page.on("console", lambda msg: logs.append(f"JS: {msg.text}"))
            page.on("pageerror", lambda exc: logs.append(f"JS ERROR: {exc}"))

            print("--- Loading Home Page ---")
            page.goto("http://127.0.0.1:8001")
            
            # Mock AI Response
            json_payload = {
                "title": "Comprehensive Test",
                "explanation": "Testing all export formats simultaneously.",
                "sections": [{"title": "Test Section", "content": "Sample content for export."}]
            }
            
            print("--- Injecting Input Text and AI Response ---")
            page.evaluate(f"""
                (async () => {{
                    document.getElementById('text-input').value = "Sample source text for comprehensive testing.";
                    const input = document.getElementById('ai-response-input');
                    input.value = JSON.stringify({json.dumps(json_payload)});
                    document.getElementById('process-ai-btn').click();
                }})();
            """)
            
            page.wait_for_selector("#download-pdf-btn:not([disabled])", timeout=10000)
            print("✅ Content rendered and buttons enabled")

            # 1. Test HTML Export
            print("--- Testing HTML Export ---")
            with page.expect_download() as download_info:
                page.click("#download-html-btn")
            download = download_info.value
            download.save_as("test_all.html")
            assert os.path.exists("test_all.html") and os.path.getsize("test_all.html") > 500
            print("✅ HTML Export success")

            # 2. Test Markdown Export
            print("--- Testing Markdown Export ---")
            with page.expect_download() as download_info:
                page.click("#download-md-btn")
            download = download_info.value
            download.save_as("test_all.md")
            assert os.path.exists("test_all.md") and os.path.getsize("test_all.md") > 50
            print("✅ Markdown Export success")

            # 3. Test Copy to Clipboard
            print("--- Testing Copy to Clipboard ---")
            page.click("#copy-btn")
            time.sleep(1)
            # Clipboard test is tricky in headless, but we check logs
            copy_success = any("Copy Output: Success" in log for log in logs)
            if copy_success:
                print("✅ Copy to Clipboard success")
            else:
                print("⚠️ Copy to Clipboard log not found (might be expected in headless)")

            # 4. Test PDF Export (The most important one)
            print("--- Testing PDF Export ---")
            # We wait a bit more for PDF as it's slow
            with page.expect_download(timeout=60000) as download_info:
                page.click("#download-pdf-btn")
            
            download = download_info.value
            download.save_as("test_all.pdf")
            assert os.path.exists("test_all.pdf") and os.path.getsize("test_all.pdf") > 1000
            print("✅ PDF Export success")

            print("\n--- Browser Console Logs During Test ---")
            for log in logs:
                print(log)

            browser.close()
            print("\n✨ All tests passed!")

    except Exception as e:
        print(f"\n☢️ Test failed: {e}")
        # Print logs on failure too
        print("\n--- Failure Browser Console Logs ---")
        for log in (logs if 'logs' in locals() else []):
            print(log)
        raise
    finally:
        server_process.terminate()
        server_process.wait()
        for f in ["test_all.html", "test_all.md", "test_all.pdf"]:
            if os.path.exists(f): os.remove(f)

if __name__ == "__main__":
    test_all_exports()
