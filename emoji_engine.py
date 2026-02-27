#!/usr/bin/env python3
"""
Visual Lexicon Lookup Engine (emoji_engine.py)
===============================================
Given a word or concept, find the best matching icon from the Visual Lexicon.
This is the core of Iconographic Annotation — pairing concepts with visuals.

Lookup Strategy:
1. Exact match in clipart index
2. Exact match in emoji index
3. Exact match in heroicon index
... (and more)

Part of TextPrism.
"""

import json
import os
import re

# ─────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
EMOJI_INDEX_PATH = os.path.join(DATA_DIR, 'emoji_index.json')
HEROICON_INDEX_PATH = os.path.join(DATA_DIR, 'heroicon_index.json')
CLIPART_INDEX_PATH = os.path.join(DATA_DIR, 'clipart_index.json')

# ─────────────────────────────────────────────────────────────
# Module Color Classification
# ─────────────────────────────────────────────────────────────
# Tier A (COLOR): Multi-color, vibrant, professional
# Tier B (MIXED): Has color variants but also outline/mono
# Tier C (BW):    Monochrome outlines, black fills, silhouettes
#
# This is the CORE of the Vibrancy Ranking Engine.
# BW modules are demoted to last-resort status.

MODULE_COLOR_TIER = {
    'module_0':  'A',   # illlustrations.co — pro color vectors
    'module_1':  'A',   # OpenClipArt (Debian) — multi-color SVGs
    'module_3':  'A',   # Google Noto Emoji — full-color emoji
    'module_6':  'A',   # Humaaans — colorful people
    'module_8':  'A',   # Ira Design — gradient infographics
    'module_10': 'A',   # Fluent Emoji (Microsoft) — color/3D/flat
    'module_11': 'A',   # Bottts/3D — 3D gradient icons
    'module_19': 'A',   # Mega Doodles Pack — 3D color SVGs
    'module_20': 'B',   # Bigheads — color avatars, limited keywords
    'module_2':  'C',   # Lucide — BW outlines
    'module_4':  'C',   # UN OCHA — black silhouettes
    'module_5':  'C',   # Open Doodles — BW sketches
    'module_9':  'C',   # Flowbite/Misc — mostly font files
    'module_13': 'C',   # Tabler — BW outlines
    'module_14': 'C',   # Tabler (outline) — BW outlines
    'module_15': 'C',   # Font Awesome — black solid fills
    'module_16': 'C',   # Phosphor — BW outlines/duotone
    'module_17': 'C',   # Heroicons (Full) — BW outlines
    'module_18': 'C',   # Avataaars — only 1-2 files
}

# Base vibrancy scores per tier
TIER_SCORES = {'A': 100, 'B': 60, 'C': 15}

def _score_clipart_path(path):
    """Score a clipart asset path by color vibrancy.
    
    Uses module tier + path-level color keywords to determine quality.
    Higher score = more colorful = preferred.
    """
    p = path.lower()
    
    # Determine module tier
    tier = 'C'  # Default: assume BW
    for mod, t in MODULE_COLOR_TIER.items():
        if f'{mod}/' in p or f'{mod}\\' in p:
            tier = t
            break
    
    score = TIER_SCORES.get(tier, 15)
    
    # Path-level bonuses for color variants (e.g., Fluent Emoji has Color/Flat/HighContrast/3D)
    if '/color/' in p or '_color' in p or 'color.' in p:
        score += 30
    if '/3d/' in p or '_3d' in p or '3d.' in p:
        score += 25
    if '/flat/' in p or '_flat' in p:
        score += 20
    if 'openclipart' in p:
        score += 15  # openclipart is reliably colorful
    if 'noto' in p or 'emoji' in p:
        score += 10  # emoji assets are always colorful
    
    # Path-level penalties for monochrome variants
    if '/outline/' in p or '_outline' in p:
        score -= 20
    if '/solid/' in p and 'color' not in p:
        score -= 10  # solid black fills
    if 'high_contrast' in p or 'high-contrast' in p:
        score -= 15  # high contrast = usually BW
    if 'black_versions' in p or 'black/' in p:
        score -= 30  # explicit black-only variants
    if '/duotone/' in p:
        score -= 5   # duotone is slightly better than mono
    
    return max(score, 1)  # Never go below 1


# ─────────────────────────────────────────────────────────────
# Category Fallbacks
# ─────────────────────────────────────────────────────────────
# If no exact/partial match, we try category-based matching.

