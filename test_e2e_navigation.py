import time
import json
from playwright.sync_api import sync_playwright

# Sample Text to simulate user input
SAMPLE_INPUT = """
A template is a tool for building generic classes or functions.
It lets the same logic adapt to any data type without rewriting the code.
Templates remove repeated code by allowing one function or class to handle many types.
"""

# Sample Phase 1 LLM Output (Distilled Markdown)
PHASE_1_OUTPUT = """
# C++ Templates Explained

## The Generic Blueprint
- A template is a tool for building generic classes or functions.
- It lets the same logic adapt to any data type without rewriting the code.

## One Definition, Zero Duplication
- Templates remove repeated code by allowing one function or class to handle many types.
"""

# Sample Phase 2 LLM Output (Hybrid JSON + ASCII)
PHASE_2_OUTPUT = """```json
{
  "title": "C++ Templates Explained",
  "summary": "Templates are blueprints for generic code.",
  "summary_keywords": ["blueprint", "recycle"],
  "sections": [
    {
      "title": "The Generic Blueprint",
      "sentences": [
        {
          "text": "A template is a tool for building generic classes or functions.",
          "keyword": "wrench"
        },
        {
          "text": "It lets the same logic adapt to any data type without rewriting the code.",
          "keyword": "layers"
        }
      ],
      "bullets": [
        "Create flexible functions.",
        "Create reusable classes."
      ]
    },
    {
      "title": "One Definition, Zero Duplication",
      "sentences": [
        {
          "text": "Templates remove repeated code by allowing one function.",
          "keyword": "safety"
        }
      ],
      "bullets": [
        "Eliminate multiple nearly identical functions.",
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

        print("🖱️ Step 2: Clicking 'Summarize & Map with AI'...")
        page.click("#magic-prompt-btn")

        print("⏳ Waiting for Phase 1 Modal...")
        page.wait_for_selector("#magic-prompt-modal", state="visible")
        time.sleep(1)

        print("📋 Step 3: Simulating user copying the Phase 1 Prompt...")
        page.click("#copy-phase1-btn")
        time.sleep(1)

        print("✍️ Step 4: Pasting simulated 1st AI result (Distilled Outline)...")
        page.fill("#distilled-text-input", PHASE_1_OUTPUT)
        time.sleep(1)

        print("🖱️ Step 5: Moving to Next step (Semantic Mapping)...")
        page.click("#goto-phase2-btn")

        print("⏳ Waiting for Phase 2 panel to render...")
        page.wait_for_selector("#phase2-container", state="visible")
        time.sleep(1)

        print("📋 Step 6: Simulating user copying the Phase 2 Prompt...")
        page.click("#copy-phase2-btn")
        time.sleep(1)

        print("✍️ Step 7: Pasting simulated 2nd AI result (Hybrid JSON+ASCII)...")
        page.fill("#ai-response-input", PHASE_2_OUTPUT)
        time.sleep(1)

        print("🎨 Step 8: Hitting the final 'Build Visual Explanation' button!")
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
