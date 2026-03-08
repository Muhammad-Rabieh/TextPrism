from src.emoji_engine import EmojiEngine
import os

def debug():
    engine = EmojiEngine()
    print(f"Stats: {engine.stats()}")
    
    word = "rocket"
    res = engine.lookup(word, embed=True)
    print(f"Lookup '{word}':")
    print(f"  Type: {res.get('type')}")
    print(f"  Path: {res.get('path')}")
    src = res.get('src')
    if src:
        print(f"  Src: {src[:50]}... (Length: {len(src)})")
    else:
        print("  Src: MISSING (None)")
        
    # Check if file exists
    if res.get('path'):
        # Normalize as in get_base64_src
        rel_path = res.get('path')
        clean_path = rel_path
        if rel_path.startswith('icons/'): clean_path = rel_path[6:]
        if rel_path.startswith('clipart/'): clean_path = rel_path[8:]
        
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        # Adjustment for tests/ dir
        DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'data')
        abs_path = os.path.join(DATA_DIR, clean_path)
        print(f"  Checking Filesystem: {abs_path}")
        print(f"  Exists: {os.path.exists(abs_path)}")

if __name__ == "__main__":
    debug()
