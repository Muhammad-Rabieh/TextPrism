import os
import requests
import zipfile
import subprocess
from io import BytesIO

candidates = [
    {
        "name": "Module 1: Debian OpenClipart (SVG Core)",
        "url": "http://ftp.us.debian.org/debian/pool/main/o/openclipart/openclipart-svg_0.18+dfsg-21_all.deb",
        "type": "deb"
    },
    {
        "name": "Module 2: Lucide Icons Master Set (SVG)",
        "url": "https://github.com/lucide-icons/lucide/archive/refs/heads/main.zip",
        "type": "zip"
    },
    {
        "name": "Module 3: Google Noto Emoji (Unified SVG)",
        "url": "https://github.com/googlefonts/noto-emoji/archive/refs/heads/main.zip",
        "type": "zip"
    },
    {
        "name": "Module 4: UN OCHA Humanitarian Pack",
        "url": "https://github.com/vizzuality/ocha-icons/archive/refs/heads/master.zip",
        "type": "zip"
    },
    {
        "name": "Module 5: Open Doodles (Sketchy People)",
        "url": "https://github.com/fangpenlin/open-doodles/archive/refs/heads/master.zip",
        "type": "zip"
    },
    {
        "name": "Module 6: Humaaans (Mix-&-Match People)",
        "url": "https://github.com/pablostanley/humaaans-design-library/archive/refs/heads/master.zip",
        "type": "zip"
    },
    {
        "name": "Module 8: Handy Arrows (Visual Connectors)",
        "url": "https://github.com/Eronred/handy-arrows/archive/refs/heads/main.zip",
        "type": "zip"
    },
    {
        "name": "Module 9: Ira Design (Modular Gradient Scenes)",
        "url": "https://github.com/ira-design/ira-illustrations/archive/refs/heads/master.zip",
        "type": "zip"
    },
    {
        "name": "Module 10: Fluent Emoji SVG (Microsoft)",
        "url": "https://github.com/cathrinew/microsoft-fluentui-emoji-svg-collection/archive/refs/heads/main.zip",
        "type": "zip"
    },
    {
        "name": "Module 11: 3D Icons (realvjy CC0)",
        "url": "https://github.com/realvjy/3dicons/archive/refs/heads/main.zip",
        "type": "zip"
    },
    {
        "name": "Module 12: Bottts (Robot Avatars)",
        "url": "https://github.com/pablostanley/bottts/archive/refs/heads/master.zip",
        "type": "zip"
    },
    {
        "name": "Module 13: Debian OpenClipart (PNG Rendered)",
        "url": "http://ftp.us.debian.org/debian/pool/main/o/openclipart/openclipart-png_0.18+dfsg-21_all.deb",
        "type": "deb"
    },
    {
        "name": "Module 14: Tabler Icons (UI Master Set)",
        "url": "https://github.com/tabler/tabler-icons/archive/refs/heads/main.zip",
        "type": "zip"
    },
    {
        "name": "Module 15: Font Awesome Free (Industry Standard)",
        "url": "https://github.com/FortAwesome/Font-Awesome/releases/download/6.7.2/fontawesome-free-6.7.2-web.zip",
        "type": "zip"
    },
    {
        "name": "Module 16: Phosphor Icons (Flexible Multi-Weight)",
        "url": "https://github.com/phosphor-icons/core/archive/refs/heads/main.zip",
        "type": "zip"
    },
    {
        "name": "Module 17: Heroicons Full (All Styles)",
        "url": "https://github.com/tailwindlabs/heroicons/archive/refs/heads/master.zip",
        "type": "zip"
    },
    {
        "name": "Module 18: Avataaars (SVG Character Generator)",
        "url": "https://github.com/fangpenlin/avataaars/archive/refs/heads/master.zip",
        "type": "zip"
    },
    {
        "name": "Module 19: Flowbite Illustrations (3D-Style SVGs)",
        "url": "https://github.com/themesberg/flowbite-illustrations/archive/refs/heads/main.zip",
        "type": "zip"
    },
    {
        "name": "Module 20: Mega Doodles Pack (Hand-Drawn Objects)",
        "url": "https://github.com/MariaLetta/mega-doodles-pack/archive/refs/heads/master.zip",
        "type": "zip"
    },
    {
        "name": "Module 21: Bigheads (Character Avatar Generator)",
        "url": "https://github.com/robertlinde/extended-bigheads/archive/refs/heads/main.zip",
        "type": "zip"
    }
]

DATA_DIR = os.path.join(os.getcwd(), 'data', 'clipart')
os.makedirs(DATA_DIR, exist_ok=True)

def download_and_extract_zip(url, target_dir):
    try:
        if os.path.exists(target_dir):
            print(f"Skipping {target_dir} (already exists)")
            return
        os.makedirs(target_dir, exist_ok=True)
        print(f"Downloading ZIP from {url}...")
        r = requests.get(url, stream=True, timeout=60)
        r.raise_for_status()
        with zipfile.ZipFile(BytesIO(r.content)) as z:
            z.extractall(target_dir)
        print(f"Extracted to {target_dir}")
    except Exception as e:
        print(f"Failed to process ZIP {url}: {e}")

def download_and_extract_deb(url, target_dir):
    try:
        if os.path.exists(target_dir):
            print(f"Skipping {target_dir} (already exists)")
            return
        os.makedirs(target_dir, exist_ok=True)
        print(f"Downloading DEB from {url}...")
        deb_path = os.path.join(target_dir, "temp.deb")
        r = requests.get(url, stream=True, timeout=60)
        r.raise_for_status()
        with open(deb_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Extracting DEB {deb_path}...")
        subprocess.run(["ar", "x", deb_path], cwd=target_dir, check=True)
        
        data_tar = os.path.join(target_dir, "data.tar.xz")
        if os.path.exists(data_tar):
            subprocess.run(["tar", "-xf", "data.tar.xz"], cwd=target_dir, check=True)
            print(f"Extracted data.tar.xz to {target_dir}")
        else:
            print(f"data.tar.xz not found in {deb_path}")
            
        # Clean up
        os.remove(deb_path)
        for temp_file in ["data.tar.xz", "control.tar.xz", "debian-binary"]:
            tf_path = os.path.join(target_dir, temp_file)
            if os.path.exists(tf_path):
                os.remove(tf_path)
                
    except Exception as e:
        print(f"Failed to process DEB {url}: {e}")

def main():
    print("Starting Clipart Download Process...")
    for cand in candidates:
        name_clean = cand["name"].split(":")[0].replace(" ", "_").lower() # e.g. module_1
        target_dir = os.path.join(DATA_DIR, name_clean)
        
        if cand["type"] == "zip":
            download_and_extract_zip(cand["url"], target_dir)
        elif cand["type"] == "deb":
            download_and_extract_deb(cand["url"], target_dir)

    print("\nDownload process completed.")

if __name__ == "__main__":
    main()
