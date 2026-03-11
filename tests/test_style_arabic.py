"""
Tests for Explanation Style Variety and Arabic Language Support.
Run with: PYTHONPATH=. ./venv/bin/python3 tests/test_style_arabic.py
"""
import sys
import os

# Ensure we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_all_styles_generate_prompt():
    """Each style must return a 200 with the style keyword in the prompt."""
    for style, keyword in [('visual', 'VISUAL'), ('narrative', 'NARRATIVE'), ('frame', 'FRAME-BASED'), ('qa', 'Q&A')]:
        r = client.post('/magic-prompt/unified', json={'text': 'Test text.', 'chart_format': 'ascii', 'style': style})
        assert r.status_code == 200, f"Style [{style}] failed with {r.status_code}"
        assert keyword in r.json()['prompt'], f"Style keyword [{keyword}] not found for style [{style}]"
    print("✅ test_all_styles_generate_prompt PASSED")

def test_arabic_prompt_contains_language_instructions():
    """Arabic language selection must inject arabic instruction into prompt."""
    r = client.post('/magic-prompt/unified', json={'text': 'Test text.', 'chart_format': 'ascii', 'style': 'visual', 'language': 'arabic'})
    assert r.status_code == 200, f"Arabic request failed: {r.status_code}"
    prompt = r.json()['prompt']
    assert 'Arabic' in prompt or 'العربية' in prompt, "Arabic instruction missing from prompt"
    print("✅ test_arabic_prompt_contains_language_instructions PASSED")

def test_english_is_default():
    """No language param must default to English — prompt must NOT contain Arabic instruction."""
    r = client.post('/magic-prompt/unified', json={'text': 'Test text.', 'chart_format': 'ascii', 'style': 'visual'})
    assert r.status_code == 200
    prompt = r.json()['prompt']
    assert 'العربية' not in prompt, "Arabic instruction appeared in default (English) prompt"
    print("✅ test_english_is_default PASSED")

if __name__ == "__main__":
    try:
        test_all_styles_generate_prompt()
        print("--- Expecting Arabic tests to fail as Phase B is not yet complete ---")
        test_arabic_prompt_contains_language_instructions()
        test_english_is_default()
        print("\n🎉 All style + language tests PASSED")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
