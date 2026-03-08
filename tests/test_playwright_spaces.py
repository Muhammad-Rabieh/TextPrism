import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        
        # Monitor failed requests
        fails = []
        page.on("requestfailed", lambda req: fails.append((req.url, req.failure.error_text)))
        page.on("response", lambda res: print(res.url, res.status))
        
        html = """
        <img src="http://127.0.0.1:8000/clipart/module_10/assets/Statue of liberty/Color/statue_of_liberty_color.svg" alt="TEST ALT STATUE">
        """
        await page.set_content(html, wait_until="networkidle")
        print("Fails:", fails)
        
        pdf = await page.pdf()
        with open("test_space.pdf", "wb") as f:
            f.write(pdf)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
