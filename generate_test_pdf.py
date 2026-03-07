import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as pw:
        # Launch browser
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        
        # Navigate to our server
        await page.goto("http://127.0.0.1:8000")
        
        # Fill in dummy data
        await page.fill("#text-input", "Test")
        
        # Send Mock response and render
        await page.evaluate("""
            const mockHtml = `
            <div class="section-block">
                <h1 class="section-header">Section 1</h1>
                <div class="sentence-item">Short sentence.</div>
                <div class="sentence-item" style="height: 800px;">Huge sentence item taking almost full page.</div>
                <div class="sentence-item">Another sentence that should be pushed to next page.</div>
            </div>
            `;
            document.getElementById('output-content').innerHTML = mockHtml;
            document.querySelector('.output-placeholder').style.display = 'none';
        """)
        
        # Click the download PDF button
        async with page.expect_download() as download_info:
            await page.click("#download-pdf-btn")
        
        download = await download_info.value
        await download.save_as("test_output.pdf")
        print("PDF downloaded to test_output.pdf")
        
        await browser.close()

asyncio.run(run())
