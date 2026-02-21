#!/usr/bin/env python3
"""
SHAPE_IT ASCII Art Engine
=========================
Programmatic generation of geometric shapes, visual containers, borders,
flowcharts, and decorative elements using ASCII and Unicode box-drawing characters.

Part of the Text Explain Project — Visual Lexicon for Semantic Text Annotation.
"""

try:
    import pyfiglet
    HAS_PYFIGLET = True
except ImportError:
    HAS_PYFIGLET = False


# ─────────────────────────────────────────────────────────────
# Box-Drawing Character Sets
# ─────────────────────────────────────────────────────────────

BOX_STYLES = {
    'single': {
        'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘',
        'h': '─', 'v': '│', 'lm': '├', 'rm': '┤',
        'tm': '┬', 'bm': '┴', 'cross': '┼',
    },
    'double': {
        'tl': '╔', 'tr': '╗', 'bl': '╚', 'br': '╝',
        'h': '═', 'v': '║', 'lm': '╠', 'rm': '╣',
        'tm': '╦', 'bm': '╩', 'cross': '╬',
    },
    'rounded': {
        'tl': '╭', 'tr': '╮', 'bl': '╰', 'br': '╯',
        'h': '─', 'v': '│', 'lm': '├', 'rm': '┤',
        'tm': '┬', 'bm': '┴', 'cross': '┼',
    },
    'heavy': {
        'tl': '┏', 'tr': '┓', 'bl': '┗', 'br': '┛',
        'h': '━', 'v': '┃', 'lm': '┣', 'rm': '┫',
        'tm': '┳', 'bm': '┻', 'cross': '╋',
    },
    'ascii': {
        'tl': '+', 'tr': '+', 'bl': '+', 'br': '+',
        'h': '-', 'v': '|', 'lm': '+', 'rm': '+',
        'tm': '+', 'bm': '+', 'cross': '+',
    },
}

ARROW_CHARS = {
    'right': '►', 'left': '◄', 'up': '▲', 'down': '▼',
    'right_thin': '→', 'left_thin': '←', 'up_thin': '↑', 'down_thin': '↓',
    'right_double': '»', 'left_double': '«',
}


# ─────────────────────────────────────────────────────────────
# 1. Bordered Boxes
# ─────────────────────────────────────────────────────────────

def draw_box(text, style='double', padding=1, min_width=0):
    """
    Wrap text in a bordered box.

    Args:
        text: String or list of strings (multiline).
        style: Box style - 'single', 'double', 'rounded', 'heavy', 'ascii'.
        padding: Horizontal padding inside box.
        min_width: Minimum width of the box interior.

    Returns:
        String with the bordered box.
    """
    s = BOX_STYLES.get(style, BOX_STYLES['double'])
    lines = text.split('\n') if isinstance(text, str) else list(text)

    # Calculate width
    max_len = max(len(line) for line in lines) if lines else 0
    width = max(max_len + padding * 2, min_width)

    result = []
    # Top border
    result.append(s['tl'] + s['h'] * width + s['tr'])
    # Content lines
    for line in lines:
        padded = ' ' * padding + line + ' ' * (width - len(line) - padding)
        result.append(s['v'] + padded + s['v'])
    # Bottom border
    result.append(s['bl'] + s['h'] * width + s['br'])

    return '\n'.join(result)


def draw_titled_box(title, body, style='double', padding=1):
    """
    Draw a box with a title header and body content.

    Args:
        title: Title string for the header.
        body: Body text (string or list of strings).
        style: Box style.
        padding: Horizontal padding.

    Returns:
        String with the titled box.
    """
    s = BOX_STYLES.get(style, BOX_STYLES['double'])
    body_lines = body.split('\n') if isinstance(body, str) else list(body)

    max_len = max(len(title), max(len(l) for l in body_lines) if body_lines else 0)
    width = max_len + padding * 2

    result = []
    # Top border + title
    result.append(s['tl'] + s['h'] * width + s['tr'])
    padded_title = ' ' * padding + title + ' ' * (width - len(title) - padding)
    result.append(s['v'] + padded_title + s['v'])
    # Middle divider
    result.append(s['lm'] + s['h'] * width + s['rm'])
    # Body lines
    for line in body_lines:
        padded = ' ' * padding + line + ' ' * (width - len(line) - padding)
        result.append(s['v'] + padded + s['v'])
    # Bottom border
    result.append(s['bl'] + s['h'] * width + s['br'])

    return '\n'.join(result)


