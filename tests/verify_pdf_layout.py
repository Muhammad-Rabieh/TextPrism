import asyncio
from playwright.async_api import async_playwright
import os

async def verify_pdf_layout():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 1. Navigate to the app
        await page.goto("http://127.0.0.1:8000")
        
        # 2. Close initial modal if present
        try:
            await page.click("button:has-text('Explain'), .magic-modal-close", timeout=2000)
        except:
            pass
            
        # 3. Paste very long text to force page breaks
        long_text = "\n\n".join([f"Section {i}: This is a long paragraph of text designed to test the page breaking logic of the PDF export. We want to ensure that content flows naturally without leaving massive empty gaps at the bottom of pages, while also respecting the 'stay-together' rules for charts and icons. Sentence one. Sentence two. Sentence three. Sentence four. Sentence five." for i in range(15)])
        await page.fill("#text-input", long_text)
        
        # 4. Trigger Magic Prompt simulation (we'll just use the unified endpoint)
        await page.click("#magic-prompt-btn")
        
        # Wait for modal and response
        await page.wait_for_selector("#magic-prompt-modal", state="visible")
        
        # Instead of waiting for real AI (can be slow), we'll inject a mock response into the textarea
        # and click the 'Process & Render' button directly if possible, 
        # but the prompt modal usually has its own 'Process' button.
        # Let's check how the UI works.
        
        # In script.js, magicPromptBtn triggers /magic-prompt/unified.
        # Then the modal shows up with magicPromptText.
        # The user then clicks 'Process & Render' which calls /explain.
        
        # Let's just bypass the modal and hit the render logic if we can,
        # or simulate the full click stream.
        
        # Inject mock AI response and click process
        await page.evaluate("""() => {
            const aiArea = document.getElementById('ai-response-input');
            const data = {
                "title": "Page Break Test",
                "summary": "Testing PDF layout stability.",
                "sections": Array.from({length: 10}, (_, i) => ({
                    "title": "Section " + (i+1),
                    "content": "This is a detailed explanation for section " + (i+1) + ". " + "A".repeat(500),
                    "sentences": [
                        {"text": "Sentence 1 with icon.", "icon": {"keyword": "rocket", "type": "heroicons", "path": "icons/heroicons/rocket-launch.svg"}},
                        {"text": "Sentence 2 with icon.", "icon": {"keyword": "shield", "type": "heroicons", "path": "icons/heroicons/shield-check.svg"}},
                        {"text": "Sentence 3 with icon.", "icon": {"keyword": "engine", "type": "heroicons", "path": "icons/heroicons/bolt.svg"}}
                    ],
                    "ascii_box": "[ Section " + (i+1) + " Chart ]\\n+-------+\\n| DATA  |\\n+-------+"
                }))
            };
            aiArea.value = JSON.stringify(data);
            document.getElementById('process-ai-btn').click();
        }""")
        
        # 5. Wait for render
        await page.wait_for_selector(".section-block", timeout=5000)
        
        # 6. Verify visual state
        await page.screenshot(path="tests/pdf_verification_render.png", full_page=True)
        print("✅ Rendered view captured to tests/pdf_verification_render.png")
        
        # 7. Trigger PDF export
        # Note: html2pdf might open a print dialog or just download.
        # In a headless environment, we'll check if the button exists and triggers.
        pdf_btn = await page.query_selector("#export-pdf-btn")
        if pdf_btn:
            print("✅ PDF Export button found.")
            # We don't necessarily need to download the actual PDF to verify CSS rules
            # because the CSS rules we applied are in the HTML that html2pdf uses.
            # However, we can check for the presence of the rules in computed style.
            
            section_break_inside = await page.evaluate("""() => {
                const el = document.querySelector('.section-block');
                return window.getComputedStyle(el).breakInside;
            }""")
            print(f"Computed break-inside for .section-block: {section_break_inside}")
            
            if section_break_inside == 'auto':
                print("✅ CSS SUCCESS: .section-block allows page breaks.")
            else:
                print(f"❌ CSS FAILURE: .section-block break-inside is {section_break_inside}")
                
            header_break_after = await page.evaluate("""() => {
                const el = document.querySelector('.section-header');
                return window.getComputedStyle(el).breakAfter;
            }""")
            print(f"Computed break-after for .section-header: {header_break_after}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_pdf_layout())
