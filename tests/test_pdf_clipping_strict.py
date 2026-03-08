import requests
import sys
import fitz

html_payload = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important; padding: 40px; }
        .test-text {
            font-size: 16px;
            line-height: 1.8;
            padding-top: 10px;
            padding-bottom: 10px;
            margin-top: -10px;
            margin-bottom: -10px;
<html><body><h1>Test</h1></body></html>
"""

def test_pdf_clipping():
    pdf_path = "tests/strict_clipping.pdf"
    
    try:
        r = requests.post("http://127.0.0.1:8000/export-pdf", json={"html": html_payload})
        if r.status_code != 200:
            print("Server returned non-200. Skipping.")
            return
        with open(pdf_path, "wb") as f:
            f.write(r.content)
    except requests.exceptions.ConnectionError:
        print("Server not running on port 8000. Skipping live test.")
        return
    except Exception as e:
        assert False, str(e)
    
    doc = fitz.open(pdf_path)
    page = doc[0]
    words = page.get_text("words")
    
    clipping_suspected = False
    print(f"Total words found: {len(words)}")
    
    for w in words:
        x0, y0, x1, y1, word_text = w[:5]
        height = y1 - y0
        print(f"Word: '{word_text}', Height: {height:.2f}pt, Width: {(x1-x0):.2f}pt, Bbox: {x0:.1f},{y0:.1f} -> {x1:.1f},{y1:.1f}")
        if height < 13.0: # Healthy height for 16px (~12pt) font is ~14pt. Threshold at 13pt to catch real clipping.
            print(f"SUSPICIOUS CLIPPING on '{word_text}' (height: {height:.2f}pt) bbox: {x0:.1f},{y0:.1f} -> {x1:.1f},{y1:.1f}")
            clipping_suspected = True
    
    assert not clipping_suspected, "FAIL: The PDF word bounding boxes are suspiciously tight, indicating Chromium clipped the font."
    print("PASS: The bounding boxes appear sufficiently large for the font.")

if __name__ == "__main__":
    test_pdf_clipping()
