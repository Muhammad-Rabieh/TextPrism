import requests
import fitz
import sys

payload = {"text": "This is a simple test containing the word geography topography jumping foxes.", "ai_tier": "heuristic"}
r = requests.post("http://127.0.0.1:8000/explain", data=payload)
html_ui = r.text

r_pdf = requests.post("http://127.0.0.1:8000/export-pdf", json={"html": html_ui})
with open("tests/actual_app_output.pdf", "wb") as f:
    f.write(r_pdf.content)

doc = fitz.open("tests/actual_app_output.pdf")
page = doc[0]
pix = page.get_pixmap(dpi=200)
pix.save("tests/actual_app_output.png")
print("Saved PDF and PNG to tests/")
