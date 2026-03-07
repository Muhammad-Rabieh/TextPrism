import asyncio
from playwright.async_api import async_playwright

html_content = """
<img src="http://127.0.0.1:8000/clipart/module_10/assets/Statue of liberty/Color/statue_of_liberty_color.svg" alt="TEST ALT STATUE">
<img src="http://127.0.0.1:8000/icons/openmoji/1F9ED.png" alt="compass text">
<img src="http://localhost:8000/icons/openmoji/1F9ED.png" alt="compass text via localhost">
"""

async def run():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        page.on("requestfailed", lambda req: print("FAILEDREQ:", req.url, req.failure))
        page.on("response", lambda res: print("RESPONSE:", res.url, res.status))
        await page.set_content(html_content, wait_until="networkidle")
        await browser.close()

asyncio.run(run())
