import time
import subprocess
from playwright.sync_api import sync_playwright

def debug_layout():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto("http://127.0.0.1:8010")
        
        page.fill("#text-input", "Test text")
        print("Clicking magic prompt button...")
        page.click("#magic-prompt-btn")
        page.wait_for_selector("#magic-prompt-modal", state="visible")
        
        # Get bounding boxes
        label_box = page.locator("label[for='ai-response-input']").bounding_box()
        paste_btn_box = page.locator("#paste-ai-btn").bounding_box()
        wrapper_box = page.locator(".ai-input-wrapper").bounding_box()
        textarea_box = page.locator("#ai-response-input").bounding_box()
        
        print("=== LAYOUT METRICS ===")
        print(f"Wrapper: {wrapper_box}")
        print(f"Label: {label_box}")
        print(f"Paste Btn: {paste_btn_box}")
        print(f"Textarea: {textarea_box}")
        
        # Let's check computed styles
        flex_container_display = page.evaluate('window.getComputedStyle(document.querySelector("#paste-ai-btn").parentElement).display')
        flex_container_justify = page.evaluate('window.getComputedStyle(document.querySelector("#paste-ai-btn").parentElement).justifyContent')
        
        print("\n=== STYLES ===")
        print(f"Container Display: {flex_container_display}")
        print(f"Container Justify: {flex_container_justify}")
        
        # Take a screenshot
        page.screenshot(path="debug_paste_layout.png")
        print("\nScreenshot saved to debug_paste_layout.png")
        
        browser.close()

if __name__ == "__main__":
    debug_layout()
