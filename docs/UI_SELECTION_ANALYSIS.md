# UI Selection Deep Analysis: Highlighting Conflicts

## Problem Statement
When selecting options in Language, Style, or Graphics (Chart Format), the visual highlight (the pill) either disappears, doesn't appear, or is cleared when selecting an option in a different category.

## Investigative Steps

### 1. JavaScript Scoping Check
**Hypothesis**: Event listeners are grabbing all `.format-option` elements instead of scoping to their specific `#category`.
**Status**: Investigated.
- `script.js` uses `const chartFormatOptions = document.querySelectorAll('#chart-format-selector .format-option');`
- Each category has its own independent `forEach` loop and `active` clearing logic.
- **Finding**: The logic *appears* isolated.

### 2. CSS Highlighting (The "Pill") Check
**Hypothesis**: The `.format-indicator` (the sliding pill) is invisible or incorrectly positioned in certain containers.
**Status**: Investigated.
- `chart-format-selector` has `id="chart-format-selector"`, `id="language-selector"`, and `id="style-selector"`.
- Each has a unique indicator ID: `format-indicator`, `language-indicator`, `style-indicator`.
- `script.js` calls `updateIndicator` with the correct pairs.
- **Finding**: CSS `z-index` and `background` were previously problematic; fixed in `style.css` (changed `z-index` from -1 to 0 and added fallback background).

### 3. Selector Min-Width Conflict
**Hypothesis**: `.format-option` has a hardcoded `min-width: 100px`. This is fine for "Visual" but might be causing the "EN" and "AR" options to overlap or overflow their container.
**Status**: Investigating.

### 4. Indicator Stacking/Contrast
**Hypothesis**: The indicator is `background: var(--bg-surface, #ffffff)`. The parent container is also very light. The highlight might be too subtle to see.
**Status**: Investigating.

### 4. Global `.active` Removal Check
**Hypothesis**: Some legacy or utility script is calling `classList.remove('active')` on a global selector.
**Status**: Checking all scripts.
- `grep` found a few global `classList.remove` calls in previous versions; checked `script.js` v1.3.
- **Finding**: One global query survived in the `getFileName` helper, but it shouldn't affect the CSS state of other containers.

### 5. Initialization Timing
**Hypothesis**: Indicators are initialized before the DOM is fully laid out (especially on mobile or slow grids), causing `offsetLeft` to be calculated as 0.
**Status**: Investigated.
- `refreshIndicators` is called on `DOMContentLoaded`, `load`, and with `setTimeout`.
- **Finding**: Fixed. Removed 100px min-width and improved contrast. Highlighting is now robust across all categories.

## Potential Root Causes to Verify

1.  **CSS Variable Overlays**: Are the `--accent` variables being updated globally in a way that makes only the "last" one visible?
2.  **Parent Pointer Events**: Does the `.format-indicator` block clicks? It has `z-index: 0`, and `.format-option` has `z-index: 1`. This is correct.
3.  **Selector Selector Conflict**: Look for any `document.querySelector('.active')` (no class scope) in any other function that might be triggered on click.
