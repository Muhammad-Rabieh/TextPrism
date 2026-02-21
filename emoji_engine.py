#!/usr/bin/env python3
"""
Visual Lexicon Lookup Engine (emoji_engine.py)
===============================================
Given a word or concept, find the best matching icon from the Visual Lexicon.
This is the core of Iconographic Annotation — pairing concepts with visuals.

Lookup Strategy:
1. Exact match in emoji index
2. Exact match in heroicon index
3. Partial/substring match in emoji index
4. Partial/substring match in heroicon index
5. Category-based fallback
6. Default icon

Part of the Text Explain Project.
"""

import json
import os

# ─────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
EMOJI_INDEX_PATH = os.path.join(DATA_DIR, 'emoji_index.json')
HEROICON_INDEX_PATH = os.path.join(DATA_DIR, 'heroicon_index.json')


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
        self._load_indexes()

    def _load_indexes(self):
        """Load the visual lexicon JSON files."""
        if os.path.isfile(EMOJI_INDEX_PATH):
            with open(EMOJI_INDEX_PATH, 'r', encoding='utf-8') as f:
                self.emoji_index = json.load(f)
        else:
            print(f"⚠️  Emoji index not found: {EMOJI_INDEX_PATH}")
            print("   Run 'python build_index.py' first to build the visual lexicon.")

        if os.path.isfile(HEROICON_INDEX_PATH):
            with open(HEROICON_INDEX_PATH, 'r', encoding='utf-8') as f:
                self.heroicon_index = json.load(f)
        else:
            print(f"⚠️  Heroicon index not found: {HEROICON_INDEX_PATH}")
            print("   Run 'python build_index.py' first to build the visual lexicon.")

    def lookup(self, word, prefer='emoji'):
        """
        Find the best matching icon for a word.

        Args:
            word: The word or concept to look up.
            prefer: Which icon type to prefer - 'emoji' or 'heroicon'.

        Returns:
            dict with keys:
                - type: 'openmoji' | 'heroicon' | 'none'
                - filename: The icon filename
                - path: Relative path to the icon file
                - match: 'exact' | 'partial' | 'category' | 'default'
                - keyword: The matched keyword
        """
        word_lower = word.lower().strip()

        if prefer == 'emoji':
            # Try emoji first, then heroicon
            result = self._lookup_emoji(word_lower)
            if result['type'] != 'none':
                return result
            result = self._lookup_heroicon(word_lower)
            if result['type'] != 'none':
                return result
        else:
            # Try heroicon first, then emoji
            result = self._lookup_heroicon(word_lower)
            if result['type'] != 'none':
                return result
            result = self._lookup_emoji(word_lower)
            if result['type'] != 'none':
                return result

        # Category fallback
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

    def _lookup_emoji(self, word):
        """Try to find an emoji match."""
        # Exact match
        if word in self.emoji_index:
            filename = self.emoji_index[word]
            return {
                'type': 'openmoji',
                'filename': filename,
                'path': f'openmoji-72x72-color/{filename}',
                'match': 'exact',
                'keyword': word,
            }

        # Partial match (word is substring of a key, or key is substring of word)
        # Only match if the key is at least 3 chars to avoid false positives
        for key, filename in self.emoji_index.items():
            if len(key) >= 3 and (word in key or key in word):
                return {
                    'type': 'openmoji',
                    'filename': filename,
                    'path': f'openmoji-72x72-color/{filename}',
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
                'path': f'heroicons_24x24/{filename}',
                'match': 'exact',
                'keyword': word,
            }

        # Partial match
        for key, filename in self.heroicon_index.items():
            if len(key) >= 3 and (word in key or key in word):
                return {
                    'type': 'heroicon',
                    'filename': filename,
                    'path': f'heroicons_24x24/{filename}',
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
                        'path': f'openmoji-72x72-color/{filename}',
                        'match': 'category',
                        'keyword': fallback_word,
                    }

        return {'type': 'none', 'filename': None, 'path': None, 'match': 'none', 'keyword': word}

    def lookup_many(self, words, prefer='emoji'):
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
        filepath = os.path.join(BASE_DIR, 'openmoji-72x72-color', filename)

        if os.path.isfile(filepath):
            return {
                'type': 'openmoji',
                'filename': filename,
                'path': f'openmoji-72x72-color/{filename}',
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
        filepath = os.path.join(BASE_DIR, 'heroicons_24x24', filename)

        if os.path.isfile(filepath):
            return {
                'type': 'heroicon',
                'filename': filename,
                'path': f'heroicons_24x24/{filename}',
                'match': 'direct',
                'keyword': name,
            }
        return None

    def stats(self):
        """Return statistics about the visual lexicon."""
        return {
            'emoji_keywords': len(self.emoji_index),
            'heroicon_keywords': len(self.heroicon_index),
            'total_vocabulary': len(self.emoji_index) + len(self.heroicon_index),
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
        'document', 'star', 'rocket', 'pizza', 'brain',
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
