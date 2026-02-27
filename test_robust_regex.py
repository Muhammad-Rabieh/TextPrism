import re

text1 = """
{ "sections": [] }

== ASCII SECTION 1 ==
```text
  +-------+
  | PC 1  |
  +-------+
```

### ASCII SECTION 2 ###
```
    ___
  /     \  
 | World |
  \ ___ /
```
"""

# Test a highly resilient extraction approach
ascii_blocks = {}

# 1. Strip markdown fences around sections globally to make it easier, OR handle them per block.
# Let's handle them per block.

# Flexible regex: matches == ASCII SECTION 1 == or ### ASCII SECTION 1 ### or **ASCII SECTION 1**
pattern = re.compile(r'(?:=+|-+|#+|\*\*)\s*ASCII SECTION\s+(\d+)\s*(?:=+|-+|#+|\*\*)', flags=re.IGNORECASE)

parts = pattern.split(text1)
print("Parts:", parts)
for i in range(1, len(parts) - 1, 2):
    sec_num = int(parts[i].strip())
    block = parts[i+1].strip('\r\n')
    
    # Remove markdown code block wrappers if they exist
    block = re.sub(r'^```[\w]*\s*\n', '', block)
    block = re.sub(r'\n```\s*$', '', block)
    
    ascii_blocks[sec_num - 1] = block

print("Extracted Blocks:")
for k, v in ascii_blocks.items():
    print(f"--- Block {k} ---")
    print(v)
