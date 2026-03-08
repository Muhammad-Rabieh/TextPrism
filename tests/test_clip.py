import requests

html = """
<!DOCTYPE html>
<html>
<head>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .sentence-item {
            display: flex;
            align-items: flex-start;
            gap: 16px;
            padding: 14px 18px;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #3b82f6;
        }
        .sentence-text {
            margin: 0 !important;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="sentence-item">
        <img src="http://127.0.0.1:8000/icons/openmoji/1F9ED.png" style="width: 32px; height: 32px;">
        <p class="sentence-text">This is a test of geology typography jumping quickly over lazy foxes jumping yyy ppp ggg jjj qqq</p>
    </div>
</body>
</html>
"""

def test_clip():
    try:
        r = requests.post("http://127.0.0.1:8000/export-pdf", json={"html": html})
        if r.status_code == 200:
            with open("test_clip.pdf", "wb") as f:
                f.write(r.content)
            print("Saved PDF of size:", len(r.content))
    except requests.exceptions.ConnectionError:
        print("Server not running. Skipping.")