# ─────────────────────────────────────────────────────────────
# 2. Geometric Shapes
# ─────────────────────────────────────────────────────────────

def draw_pyramid(height=5, char='*', fill=True):
    """Generate a pyramid shape."""
    lines = []
    for i in range(1, height + 1):
        spaces = ' ' * (height - i)
        if fill:
            stars = char * (2 * i - 1)
        else:
            if i == 1 or i == height:
                stars = char * (2 * i - 1)
            else:
                stars = char + ' ' * (2 * i - 3) + char
        lines.append(spaces + stars)
    return '\n'.join(lines)


def draw_diamond(height=5, char='*'):
    """Generate a diamond shape. Height should be odd for symmetry."""
    if height % 2 == 0:
        height += 1
    half = height // 2
    lines = []
    # Top half
    for i in range(half + 1):
        spaces = ' ' * (half - i)
        stars = char * (2 * i + 1)
        lines.append(spaces + stars)
    # Bottom half
    for i in range(half - 1, -1, -1):
        spaces = ' ' * (half - i)
        stars = char * (2 * i + 1)
        lines.append(spaces + stars)
    return '\n'.join(lines)


def draw_triangle(height=5, char='*', direction='up'):
    """Generate a triangle pointing in a direction."""
    lines = []
    if direction == 'up':
        for i in range(1, height + 1):
            spaces = ' ' * (height - i)
            lines.append(spaces + char * (2 * i - 1))
    elif direction == 'down':
        for i in range(height, 0, -1):
            spaces = ' ' * (height - i)
            lines.append(spaces + char * (2 * i - 1))
    elif direction == 'right':
        for i in range(1, height + 1):
            lines.append(char * i)
        for i in range(height - 1, 0, -1):
            lines.append(char * i)
    elif direction == 'left':
        for i in range(1, height + 1):
            spaces = ' ' * (height - i)
            lines.append(spaces + char * i)
        for i in range(height - 1, 0, -1):
            spaces = ' ' * (height - i)
            lines.append(spaces + char * i)
    return '\n'.join(lines)


# ─────────────────────────────────────────────────────────────
# 3. Flowchart Diagrams
# ─────────────────────────────────────────────────────────────

def draw_flowchart(steps, style='single', arrow='────►', vertical=False):
    """
    Generate a flowchart (horizontal by default, or vertical).
    """
    if not steps:
        return ''

    if vertical:
        return draw_vertical_flow(steps, style)

    s = BOX_STYLES.get(style, BOX_STYLES['single'])
    # Truncate labels if too long to keep flowchart manageable
    short_steps = []
    for step in steps:
        if len(step) > 20:
            short_steps.append(step[:17] + '...')
        else:
            short_steps.append(step)
            
    # Handle multi-line or long steps
    step_lines = [step.split('\n') for step in short_steps]
    max_h = max(len(lines) for lines in step_lines)
    max_w = max(max(len(l) for l in lines) for lines in step_lines)
    box_width = max_w + 2

    lines_out = [[] for _ in range(max_h + 2)] # top, body..., bot

    for i, step in enumerate(steps):
        curr_lines = step_lines[i]
        # Top
        lines_out[0].append(s['tl'] + s['h'] * box_width + s['tr'])
        # Body
        for j in range(max_h):
            text = curr_lines[j] if j < len(curr_lines) else ""
            padded = ' ' + text + ' ' * (box_width - len(text) - 1)
            lines_out[j+1].append(s['v'] + padded + s['v'])
        # Bottom
        lines_out[-1].append(s['bl'] + s['h'] * box_width + s['br'])

        if i < len(steps) - 1:
            # Arrows
            lines_out[0].append(' ' * len(arrow))
            arrow_row = (max_h + 2) // 2
            for j in range(max_h):
                if j+1 == arrow_row:
                    lines_out[j+1].append(arrow)
                else:
                    lines_out[j+1].append(' ' * len(arrow))
            lines_out[-1].append(' ' * len(arrow))

    return '\n'.join([''.join(parts) for parts in lines_out])