CATEGORY_MAP = {
    'emotion': ['happy', 'sad', 'angry', 'love', 'fear', 'surprise', 'joy'],
    'nature': ['sun', 'moon', 'star', 'rain', 'cloud', 'tree', 'flower'],
    'tech': ['computer', 'code', 'software', 'network', 'database', 'server'],
    'science': ['science', 'experiment', 'brain', 'dna', 'atom'],
    'business': ['money', 'chart', 'briefcase', 'office', 'meeting'],
    'health': ['health', 'medical', 'medicine', 'safety'],
    'education': ['book', 'school', 'graduate', 'study', 'learn'],
    'food': ['food', 'apple', 'coffee', 'pizza', 'cake'],
    'travel': ['car', 'airplane', 'house', 'map', 'train'],
    'communication': ['speech', 'mail', 'phone', 'speak', 'talk'],
}

# Words indicating a category
CATEGORY_KEYWORDS = {
    'feel': 'emotion', 'feeling': 'emotion', 'emotion': 'emotion', 'mood': 'emotion',
    'weather': 'nature', 'environment': 'nature', 'outdoor': 'nature',
    'technology': 'tech', 'digital': 'tech', 'software': 'tech', 'hardware': 'tech',
    'research': 'science', 'scientific': 'science', 'laboratory': 'science',
    'finance': 'business', 'economic': 'business', 'corporate': 'business',
    'medical': 'health', 'healthcare': 'health', 'hospital': 'health',
    'academic': 'education', 'teaching': 'education', 'learning': 'education',
    'cuisine': 'food', 'cooking': 'food', 'eating': 'food',
    'transport': 'travel', 'journey': 'travel', 'trip': 'travel',
    'message': 'communication', 'chat': 'communication', 'conversation': 'communication',
}


# ─────────────────────────────────────────────────────────────
# Visual Lexicon Engine
# ─────────────────────────────────────────────────────────────

