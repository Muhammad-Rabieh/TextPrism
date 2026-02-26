#!/usr/bin/env python3
"""
Visual Lexicon Builder (build_index.py)
=======================================
One-time script to scan asset folders and create
JSON lookup tables (the "Visual Lexicon") that map English keywords to filenames.

This is the foundation of Iconographic Annotation — pairing concepts with visuals.

Part of TextPrism.
"""

import json
import os
import re

# ─────────────────────────────────────────────────────────────
# Project paths
# ─────────────────────────────────────────────────────────────

# BASE_DIR is scripts/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DATA_DIR should be at the project root
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'data')
OPENMOJI_DIR = os.path.join(DATA_DIR, 'icons', 'openmoji')
HEROICON_DIR = os.path.join(DATA_DIR, 'icons', 'heroicons')
CLIPART_DIR = os.path.join(DATA_DIR, 'clipart')

EMOJI_INDEX_PATH = os.path.join(DATA_DIR, 'emoji_index.json')
HEROICON_INDEX_PATH = os.path.join(DATA_DIR, 'heroicon_index.json')
CLIPART_INDEX_PATH = os.path.join(DATA_DIR, 'clipart_index.json')


# ─────────────────────────────────────────────────────────────
# Curated OpenMoji Mapping
# ─────────────────────────────────────────────────────────────
# OpenMoji filenames are Unicode codepoints (e.g., 1F600.png).
# We manually map common English keywords to their Unicode codepoints.
# This is a curated subset for semantic icon mapping.