def draw_vertical_flow(steps, style='single'):
    """
    Generate a vertical flowchart.

    Args:
        steps: List of strings.
        style: Box style.

    Returns:
        String with vertical flow.
    """
    s = BOX_STYLES.get(style, BOX_STYLES['single'])
    max_len = max(len(step) for step in steps)
    box_width = max_len + 2
    center = (box_width + 2) // 2

    result = []
    for i, step in enumerate(steps):
        padded = ' ' + step + ' ' * (box_width - len(step) - 1)
        result.append(s['tl'] + s['h'] * box_width + s['tr'])
        result.append(s['v'] + padded + s['v'])
        result.append(s['bl'] + s['h'] * box_width + s['br'])
        if i < len(steps) - 1:
            result.append(' ' * center + '│')
            result.append(' ' * center + '▼')

    return '\n'.join(result)


# ─────────────────────────────────────────────────────────────
# 4. Separators and Banners
# ─────────────────────────────────────────────────────────────

def draw_separator(text='', width=50, style='double', fill_char='░'):
    """
    Generate a decorative section separator.

    Args:
        text: Optional text to center in the separator.
        width: Total width.
        style: 'double', 'single', 'heavy', 'wave', 'dots'.
        fill_char: Character for filled sections.

    Returns:
        String with the separator.
    """
    s = BOX_STYLES.get(style, BOX_STYLES['double'])
    h = s['h']

    if not text:
        return h * width

    lines = []
    lines.append(h * width)
    # Center text with fill
    text_with_pad = f' {text} '
    side_len = (width - len(text_with_pad)) // 2
    centered = fill_char * side_len + text_with_pad + fill_char * side_len
    if len(centered) < width:
        centered += fill_char
    lines.append(centered)
    lines.append(h * width)

    return '\n'.join(lines)


def draw_banner(text, font='slant'):
    """
    Generate a large text banner using pyfiglet.

    Args:
        text: Text to render as ASCII art.
        font: pyfiglet font name ('slant', 'banner3', 'big', 'block', 'standard', etc.)

    Returns:
        String with the ASCII art banner.
    """
    if HAS_PYFIGLET:
        try:
            return pyfiglet.figlet_format(text, font=font).rstrip()
        except pyfiglet.FontNotFound:
            return pyfiglet.figlet_format(text, font='standard').rstrip()
    else:
        # Fallback: simple uppercase in a box
        return draw_box(f'  {text.upper()}  ', style='heavy')


# ─────────────────────────────────────────────────────────────
# 5. Callout Bubbles
# ─────────────────────────────────────────────────────────────

def draw_callout(text, pointer='left'):
    """
    Generate a speech/thought callout bubble.

    Args:
        text: Content of the callout.
        pointer: Direction of the pointer ('left', 'right', 'down').

    Returns:
        String with the callout bubble.
    """
    lines = text.split('\n') if isinstance(text, str) else list(text)
    max_len = max(len(l) for l in lines)
    width = max_len + 2

    result = []
    result.append(' .' + '─' * width + '.')
    for line in lines:
        padded = ' ' + line + ' ' * (width - len(line) - 1)
        result.append('(' + padded + ' )')
    result.append(' `' + '─' * width + "'")

    if pointer == 'down':
        center = width // 2 + 1
        result.append(' ' * center + '\\')
        result.append(' ' * (center + 1) + '★')
    elif pointer == 'left':
        result.append('  /')
        result.append(' ★')
    elif pointer == 'right':
        result.append(' ' * (width + 1) + '\\')
        result.append(' ' * (width + 2) + '★')

    return '\n'.join(result)


