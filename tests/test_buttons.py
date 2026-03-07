import os
import time
import subprocess
from playwright.sync_api import sync_playwright

def test_buttons_functionality():
    print("\n🚀 Starting Comprehensive Button Functionality Test...")
    
    # 1. Start Server
    server_process = subprocess.Popen(
        ["python3", "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8006"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(5)
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(permissions=['clipboard-read', 'clipboard-write'])
            page = context.new_page()
            
            print("--- Loading Home Page ---")
            page.goto("http://127.0.0.1:8006")
            
            # Test Initial State
            print("--- Checking Initial Button States ---")
            assert page.is_enabled("#magic-prompt-btn")
            assert page.is_enabled("#clear-btn")
            assert page.is_enabled("#paste-main-btn"), "Main paste button should be visible"
            assert page.is_disabled("#download-html-btn")
            assert page.is_disabled("#download-pdf-btn")
            assert page.is_disabled("#download-md-btn")
            assert page.is_disabled("#copy-btn")
            print("✅ Initial states correct")

            # Test Main Page Paste Button
            print("--- Testing Main Page Paste Button ---")
            mock_doc_text = "Hello from Clipboard"
            page.click("#paste-main-btn")
            page.evaluate("""
                (text) => {
                    const overlay = document.querySelector('#paste-main-btn textarea');
                    const dt = new DataTransfer();
                    dt.setData('text/plain', text);
                    const event = new ClipboardEvent('paste', { clipboardData: dt, bubbles: true, cancelable: true });
                    overlay.dispatchEvent(event);
                }
            """, mock_doc_text)
            page.wait_for_function('document.getElementById("text-input").value !== ""', timeout=3000)
            assert page.input_value("#text-input") == mock_doc_text, "Main paste button did not populate text-input"
            print("✅ Main page Paste button functional")

            # Fill some text for clear button test
            page.fill("#text-input", "Sample text for testing clear button.")
            
            # Test Clear Button
            print("--- Testing Clear Button ---")
            # We want to see if the page URL changes or if it reloads unexpectedly
            current_url = page.url
            page.click("#clear-btn")
            
            # Check if input is cleared
            input_val = page.input_value("#text-input")
            assert input_val == "", f"Expected empty input after clear, got: {input_val}"
            
            # Check if URL changed (it shouldn't if preventDefault or type=button is correct)
            if page.url != current_url:
                print(f"⚠️ URL changed from {current_url} to {page.url}. This indicates a form submission!")
            
            # Check if paste buttons are reset
            paste_val = page.locator("#paste-main-btn").inner_text()
            assert "Paste" in paste_val, f"Expected Paste button text to be reset, got: {paste_val}"
            
            # Check if placeholder is restored
            assert page.is_visible(".output-placeholder")
            print("✅ Clear button functional (including Paste reset)")

            # Test Magic Prompt Modal
            print("--- Testing Magic Prompt Button ---")
            page.fill("#text-input", "Text for magic prompt")
            page.click("#magic-prompt-btn")
            page.wait_for_selector("#magic-prompt-modal", state="visible", timeout=10000)
            assert page.is_visible("#magic-prompt-modal")
            assert page.is_visible("#copy-magic-btn"), "Copy Prompt button not visible"
            assert page.is_visible("#paste-ai-btn"), "Paste AI Response button not visible"
            
            # Test Paste functionality (Overlay approach)
            print("--- Testing Paste Button ---")
            mock_ai_response = "TestResponseText"
            # Click the button to open/focus the overlay
            page.click("#paste-ai-btn")
            # Dispatch a real ClipboardEvent on the overlay (which has focus)
            page.evaluate("""
                (text) => {
                    const overlay = document.querySelector('#paste-ai-btn textarea');
                    const dt = new DataTransfer();
                    dt.setData('text/plain', text);
                    const event = new ClipboardEvent('paste', { clipboardData: dt, bubbles: true, cancelable: true });
                    overlay.dispatchEvent(event);
                }
            """, mock_ai_response)
            # Check if the main textarea was populated
            page.wait_for_function('document.getElementById("ai-response-input").value !== ""', timeout=3000)
            actual_value = page.input_value("#ai-response-input")
            assert actual_value == mock_ai_response, f"Paste button did not populate textarea. Got: '{actual_value}'"
            
            # Close it
            page.click("#magic-modal-close")
            assert not page.is_visible("#magic-prompt-modal")
            print("✅ Magic Prompt modal functional")

            browser.close()
            print("✨ All button functionality tests PASSED!")

    except Exception as e:
        print(f"\n☢️ Button Functionality Test failed: {e}")
        raise
    finally:
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    test_buttons_functionality()