OPENMOJI_KEYWORD_MAP = {
    # ── Emotions & Faces ──
    "happy": "1F600", "smile": "1F603", "laugh": "1F602", "joy": "1F602",
    "love": "2764-FE0F", "heart": "2764-FE0F", "sad": "1F622", "cry": "1F622",
    "angry": "1F621", "fear": "1F628", "surprise": "1F632", "think": "1F914",
    "thinking": "1F914", "cool": "1F60E", "sunglasses": "1F60E",
    "worried": "1F61F", "confused": "1F615", "proud": "1F60A",
    "tired": "1F634", "sleep": "1F634", "sick": "1F912",
    "celebrate": "1F389", "party": "1F389", "clap": "1F44F",

    # ── People & Communication ──
    "person": "1F9D1", "people": "1F465", "group": "1F465",
    "family": "1F46A", "child": "1F9D2", "baby": "1F476",
    "man": "1F468", "woman": "1F469", "handshake": "1F91D",
    "wave": "1F44B", "thumbs up": "1F44D", "thumbs down": "1F44E",
    "point": "1F449", "hand": "270B", "pray": "1F64F",
    "speak": "1F5E3", "speech": "1F4AC", "talk": "1F4AC",
    "listen": "1F442", "eye": "1F441", "eyes": "1F440",

    # ── Nature & Weather ──
    "sun": "2600", "moon": "1F319", "star": "2B50", "stars": "1F31F",
    "rain": "1F327", "cloud": "2601", "snow": "1F328",
    "wind": "1F32C", "lightning": "26A1", "thunder": "26A1",
    "rainbow": "1F308", "fire": "1F525", "flame": "1F525",
    "water": "1F4A7", "droplet": "1F4A7", "ocean": "1F30A",
    "wave_water": "1F30A", "earth": "1F30D", "globe": "1F30D",
    "world": "1F30D", "mountain": "26F0", "tree": "1F333",
    "flower": "1F33B", "plant": "1F331", "leaf": "1F343",
    "animal": "1F43E", "dog": "1F436", "cat": "1F431",
    "bird": "1F426", "fish": "1F41F", "butterfly": "1F98B",

    # ── Objects & Tools ──
    "book": "1F4D6", "books": "1F4DA", "notebook": "1F4D3",
    "pen": "1F58A", "pencil": "270F", "paper": "1F4C4",
    "document": "1F4C4", "folder": "1F4C1", "file": "1F4C2",
    "clipboard": "1F4CB", "calendar": "1F4C5", "clock": "1F554",
    "time": "1F554", "watch": "231A", "alarm": "23F0",
    "phone": "1F4F1", "computer": "1F4BB", "laptop": "1F4BB",
    "keyboard": "2328", "screen": "1F5A5", "printer": "1F5A8",
    "camera": "1F4F7", "video": "1F4F9", "microphone": "1F3A4",
    "speaker": "1F50A", "music": "1F3B5", "headphones": "1F3A7",
    "mail": "1F4E7", "email": "1F4E7", "letter": "1F4E9",
    "package": "1F4E6", "gift": "1F381", "key": "1F511",
    "lock": "1F512", "unlock": "1F513", "magnifying": "1F50D",
    "search": "1F50D", "flashlight": "1F526", "bulb": "1F4A1",
    "light": "1F4A1", "idea": "1F4A1", "battery": "1F50B",
    "plug": "1F50C", "tool": "1F6E0", "wrench": "1F527",
    "hammer": "1F528", "gear": "2699", "settings": "2699",
    "shield": "1F6E1", "sword": "2694",

    # ── Science & Education ──
    "science": "1F52C", "microscope": "1F52C", "telescope": "1F52D",
    "experiment": "1F9EA", "lab": "1F9EA", "test tube": "1F9EA",
    "dna": "1F9EC", "atom": "269B", "formula": "1F9EE",
    "brain": "1F9E0", "mind": "1F9E0", "intelligence": "1F9E0",
    "robot": "1F916", "ai": "1F916", "artificial": "1F916",
    "graduate": "1F393", "school": "1F3EB", "university": "1F3EB",
    "teacher": "1F9D1-200D-1F3EB", "student": "1F9D1-200D-1F393",
    "study": "1F4D6", "learn": "1F4D6", "education": "1F393",
    "math": "1F522", "number": "1F522", "calculate": "1F9EE",
    "energy": "26A1", "power_sci": "26A1", "molecule": "269B",
    "oxygen": "1F4A7", "glucose": "1F36D", "carbon": "1F525",
    "cell": "1F9A0", "biology": "1F33F", "physics": "269B",
    "chemistry": "1F9EA", "space": "1F680", "planet": "1FA90",

    # ── Nature & Environment ──
    "nature": "1F333", "environment": "1F30D", "ecology": "1F33F",
    "leaf": "1F343", "grass": "1F33F", "flower": "1F33B",
    "forest": "1F332", "jungle": "1F334", "desert": "1F335",
    "ice": "1F3CA", "fire_nature": "1F525", "water_cycle": "1F504",
    "liquid": "1F4A7", "gas": "1F4A8", "solid": "1F9F1",
    "cycle": "1F504", "loop": "1F504",

    # ── Abstract & Logic ──
    "logic": "2699", "balance": "2696", "scale": "2696",
    "law": "2696", "justice": "2696", "peace": "262E",
    "warning_icon": "26A0", "danger_icon": "2620", "radiation": "2622",
    "biohazard": "2623", "infinite": "267E", "omega": "2126",
    "alpha": "03B1", "sigma": "03A3", "delta": "0394",

    # ── Technology & Computing ──
    "code": "1F4BB", "programming": "1F4BB", "software": "1F4BB",
    "bug": "1F41B", "debug": "1F41B", "database": "1F4BD",
    "disk": "1F4BD", "cloud_tech": "2601", "server": "1F5A5",
    "network": "1F310", "internet": "1F310", "web": "1F310",
    "link": "1F517", "chain": "1F517", "satellite": "1F6F0",
    "rocket": "1F680", "launch": "1F680",

    # ── Business & Finance ──
    "money": "1F4B0", "dollar": "1F4B5", "euro": "1F4B6",
    "bank": "1F3E6", "chart": "1F4C8", "graph": "1F4C8",
    "increase": "1F4C8", "decrease": "1F4C9", "trend": "1F4C8",
    "briefcase": "1F4BC", "business": "1F4BC", "work": "1F4BC",
    "office": "1F3E2", "factory": "1F3ED", "shop": "1F3EA",
    "shopping": "1F6D2", "cart": "1F6D2",
    "meeting": "1F91D", "presentation": "1F4CA",

    # ── Food & Drink ──
    "food": "1F37D", "eat": "1F37D", "restaurant": "1F37D",
    "apple": "1F34E", "fruit": "1F34F", "vegetable": "1F966",
    "bread": "1F35E", "pizza": "1F355", "burger": "1F354",
    "coffee": "2615", "tea": "1F375", "drink": "1F964",
    "wine": "1F377", "beer": "1F37A", "cake": "1F382",
    "cookie": "1F36A", "ice cream": "1F368", "chocolate": "1F36B",

    # ── Travel & Places ──
    "car": "1F697", "bus": "1F68C", "train": "1F686",
    "airplane": "2708", "ship": "1F6A2", "bicycle": "1F6B2",
    "house": "1F3E0", "home": "1F3E0", "building": "1F3E2",
    "hospital": "1F3E5", "hotel": "1F3E8", "church": "26EA",
    "map": "1F5FA", "compass": "1F9ED", "flag": "1F3F3",

    # ── Health & Safety ──
    "health": "1F3E5", "medical": "2695", "medicine": "1F48A",
    "pill": "1F48A", "injection": "1F489", "bandage": "1FA79",
    "mask": "1F637", "virus": "1F9A0", "bacteria": "1F9A0",
    "safety": "1F6E1", "warning": "26A0", "danger": "2620",
    "emergency": "1F6A8", "ambulance": "1F691",

    # ── Symbols & Abstract ──
    "check": "2705", "correct": "2705", "yes": "2705", "done": "2705",
    "cross": "274C", "wrong": "274C", "no": "274C", "error": "274C",
    "question": "2753", "exclamation": "2757", "important": "2757",
    "info": "2139", "information": "2139",
    "arrow_right": "27A1", "arrow_left": "2B05", "arrow_up": "2B06",
    "arrow_down": "2B07", "cycle": "1F504", "refresh": "1F504",
    "plus": "2795", "minus": "2796", "multiply": "2716",
    "infinity": "267E", "percent": "1F4AF", "hundred": "1F4AF",
    "target": "1F3AF", "goal": "1F3AF", "trophy": "1F3C6",
    "medal": "1F3C5", "crown": "1F451", "diamond_gem": "1F48E",
    "art": "1F3A8", "paint": "1F3A8", "palette": "1F3A8",
    "magic": "1FA84", "sparkle": "2728", "shine": "2728",
    "power": "1F4AA", "strong": "1F4AA", "muscle": "1F4AA",
    "speed": "1F3CE", "fast": "1F3CE",
    "puzzle": "1F9E9", "piece": "1F9E9", "solution": "1F9E9",
    "tag": "1F3F7", "label": "1F3F7", "pin": "1F4CC",
    "bookmark": "1F516", "memo": "1F4DD", "note": "1F4DD",
    "news": "1F4F0", "newspaper": "1F4F0",
    "stop": "1F6D1", "slow": "1F6A7", "construction": "1F6A7",
    "recycle": "267B", "environment": "267B", "green": "267B",
}