# ─────────────────────────────────────────────────────────────
# 6. ASCII Tables
# ─────────────────────────────────────────────────────────────

def draw_table(headers, rows, style='single'):
    """
    Generate an ASCII table with borders.

    Args:
        headers: List of header strings.
        rows: List of lists (each row is a list of cell values).
        style: Box style.

    Returns:
        String with the bordered table.
    """
    s = BOX_STYLES.get(style, BOX_STYLES['single'])

    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    def make_row(cells, sep_v):
        parts = []
        for i, cell in enumerate(cells):
            w = col_widths[i] if i < len(col_widths) else len(str(cell))
            parts.append(' ' + str(cell) + ' ' * (w - len(str(cell))) + ' ')
        return sep_v + sep_v.join(parts) + sep_v

    def make_separator(left, mid, right, h_char):
        parts = []
        for w in col_widths:
            parts.append(h_char * (w + 2))
        return left + mid.join(parts) + right

    result = []
    # Top border
    result.append(make_separator(s['tl'], s['tm'], s['tr'], s['h']))
    # Header row
    result.append(make_row(headers, s['v']))
    # Header separator
    result.append(make_separator(s['lm'], s['cross'], s['rm'], s['h']))
    # Data rows
    for row in rows:
        # Pad row to match header count
        padded_row = list(row) + [''] * (len(headers) - len(row))
        result.append(make_row(padded_row, s['v']))
    # Bottom border
    result.append(make_separator(s['bl'], s['bm'], s['br'], s['h']))

    return '\n'.join(result)


# ─────────────────────────────────────────────────────────────
# 7. Arrows
# ─────────────────────────────────────────────────────────────

def draw_arrow(direction='right', length=10, label=''):
    """Generate a directional arrow with optional label."""
    if direction == 'right':
        line = '─' * length + '►'
        if label:
            pad = (length - len(label)) // 2
            label_line = ' ' * pad + label
            return label_line + '\n' + line
        return line
    elif direction == 'left':
        line = '◄' + '─' * length
        if label:
            pad = (length - len(label)) // 2
            label_line = ' ' * (pad + 1) + label
            return label_line + '\n' + line
        return line
    elif direction == 'down':
        result = []
        if label:
            result.append(label)
        for _ in range(length):
            result.append('│')
        result.append('▼')
        return '\n'.join(result)
    elif direction == 'up':
        result = ['▲']
        for _ in range(length):
            result.append('│')
        if label:
            result.append(label)
        return '\n'.join(result)
    return ''


# ─────────────────────────────────────────────────────────────
# 8. Hierarchy / Pyramid with Labels
# ─────────────────────────────────────────────────────────────

