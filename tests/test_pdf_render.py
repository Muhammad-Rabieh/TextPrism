import requests

html = """
<!DOCTYPE html>
<html>
<body>
    <h1>Test</h1>
    <img src="http://127.0.0.1:8000/clipart/module_10/assets/Statue%20of%20liberty/Color/statue_of_liberty_color.svg" alt="statue text">
    <img src="http://127.0.0.1:8000/icons/openmoji/1F9ED.png" alt="compass text">
</body>
</html>
"""

def test_pdf_render():
    try:
        r = requests.post("http://127.0.0.1:8000/export-pdf", json={"html": html})
        if r.status_code == 200:
            with open("test_out.pdf", "wb") as f:
                f.write(r.content)
            print("Saved PDF of size:", len(r.content))
    except requests.exceptions.ConnectionError:
        print("Server not running. Skipping.")