# ─────────────────────────────────────────────────────────────
# Heroicon Indexing
# ─────────────────────────────────────────────────────────────

def build_heroicon_index():
    """
    Parse heroicon filenames into searchable keyword mappings.
    Heroicons have descriptive names like 'light-bulb.svg', 'document-text.svg'.
    """
    index = {}

    if not os.path.isdir(HEROICON_DIR):
        print(f"⚠️  Heroicons directory not found: {HEROICON_DIR}")
        return index

    for filename in sorted(os.listdir(HEROICON_DIR)):
        if not filename.endswith('.svg'):
            continue

        name = filename.replace('.svg', '')
        # Split on hyphens to get keywords
        keywords = name.split('-')

        # Add the full name
        index[name] = filename

        # Add individual keywords (only if they're meaningful, 3+ chars)
        for kw in keywords:
            if len(kw) >= 3 and kw not in index:
                index[kw] = filename

        # Add the full name with spaces
        full_name = name.replace('-', ' ')
        if full_name not in index:
            index[full_name] = filename

    return index


# ─────────────────────────────────────────────────────────────
# Clipart Indexing (illlustrations.co)
# ─────────────────────────────────────────────────────────────

def build_clipart_index():
    """
    Recursively scan the data/clipart folder and index SVGs and PNGs from all modules.
    Extract keywords from filenames for semantic mapping.
    """
    index = {}
    
    if not os.path.isdir(CLIPART_DIR):
        print(f"⚠️  Clipart directory not found: {CLIPART_DIR}")
        return index

    for root, dirs, files in os.walk(CLIPART_DIR):
        for filename in sorted(files):
            if not filename.endswith('.svg') and not filename.endswith('.png'):
                continue

            # Full path relative to the root clipart folder (e.g., 'module_0/day1-ipod.svg')
            rel_path = os.path.relpath(os.path.join(root, filename), CLIPART_DIR)

            # Extract keyword from filename
            name = os.path.splitext(filename)[0]
            
            # Clean up prefixes like 'day93-'
            match = re.search(r'day\d+-?(.*)', name, re.IGNORECASE)
            if match and match.group(1):
                keyword = match.group(1).lower().replace('-', ' ').replace('_', ' ')
            else:
                keyword = name.lower().replace('-', ' ').replace('_', ' ')

            if not keyword:
                keyword = name.lower()

            # Add the cleaned keyword
            # We use setdefault to avoid later modules overwriting earlier ones
            index.setdefault(keyword, rel_path)

            # Also add the original raw name if it's different and absent
            index.setdefault(name.lower(), rel_path)

    return index


