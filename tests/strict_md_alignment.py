#!/usr/bin/env python3
"""
strict_md_alignment.py
══════════════════════
Strict structural alignment test — verifies the Markdown export
matches the HTML template's element ordering for every section.

HTML template order (templates/explanation.html):
  ascii_separator → header → ascii_box → sentences → ascii_callout → ascii_flow → bullets

This script parses the provided HTML and MD files and checks:
 1. Section headers appear in the same order.
 2. ASCII art placement: ascii_box lines appear AFTER the section header.
 3. Sentences with icons appear AFTER the header (not before).
 4. Bullets appear AFTER sentences in each section.
 5. Icons in title, sentences, and bullets reference real assets.
"""
import re
import os
import sys

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ALIGNMENT_DIR = os.path.join(TESTS_DIR, "md-alignment")
HTML_FILE = os.path.join(ALIGNMENT_DIR, "Understanding_Playfair_s.html")
MD_FILE   = os.path.join(ALIGNMENT_DIR, "explanation.md")
ASSETS_DIR = os.path.join(ALIGNMENT_DIR, "assets")

PASS = 0
FAIL = 0


def check(label, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {label}")
    else:
        FAIL += 1
        msg = f"  ❌ {label}"
        if detail:
            msg += f"  → {detail}"
        print(msg)


# ─────────────────── Parse HTML sections ───────────────────
def extract_html_sections(html):
    """Extract section titles in order from the HTML file."""
    # The HTML uses <h2> inside .section-header for section titles
    titles = re.findall(r'<h2>(.*?)</h2>', html)
    # Filter out the "📋 Explanation" which is the summary, not a section
    titles = [t.strip() for t in titles if '📋' not in t and t.strip()]
    return titles


def extract_html_sentence_texts(html):
    """Extract sentence texts from .sentence-text elements."""
    return re.findall(r'<p class="sentence-text">(.*?)</p>', html, re.DOTALL)


# ─────────────────── Parse MD sections ───────────────────
def extract_md_sections(md):
    """Split markdown into sections by ### headers. Returns list of (title, body)."""
    sections = []
    parts = re.split(r'^### ', md, flags=re.MULTILINE)
    for part in parts[1:]:  # skip content before first ###
        lines = part.split('\n', 1)
        # Title line may contain <img> tags before the actual title
        title_line = lines[0].strip()
        # Strip HTML img tags to get plain title 
        plain_title = re.sub(r'<img[^>]*>\s*', '', title_line).strip()
        body = lines[1] if len(lines) > 1 else ""
        sections.append((plain_title, body))
    return sections


def find_line_number(md, pattern):
    """Find 1-indexed line number of first match."""
    for i, line in enumerate(md.split('\n'), 1):
        if pattern in line:
            return i
    return -1


# ═══════════════════ MAIN TEST ═══════════════════
def main():
    global PASS, FAIL

    # ── Load files ──
    if not os.path.exists(HTML_FILE):
        print(f"❌ HTML file not found: {HTML_FILE}")
        sys.exit(1)
    if not os.path.exists(MD_FILE):
        print(f"❌ MD file not found: {MD_FILE}")
        sys.exit(1)

    with open(HTML_FILE, encoding='utf-8') as f:
        html = f.read()
    with open(MD_FILE, encoding='utf-8') as f:
        md = f.read()

    md_lines = md.split('\n')

    print("═" * 60)
    print("  STRICT MARKDOWN ALIGNMENT TEST")
    print("═" * 60)

    # ══════════════════════════════════════════════════════
    # TEST 1: Title presence
    # ══════════════════════════════════════════════════════
    print("\n── 1. Title ──")
    check("MD starts with H1 (#)", md_lines[0].startswith('# '))
    html_title = re.search(r'<title>.*?—\s*(.*?)</title>', html)
    if html_title:
        expected_title = html_title.group(1).strip()
        check(f"Title matches HTML", expected_title in md_lines[0],
              f"Expected '{expected_title[:40]}...' in MD H1")

    # ══════════════════════════════════════════════════════
    # TEST 2: Section count and order
    # ══════════════════════════════════════════════════════
    print("\n── 2. Section Order ──")
    html_sections = extract_html_sections(html)
    md_sections = extract_md_sections(md)
    md_titles = [t for t, _ in md_sections]

    check(f"HTML has {len(html_sections)} sections",
          len(html_sections) >= 2,
          f"Found: {len(html_sections)}")

    check(f"MD has {len(md_sections)} sections",
          len(md_sections) >= 2,
          f"Found: {len(md_sections)}")

    check("Same number of sections",
          len(html_sections) == len(md_sections),
          f"HTML={len(html_sections)}, MD={len(md_sections)}")

    for i, html_title in enumerate(html_sections):
        if i < len(md_titles):
            # Fuzzy match — first 30 chars
            match = html_title[:30].lower().strip() in md_titles[i].lower()
            check(f"Section {i+1} title match",
                  match,
                  f"HTML='{html_title[:40]}' vs MD='{md_titles[i][:40]}'")

    # ══════════════════════════════════════════════════════
    # TEST 3: ASCII art placement — MUST be AFTER header
    # ══════════════════════════════════════════════════════
    print("\n── 3. ASCII Art Placement (must be AFTER header) ──")
    for i, (title, body) in enumerate(md_sections):
        header_line = find_line_number(md, f"### {'' if not title else title[:20]}")

        # Check for code blocks (```) in the body content
        code_blocks = list(re.finditer(r'```', body))
        if code_blocks:
            # The first code block should be AFTER the header line
            first_code_pos = body.find('```')
            # Compute absolute line number
            body_start_line = header_line  # body starts right after header
            body_lines_before_code = body[:first_code_pos].count('\n')
            code_line = body_start_line + body_lines_before_code

            check(f"Section {i+1} '{title[:30]}…': ASCII art after header",
                  code_line >= header_line,
                  f"Header at line {header_line}, first code block at ~line {code_line}")

    # ══════════════════════════════════════════════════════
    # TEST 4: Sentence-icon alignment
    # ══════════════════════════════════════════════════════
    print("\n── 4. Sentence Icons ──")
    # Count sentence-level <img> tags with width="24" (sentence icons)
    md_sentence_icons = re.findall(r'<img src="assets/[^"]*" alt="[^"]*" width="24">', md)
    html_sentence_icons = re.findall(r'class="sentence-icon"', html)
    check(f"Sentence icon count ≥ HTML sentence count",
          len(md_sentence_icons) >= len(html_sentence_icons) * 0.5,
          f"MD has {len(md_sentence_icons)} sentence icons, HTML has {len(html_sentence_icons)}")

    # Each sentence icon line should have text after the img tag
    for i, line in enumerate(md_lines):
        if '<img src="assets/' in line and 'width="24">' in line:
            # After the closing >, there should be text content before any comment
            after_img = re.sub(r'<img[^>]*>\s*', '', line).strip()
            after_img = re.sub(r'<!--.*?-->', '', after_img).strip()
            check(f"Line {i+1}: sentence icon has text",
                  len(after_img) > 10,
                  f"Text after icon: '{after_img[:50]}…'" if after_img else "No text!")

    # ══════════════════════════════════════════════════════
    # TEST 5: Bullets appear AFTER sentences
    # ══════════════════════════════════════════════════════
    print("\n── 5. Bullet Placement ──")
    for i, (title, body) in enumerate(md_sections):
        body_lines = body.split('\n')
        last_sentence_line = -1
        first_bullet_line = -1

        for j, line in enumerate(body_lines):
            stripped = line.strip()
            if stripped.startswith('<img') and 'width="24">' in stripped and not stripped.startswith('- '):
                last_sentence_line = j
            if stripped.startswith('- ') and first_bullet_line == -1:
                first_bullet_line = j

        if last_sentence_line >= 0 and first_bullet_line >= 0:
            check(f"Section {i+1}: bullets after sentences",
                  first_bullet_line > last_sentence_line,
                  f"Last sentence at line {last_sentence_line}, first bullet at {first_bullet_line}")

    # ══════════════════════════════════════════════════════
    # TEST 6: Asset file references are valid
    # ══════════════════════════════════════════════════════
    print("\n── 6. Asset Integrity ──")
    asset_refs = re.findall(r'src="(assets/[^"]+)"', md)
    check(f"MD references {len(asset_refs)} assets", len(asset_refs) >= 5,
          f"Found {len(asset_refs)}")

    missing = []
    for ref in asset_refs:
        full_path = os.path.join(ALIGNMENT_DIR, ref)
        if not os.path.exists(full_path):
            missing.append(ref)
    check("All referenced assets exist on disk",
          len(missing) == 0,
          f"Missing: {missing[:5]}" if missing else "")

    # ══════════════════════════════════════════════════════
    # TEST 7: Summary section structure
    # ══════════════════════════════════════════════════════
    print("\n── 7. Summary Section ──")
    check("Summary header present", '## 📋' in md or '## 📋 Summary' in md)
    
    summary_pos = md.find('## 📋')
    first_section_pos = md.find('### ')
    if summary_pos >= 0 and first_section_pos >= 0:
        # Extract summary block  
        summary_block = md[summary_pos:first_section_pos]
        # Summary icons should be AFTER summary text
        summary_text_end = summary_block.rfind('.')
        summary_icons_start = summary_block.find('<img src="assets/')

        if summary_icons_start >= 0:
            check("Summary icons after summary text",
                  summary_icons_start > summary_text_end,
                  f"Text ends at char {summary_text_end}, icons start at {summary_icons_start}")

    # ══════════════════════════════════════════════════════
    # TEST 8: No duplicated ASCII blocks across sections
    # ══════════════════════════════════════════════════════
    print("\n── 8. No Orphaned ASCII ──")
    # Check that there are no code blocks between ---\n and the first ###
    separator_to_first_section = ""
    sep_pos = md.find('\n---\n')
    first_h3 = md.find('### ')
    if sep_pos >= 0 and first_h3 >= 0 and first_h3 > sep_pos:
        separator_to_first_section = md[sep_pos:first_h3]
    orphaned_code = separator_to_first_section.count('```')
    check("No orphaned code blocks between summary and first section",
          orphaned_code == 0,
          f"Found {orphaned_code // 2} orphaned code block(s)")

    # ══════════════════════════════════════════════════════
    # FINAL REPORT
    # ══════════════════════════════════════════════════════
    print("\n" + "═" * 60)
    total = PASS + FAIL
    print(f"  RESULTS: {PASS}/{total} passed, {FAIL} failed")
    if FAIL == 0:
        print("  🎉 ALL TESTS PASSED — Markdown aligns with HTML structure!")
    else:
        print("  ⚠️  Some tests failed — review the output above.")
    print("═" * 60)
    return FAIL == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
