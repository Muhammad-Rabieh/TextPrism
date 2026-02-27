import time
import json
from playwright.sync_api import sync_playwright

# Sample Text to simulate user input
SAMPLE_INPUT = """
A template is a tool for building generic classes or functions.
It lets the same logic adapt to any data type without rewriting the code.
Templates remove repeated code by allowing one function or class to handle many types.
"""

# Sample Single-Phase AI Response (Hybrid JSON + ASCII)
SINGLE_PHASE_OUTPUT = """```json
{
  "title": "C++ Templates Explained",
  "explanation": "[vision] Templates are blueprints for generic code.",
  "explanation_keywords": ["blueprint", "recycle"],
  "sections": [
    {
      "title": "The Generic Blueprint",
      "content": "[wrench] A template is a tool for building generic classes. [layers] It lets the logic adapt to any data type.",
      "bullets": [
        "Create flexible functions.",
        "Create reusable classes."
      ]
    },
    {
      "title": "Zero Duplication",
      "content": "[safety] Templates remove repeated code by allowing one function handle many types.",
      "bullets": [
        "Eliminate nearly identical functions.",
        "Keep source code compact."
      ]
    }
  ]
}
```

=== ASCII SECTION 1 ===
```text
┌──────────────────────────────┐
│        TEMPLATE = MOLD       │
│   One Pattern → Many Types   │
└──────────────────────────────┘
```

=== ASCII SECTION 2 ===
```text
 Without Templates              With Templates
 ┌───────────────┐             ┌────────────────┐
 │ func_int      │             │   func<T>      │
 │ func_float    │   ─────▶    │  One Generic   │
 │ func_double   │             │    Function    │
 └───────────────┘             └────────────────┘
```
"""



def test_e2e_user_journey():
    with sync_playwright() as p:
        print("🚀 Launching browser...")
        browser = p.chromium.launch(headless=False) # Keep true to see it visually!
        page = browser.new_page()

        print("🌐 Navigating to TextPrism Data App...")
        page.goto("http://localhost:8000")
        page.wait_for_selector("#main-header")

        print("📝 Step 1: Inserting document text...")
        page.fill("#text-input", SAMPLE_INPUT)
        time.sleep(1) # Visual pauses

        print("🖱️ Step 2: Clicking 'Explain & Map with AI'...")
        page.click("#magic-prompt-btn")

        print("⏳ Waiting for Magic Modal...")
        page.wait_for_selector("#magic-prompt-modal", state="visible")
        time.sleep(1)

        print("📋 Step 3: Simulating user copying the Unified Prompt...")
        page.click("#copy-magic-btn")
        time.sleep(1)

        print("✍️ Step 4: Pasting simulated AI response (Hybrid JSON+ASCII)...")
        page.fill("#ai-response-input", SINGLE_PHASE_OUTPUT)
        time.sleep(1)

        print("🎨 Step 5: Hitting the final 'Build Visual Explanation' button!")
        page.click("#process-ai-btn")


        print("⏳ Waiting for the UI to process the request and render output...")
        # The frontend script strips .explanation-wrapper and inserts its inner HTML
        page.wait_for_selector("#output-content .title-section", timeout=10000)
        
        print("✅ Output successfully detected! User Journey Navigation is working.")
        time.sleep(3) # Leave screen open so you can see it

        print("📸 Taking a screenshot of the final output...")
        page.screenshot(path="e2e_test_success.png", full_page=True)

        print("🛑 Closing browser.")
        browser.close()

if __name__ == "__main__":
    print("====================================")
    print("  TextPrism Playwright E2E Test     ")
    print("====================================")
    try:
        test_e2e_user_journey()
        print("\n🎉 All tests passed smoothly!")
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