# ─────────────────────────────────────────────────────────────
# OpenMoji Indexing
# ─────────────────────────────────────────────────────────────

def build_emoji_index():
    """
    Build the emoji index from the curated keyword map.
    Validates that each referenced PNG file actually exists.
    """
    index = {}
    missing = []

    for keyword, codepoint in OPENMOJI_KEYWORD_MAP.items():
        filename = f"{codepoint}.png"
        filepath = os.path.join(OPENMOJI_DIR, filename)

        if os.path.isfile(filepath):
            index[keyword] = filename
        else:
            missing.append((keyword, filename))

    return index, missing


# ─────────────────────────────────────────────────────────────
# Main Build Process
# ─────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("🔧 Visual Lexicon Builder")
    print("=" * 60)

    # Create data directory
    os.makedirs(DATA_DIR, exist_ok=True)

    # ── Build Emoji Index ──
    print("\n📦 Building OpenMoji emoji index...")
    emoji_index, missing = build_emoji_index()
    print(f"   ✅ Mapped {len(emoji_index)} keywords to emoji PNGs")
    if missing:
        print(f"   ⚠️  {len(missing)} keywords have missing PNGs:")
        for kw, fn in missing[:10]:
            print(f"      - '{kw}' → {fn}")
        if len(missing) > 10:
            print(f"      ... and {len(missing) - 10} more")

    # Save emoji index
    with open(EMOJI_INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(emoji_index, f, indent=2, ensure_ascii=False)
    print(f"   💾 Saved to: {EMOJI_INDEX_PATH}")

    # ── Build Heroicon Index ──
    print("\n📦 Building Heroicon index...")
    heroicon_index = build_heroicon_index()
    print(f"   ✅ Mapped {len(heroicon_index)} keywords to Heroicon SVGs")

    # Save heroicon index
    with open(HEROICON_INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(heroicon_index, f, indent=2, ensure_ascii=False)
    print(f"   💾 Saved to: {HEROICON_INDEX_PATH}")

    # ── Build Clipart Index ──
    print("\n📦 Building illlustrations.co index...")
    clipart_index = build_clipart_index()
    print(f"   ✅ Mapped {len(clipart_index)} keywords to stylized illustrations")

    # Save clipart index
    with open(CLIPART_INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(clipart_index, f, indent=2, ensure_ascii=False)
    print(f"   💾 Saved to: {CLIPART_INDEX_PATH}")

    # ── Summary ──
    print("\n" + "=" * 60)
    print("✅ Visual Lexicon built successfully!")
    print(f"   Emoji keywords:    {len(emoji_index)}")
    print(f"   Heroicon keywords: {len(heroicon_index)}")
    print(f"   Clipart keywords:  {len(clipart_index)}")
    print(f"   Total vocabulary:  {len(emoji_index) + len(heroicon_index) + len(clipart_index)}")
    print("=" * 60)

    # List available OpenMoji files count
    if os.path.isdir(OPENMOJI_DIR):
        total_emojis = len([f for f in os.listdir(OPENMOJI_DIR) if f.endswith('.png')])
        print(f"\n📊 Stats:")
        print(f"   Available OpenMoji PNGs: {total_emojis}")
        print(f"   Mapped to keywords:     {len(emoji_index)}")
        print(f"   Coverage:               {len(emoji_index)/total_emojis*100:.1f}%")
        print(f"   Unmapped PNGs:          {total_emojis - len(emoji_index)}")
        print(f"   (Unmapped emojis can still be used by codepoint)")


if __name__ == '__main__':
    main()
