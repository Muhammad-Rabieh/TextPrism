import re

def normalize_ascii(text):
    """Clean up and pad ASCII art blocks to maintain structural integrity."""
    if not text:
        return ""
    
    # Handle literal '\n' strings that some LLMs emit within JSON
    if '\\n' in text:
        text = text.replace('\\n', '\n')
    
    # Expand tabs to spaces
    text = text.expandtabs(4)
    lines = text.splitlines()
    if not lines:
        return ""
        
    # Trim leading/trailing EMPTY lines but preserve internal ones
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
        
    if not lines:
        return ""

    # Remove common indentation (dedent)
    non_empty_lines = [l for l in lines if l.strip()]
    if non_empty_lines:
        common_indent = min(len(l) - len(l.lstrip()) for l in non_empty_lines)
        if common_indent > 0:
            lines = [l[common_indent:] if len(l) >= common_indent else l.lstrip() for l in lines]
    
    # Pad all lines to the same length (fixes broken box borders if LLM trimmed spaces)
    # We pad with a bit of extra space to ensure borders aren't at the very edge
    max_len = max(len(l) for l in lines)
    lines = [l.ljust(max_len) for l in lines]
    
    return "\n".join(lines)
