import re

text1 = """
{ "sections": [] }
=== ASCII SECTION 1 ===
  +-------+
  | PC 1  |
  +-------+
=== ASCII SECTION 2 ===
    ___
  /     \  
"""

text2 = """
{ "sections": [] }

=== ASCII SECTION 1 ===

   ascii here
"""

texts = [text1, text2]

for idx, text in enumerate(texts):
    print(f"Test {idx+1}")
    ascii_blocks = {}
    parts = re.split(r'===\s*ASCII SECTION\s+(\d+)\s*===', text, flags=re.IGNORECASE)
    print("Parts:", parts)
    for i in range(1, len(parts) - 1, 2):
        sec_num = int(parts[i].strip())
        ascii_blocks[sec_num - 1] = parts[i+1].strip()
    print("Blocks:", ascii_blocks)
