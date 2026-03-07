import asyncio
from playwright.async_api import async_playwright

html_content = """
<!DOCTYPE html>
<html>
<head>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; padding: 50px; }
        
        .box {
            border: 1px solid red;
            margin-bottom: 20px;
        }
        
        /* The clipping bug (Chromium tight bounding box) */
        .clipped {
            font-size: 24px;
            line-height: 1.0;
            overflow: hidden;
        }
        
        /* The fix (expanded paint box) */
        .fixed {
            font-size: 24px;
            line-height: 1.0;
            padding-top: 10px !important;
            padding-bottom: 10px !important;
            margin-top: -10px !important;
            margin-bottom: -10px !important;
            overflow: visible !important;
            display: inline-block;
        }
    </style>
</head>
<body>
    <h1>PDF Clipping Test</h1>
    
    <h3>Without Fix (Notice tops of 'T' and bottoms of 'y', 'g', 'p' might touch/clip the red border)</h3>
    <div class="box">
        <div class="clipped">Typography testing jumping quickly over lazy foxes jumping yyy ppp ggg jjj qqq Testing ascenders: Ill lll hhh bbb ddd ttt</div>
    </div>
    
    <h3>With Fix (Paint box explicitly expanded via padding & negative margin)</h3>
    <div class="box">
        <div class="fixed">Typography testing jumping quickly over lazy foxes jumping yyy ppp ggg jjj qqq Testing ascenders: Ill lll hhh bbb ddd ttt</div>
    </div>
</body>
</html>
"""

async def run_test():
    print("Generating clipping test PDF...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html_content, wait_until="networkidle")
        
        # Take a visual screenshot for easy viewing without a PDF reader
        await page.screenshot(path="tests/clipping_test_output.png")
        
        # Output the PDF
        await page.pdf(path="tests/clipping_test_output.pdf", print_background=True)
        await browser.close()
        print("✅ Generated: tests/clipping_test_output.pdf")
        print("✅ Generated: tests/clipping_test_output.png (for quick visual review)")
        print("\nIf 'With Fix' works, apply `padding-top/bottom: Xpx; margin-top/bottom: -Xpx;` to your text classes.")

if __name__ == "__main__":
    asyncio.run(run_test())
