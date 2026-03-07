import os
import sys

def check_file_charset(filepath):
    """Checks if a file contains only ASCII characters."""
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        
        non_ascii = []
        for i, b in enumerate(content):
            if b > 127:
                # Get some context around the character
                start = max(0, i - 10)
                end = min(len(content), i + 10)
                context = content[start:end]
                try:
                    char = content[i:i+4].decode('utf-8', errors='ignore')
                except:
                    char = f"Byte: {b}"
                non_ascii.append((i, char, context))
        
        return non_ascii
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []

def main():
    docs_to_check = [
        "README.md",
        "docs/PROGRESS.md",
        "docs/IMPLEMENTATION_PLAN.md"
    ]
    
    # Also check any other markdown files in docs/
    if os.path.exists("docs"):
        for f in os.listdir("docs"):
            if f.endswith(".md"):
                path = os.path.join("docs", f)
                if path not in docs_to_check:
                    docs_to_check.append(path)

    total_issues = 0
    for doc in docs_to_check:
        if not os.path.exists(doc):
            continue
            
        issues = check_file_charset(doc)
        if issues:
            print(f"FAIL: {doc} contains non-ASCII characters:")
            for pos, char, context in issues:
                print(f"  Pos {pos}: Char '{char}' | Context: {context}")
            total_issues += len(issues)
        else:
            print(f"PASS: {doc} is strictly ASCII.")

    if total_issues > 0:
        print(f"\nTotal issues found: {total_issues}")
        sys.exit(1)
    else:
        print("\nAll checked documentation files are clean.")
        sys.exit(0)

if __name__ == "__main__":
    main()