def draw_hierarchy(items, width=40):
    """
    Draw a hierarchy pyramid with labeled levels.

    Args:
        items: List of strings, from top (most important) to bottom.
        width: Maximum width of the base.

    Returns:
        String with the pyramid.
    """
    n = len(items)
    if n == 0:
        return ''

    result = []
    for i, item in enumerate(items):
        level_width = int(width * (i + 1) / n)
        if level_width % 2 == 0:
            level_width += 1

        indent = (width - level_width) // 2

        if i == 0:
            # Peak
            result.append(' ' * (width // 2) + '/\\')
        else:
            result.append(' ' * indent + '/' + '─' * (level_width - 2) + '\\')

        # Label centered
        label = item[:level_width - 4] if len(item) > level_width - 4 else item
        label_pad = (level_width - len(label)) // 2
        label_line = ' ' * indent + '/' + ' ' * (label_pad - 1) + label
        label_line += ' ' * (level_width - label_pad - len(label) - 1) + '\\'
        result.append(label_line)

    # Base
    result.append('/' + '─' * (width - 2) + '\\')

    return '\n'.join(result)


# ─────────────────────────────────────────────────────────────
# 9. Advanced Layouts
# ─────────────────────────────────────────────────────────────

def draw_gantt(items, width=40):
    """
    Generate a simple ASCII Gantt chart.
    items: List of (label, start_percent, duration_percent)
    """
    result = []
    # Header
    result.append("Timeline " + " " * (width - 16) + "0%   50%  100%")
    result.append("┌" + "─" * width + "┐")

    for label, start, duration in items:
        # Scale percentages to width
        s_pos = int((start / 100) * width)
        d_len = int((duration / 100) * width)
        if d_len < 1: d_len = 1

        bar = " " * s_pos + "█" * d_len + " " * (width - s_pos - d_len)
        label_text = (label[:10] + "..") if len(label) > 12 else label
        result.append(f"│{bar}│ {label_text}")

    result.append("└" + "─" * width + "┘")
    return "\n".join(result)


def draw_progress(percent, label="", width=30):
    """Generate a progress bar."""
    filled = int((percent / 100) * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"{label + ' ' if label else ''}[{bar}] {percent}%"


def draw_side_by_side(left_title, left_text, right_title, right_text, style='single'):
    """Draw two boxes next to each other for comparison."""
    left_box = draw_titled_box(left_title, left_text, style=style, padding=1).split('\n')
    right_box = draw_titled_box(right_title, right_text, style=style, padding=1).split('\n')

    # Pad height
    max_h = max(len(left_box), len(right_box))
    while len(left_box) < max_h: left_box.append(" " * len(left_box[0]))
    while len(right_box) < max_h: right_box.append(" " * len(right_box[0]))

    result = []
    for l, r in zip(left_box, right_box):
        result.append(l + "   " + r)

    return "\n".join(result)


def draw_tree(root, children):
    """Generate a simple tree structure."""
    result = [f" {root}"]
    for i, child in enumerate(children):
        connector = " └── " if i == len(children) - 1 else " ├── "
        result.append(connector + child)
    return "\n".join(result)


# ─────────────────────────────────────────────────────────────
# Demo / Testing
# ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 60)
    print("SHAPE_IT ASCII Art Engine — Demo")
    print("=" * 60)

    print("\n--- 1. Advanced: Gantt Chart ---")
    print(draw_gantt([
        ("Phase 1", 0, 30),
        ("Phase 2", 30, 40),
        ("Phase 3", 70, 30)
    ]))

    print("\n--- 2. Advanced: Progress ---")
    print(draw_progress(65, "Deployment"))

    print("\n--- 3. Advanced: Comparison ---")
    print(draw_side_by_side("Option A", "Low cost\nSlow speed", "Option B", "High cost\nFast speed"))

    print("\n--- 4. Advanced: Tree ---")
    print(draw_tree("Project Root", ["Assets", "Backend", "Frontend", "Docs"]))

    print("\n--- Original Elements ---")
    print("\n--- Bordered Box (double) ---")
    print(draw_box("Hello, World!\nThis is a visual explanation.", style='double'))

    print("\n--- Flowchart (horizontal) ---")
    print(draw_flowchart(['Input', 'Process', 'Output'], style='single'))

    print("\n--- 6. Vertical Flow ---")
    print(draw_vertical_flow(['Step 1', 'Step 2', 'Step 3'], style='rounded'))

    print("\n--- 7. Separator ---")
    print(draw_separator("Chapter 1: Introduction", width=45))

    print("\n--- 8. Banner ---")
    print(draw_banner("Hello", font='slant'))

    print("\n--- 9. Callout ---")
    print(draw_callout("This is a key point!", pointer='down'))

    print("\n--- 10. Table ---")
    print(draw_table(
        ['Term', 'Meaning', 'Icon'],
        [['API', 'Interface', '🔌'], ['LLM', 'AI Model', '🤖'], ['HTML', 'Markup', '📄']]
    ))

    print("\n--- 11. Arrow ---")
    print(draw_arrow('right', 20, 'data flow'))

    print("\n--- 12. Hierarchy ---")
    print(draw_hierarchy(['Critical', 'Important', 'Nice to have', 'Optional']))