class EmojiEngine:
    """
    Visual Lexicon Lookup Engine.

    Loads the pre-built JSON indexes and provides methods to find
    the best matching icon for any word or concept.
    """

    def __init__(self):
        self.emoji_index = {}
        self.heroicon_index = {}
        self.clipart_index = {}
        self._load_indexes()

    def _load_indexes(self):
        """Load the visual lexicon JSON files."""
        if os.path.isfile(EMOJI_INDEX_PATH):
            with open(EMOJI_INDEX_PATH, 'r', encoding='utf-8') as f:
                self.emoji_index = json.load(f)
        else:
            print(f"⚠️  Emoji index not found: {EMOJI_INDEX_PATH}")

        if os.path.isfile(HEROICON_INDEX_PATH):
            with open(HEROICON_INDEX_PATH, 'r', encoding='utf-8') as f:
                self.heroicon_index = json.load(f)
        else:
            print(f"⚠️  Heroicon index not found: {HEROICON_INDEX_PATH}")

        if os.path.isfile(CLIPART_INDEX_PATH):
            with open(CLIPART_INDEX_PATH, 'r', encoding='utf-8') as f:
                self.clipart_index = json.load(f)
        else:
            print(f"⚠️  Clipart index not found: {CLIPART_INDEX_PATH}")

    def lookup(self, word, prefer='vivid'):
        """
        Find the best matching icon for a word, prioritizing visual vibrancy.
        
        Scoring hierarchy:
          1. Module Color Tier (A=100, B=60, C=15) + path bonuses
          2. OpenMoji emoji (always colorful, score 90)
          3. Heroicons (BW outlines, score 10 — last resort)
          4. Exact match bonus (+200)
          5. Remapping penalty (-40)
        """
        word_lower = word.lower().strip()
        
        # Semantic remapping: abstract terms → concrete vivid icons
        remappings = {
            "safety": ["shield_color", "security", "safe_box"],
            "duplication": ["copy_color", "layers", "stack"],
            "reuse": ["recycle", "loop", "update"],
            "blueprint": ["drawing", "blueprint_color", "plan"],
            "vibrant": ["rainbow", "sparkles", "paint"],
            "foundation": ["pillar", "construction", "bricks"],
            "core": ["center", "heart", "gem"],
            "generic": ["cube", "package", "box_color"],
            "efficiency": ["rocket", "speed", "bolt"],
            "power": ["lightning", "energy", "power_color"],
            "infrastructure": ["building", "server", "network"],
            "consolidation": ["merge", "compress", "layers"],
            "abstraction": ["diamond", "prism", "crystal"],
            "specialization": ["wrench", "gear", "customize"],
            "scalability": ["chart", "growth", "expand"],
        }
        
        search_words = [word_lower]
        if word_lower in remappings:
            search_words.extend(remappings[word_lower])

        all_matches = []
        for w in search_words:
            candidates = [
                self._lookup_emoji(w),
                self._lookup_clipart(w),
                self._lookup_heroicon(w)
            ]
            
            for r in candidates:
                if r['type'] == 'none':
                    continue
                
                # VIBRANCY SCORE
                if r['type'] == 'openmoji':
                    score = 90  # OpenMoji is always colorful
                elif r['type'] == 'clipart':
                    # Use module-aware vibrancy scoring
                    score = r.get('vibrancy', _score_clipart_path(r.get('path', '')))
                elif r['type'] == 'heroicon':
                    score = 10  # BW outlines — absolute last resort
                else:
                    score = 5

                # RELEVANCE BONUS — proportional to vibrancy
                # Colorful exact matches get a big boost; BW exact matches get a small one.
                # This prevents a monochrome "sparkles.svg" from beating a colorful "sparkles_color.svg".
                if r['match'] == 'exact':
                    if score >= 80:
                        score += 200  # Colorful exact match: massive boost
                    elif score >= 40:
                        score += 80   # Mixed-tier exact match: moderate boost
                    else:
                        score += 20   # BW exact match: tiny boost (still loses to color partial)
                
                # REMAPPING PENALTY
                if w != word_lower:
                    score -= 40

                r['visual_score'] = score
                all_matches.append(r)

        if all_matches:
            all_matches.sort(key=lambda x: x['visual_score'], reverse=True)
            return all_matches[0]

        # Category/Tag fallback
        result = self._category_fallback(word_lower)
        if result['type'] != 'none':
            return result

        # Default
        return {
            'type': 'none',
            'filename': None,
            'path': None,
            'match': 'none',
            'keyword': word_lower,
        }

    def _lookup_clipart(self, word):
        """Find the most vibrant clipart match using module-aware scoring."""
        # Exact match — still score it for vibrancy
        exact_result = None
        if word in self.clipart_index:
            rel_path = self.clipart_index[word]
            exact_result = {
                'type': 'clipart',
                'filename': os.path.basename(rel_path),
                'path': f'clipart/{rel_path}',
                'match': 'exact',
                'keyword': word,
                'vibrancy': _score_clipart_path(rel_path),
            }

        # Partial word match — collect ALL matches
        partial_matches = []
        try:
            pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        except re.error:
            pattern = None
        
        if pattern:
            for key, rel_path in self.clipart_index.items():
                if pattern.search(key):
                    vibrancy = _score_clipart_path(rel_path)
                    partial_matches.append({
                        'type': 'clipart',
                        'filename': os.path.basename(rel_path),
                        'path': f'clipart/{rel_path}',
                        'match': 'partial',
                        'keyword': key,
                        'vibrancy': vibrancy,
                    })

        # Combine exact + partials and pick the most vibrant
        all_candidates = partial_matches[:]
        if exact_result:
            all_candidates.append(exact_result)
        
        if all_candidates:
            # Sort by vibrancy descending, then prefer exact matches
            all_candidates.sort(key=lambda x: (x['vibrancy'], x['match'] == 'exact'), reverse=True)
            return all_candidates[0]

        return {'type': 'none', 'filename': None, 'path': None, 'match': 'none', 'keyword': word}

    def _lookup_emoji(self, word):
        """Try to find an emoji match."""
        # Exact match
        if word in self.emoji_index:
            filename = self.emoji_index[word]
            return {
                'type': 'openmoji',
                'filename': filename,
                'path': f'icons/openmoji/{filename}',
                'match': 'exact',
                'keyword': word,
            }

        # Partial match - word as a whole word in key
        for key, filename in self.emoji_index.items():
            if re.search(rf'\b{re.escape(word)}\b', key.lower()):
                return {
                    'type': 'openmoji',
                    'filename': filename,
                    'path': f'icons/openmoji/{filename}',
                    'match': 'partial',
                    'keyword': key,
                }

        return {'type': 'none', 'filename': None, 'path': None, 'match': 'none', 'keyword': word}

    def _lookup_heroicon(self, word):
        """Try to find a heroicon match."""
        # Exact match
        if word in self.heroicon_index:
            filename = self.heroicon_index[word]
            return {
                'type': 'heroicon',
                'filename': filename,
                'path': f'icons/heroicons/{filename}',
                'match': 'exact',
                'keyword': word,
            }

        # Partial match
        for key, filename in self.heroicon_index.items():
            if re.search(rf'\b{re.escape(word)}\b', key.lower()):
                return {
                    'type': 'heroicon',
                    'filename': filename,
                    'path': f'icons/heroicons/{filename}',
                    'match': 'partial',
                    'keyword': key,
                }

        return {'type': 'none', 'filename': None, 'path': None, 'match': 'none', 'keyword': word}

    def _category_fallback(self, word):
        """Try category-based matching."""
        # Check if word hints at a category
        category = CATEGORY_KEYWORDS.get(word)

        if category and category in CATEGORY_MAP:
            # Use the first keyword from that category that exists in our index
            for fallback_word in CATEGORY_MAP[category]:
                if fallback_word in self.emoji_index:
                    filename = self.emoji_index[fallback_word]
                    return {
                        'type': 'openmoji',
                        'filename': filename,
                        'path': f'icons/openmoji/{filename}',
                        'match': 'category',
                        'keyword': fallback_word,
                    }

        return {'type': 'none', 'filename': None, 'path': None, 'match': 'none', 'keyword': word}

    def lookup_many(self, words, prefer='clipart'):
        """
        Look up multiple words at once.

        Args:
            words: List of strings.
            prefer: 'emoji' or 'heroicon'.

        Returns:
            List of lookup result dicts.
        """
        return [self.lookup(w, prefer) for w in words]

    def get_emoji_by_codepoint(self, codepoint):
        """
        Directly get an OpenMoji icon by its Unicode codepoint.

        Args:
            codepoint: e.g., '1F600' or '2764-FE0F'

        Returns:
            dict with type, filename, path, or None if not found.
        """
        filename = f'{codepoint}.png'
        filepath = os.path.join(BASE_DIR, 'data', 'icons', 'openmoji', filename)

        if os.path.isfile(filepath):
            return {
                'type': 'openmoji',
                'filename': filename,
                'path': f'icons/openmoji/{filename}',
                'match': 'codepoint',
                'keyword': codepoint,
            }
        return None

    def get_heroicon(self, name):
        """
        Directly get a Heroicon by its filename (without .svg).

        Args:
            name: e.g., 'light-bulb', 'document-text'

        Returns:
            dict with type, filename, path, or None if not found.
        """
        filename = f'{name}.svg'
        filepath = os.path.join(BASE_DIR, 'data', 'icons', 'heroicons', filename)

        if os.path.isfile(filepath):
            return {
                'type': 'heroicon',
                'filename': filename,
                'path': f'icons/heroicons/{filename}',
                'match': 'direct',
                'keyword': name,
            }
        return None

    def stats(self):
        """Return statistics about the visual lexicon."""
        return {
            'emoji_keywords': len(self.emoji_index),
            'heroicon_keywords': len(self.heroicon_index),
            'clipart_keywords': len(self.clipart_index),
            'total_vocabulary': len(self.emoji_index) + len(self.heroicon_index) + len(self.clipart_index),
            'categories': len(CATEGORY_MAP),
            'category_keywords': len(CATEGORY_KEYWORDS),
        }


# ─────────────────────────────────────────────────────────────
# Demo / Testing
# ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 60)
    print("🔍 Visual Lexicon Lookup Engine — Demo")
    print("=" * 60)

    engine = EmojiEngine()

    # Show stats
    stats = engine.stats()
    print(f"\n📊 Lexicon Stats:")
    for k, v in stats.items():
        print(f"   {k}: {v}")

    # Test lookups
    test_words = [
        'happy', 'book', 'computer', 'fire', 'idea',
        'ipod', 'robot', 'programming', 'rocket', 'canvas',
        'learning', 'technology', 'conversation',
        'xyznonexistent',
    ]

    print(f"\n🔍 Lookup Tests:")
    print(f"{'Word':<20} {'Type':<12} {'Match':<10} {'Keyword':<15} {'File'}")
    print("─" * 80)

    for word in test_words:
        result = engine.lookup(word)
        t = result['type']
        m = result['match']
        k = result['keyword'] or ''
        f = result['filename'] or '(none)'
        print(f"{word:<20} {t:<12} {m:<10} {k:<15} {f}")
