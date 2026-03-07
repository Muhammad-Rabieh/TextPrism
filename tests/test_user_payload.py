import re
import json

raw_text = """
{
  "title": "C++ Templates: Build Once, Use Everywhere",
  "explanation": "[doodle_blueprint] C++ templates enable generic programming, [doodle_rocket] eliminate duplication, and power the STL ecosystem.",
  "explanation_keywords": ["doodle_blueprint", "doodle_rocket"],
  "sections": [
    {
      "title": "Generic Code Engine",
      "content": "[doodle_blueprint] A C++ template lets you create generic functions or classes. [doodle_factory] You write the logic once, and it works with any data type.",
      "bullets": [
        "Supports int, float, double, string, custom types",
        "No rewriting for every data type",
        "Compiler generates type-specific versions automatically"
      ]
    },
    {
      "title": "No More Duplication",
      "content": "[doodle_stack] Templates eliminate repeated code by allowing a single reusable definition. [doodle_broom] This keeps programs cleaner and easier to manage.",
      "bullets": [
        "One implementation instead of many",
        "Reduces copy-paste functions",
        "Easier updates and maintenance"
      ]
    },
    {
      "title": "Safety + Specialization",
      "content": "[doodle_shield] Templates are type-safe and checked at compile time. [doodle_wrench] They can also be specialized for specific data types.",
      "bullets": [
        "Compile-time type checking",
        "Safer than void* and macros",
        "Supports template specialization"
      ]
    },
    {
      "title": "Foundation of the STL",
      "content": "[colorful_building] Templates form the backbone of the Standard Template Library (STL). [doodle_engine] They power flexible containers and reusable algorithms.",
      "bullets": [
        "Containers: vector, map",
        "Algorithms: sort, find",
        "High-performance reusable components"
      ]
    }
  ]
}

=== ASCII SECTION 1 ===
┌────────────────────┐
│ Template<T> │
│ (One Blueprint) │
└─────────┬──────────┘
│
┌───────────┼───────────┐
▼ ▼ ▼
[int] [double] [string]

=== ASCII SECTION 2 ===
Without Templates: With Templates:

addInt() add<T>()
addDouble() ───▶ (one definition)
addFloat()

=== ASCII SECTION 3 ===
┌──────────────────┐
│ Template<T> │
└─────────┬────────┘
│
┌─────────▼─────────┐
│ Specialized<T> │
│ (Custom Behavior) │
└───────────────────┘

=== ASCII SECTION 4 ===
┌───────────────────────────┐
│ STL CORE │
├────────────┬──────────────┤
│ Containers │ Algorithms │
├────────────┼──────────────┤
│ vector │ sort │
│ map │ find │
└────────────┴──────────────┘
"""

# Extract JSON block
json_match = re.search(r'```json\s*(.*?)\s*```', raw_text, re.DOTALL | re.IGNORECASE)
if json_match:
    json_str = json_match.group(1)
    print("Found JSON using ```json")
else:
    start = raw_text.find('{')
    end = raw_text.rfind('}')
    if start != -1 and end != -1:
        json_str = raw_text[start:end+1]
        print("Found JSON using brackets fallback")
    else:
        print("Could not find JSON block in output.")
        json_str = "{}"

try:
    ai_data = json.loads(json_str)
    print("Parsed JSON successfully.")
except Exception as e:
    print(f"JSON Decode Error: {e}")
    ai_data = {"sections": [{}, {}, {}, {}]} # Mock 4 sections

ascii_blocks = {}
pattern = re.compile(r'(?:=+|-+|#+|\*\*)\s*ASCII SECTION\s+(\d+)\s*(?:=+|-+|#+|\*\*)', flags=re.IGNORECASE)
parts = pattern.split(raw_text)

print(f"Total parts from split: {len(parts)}")

for i in range(1, len(parts) - 1, 2):
    try:
        sec_num = int(parts[i].strip())
        block = parts[i+1].strip('\r\n')
        block = re.sub(r'^```[\w]*\s*\n', '', block)
        block = re.sub(r'\n```\s*$', '', block)
        ascii_blocks[sec_num - 1] = block
    except ValueError:
        pass

print("Extracted ASCII blocks:")
for i, block in ascii_blocks.items():
    print(f"--- Block {i} (Length {len(block)}) ---")
    print(block)

if not ascii_blocks:
    print("ERROR: No ASCII blocks extracted!")

# Simulate render_magic logic
fallback_count = 0
for idx, section in enumerate(ai_data.get('sections', [])):
    raw_ai_ascii = ascii_blocks.get(idx, section.get('raw_ascii', ''))
    
    if not raw_ai_ascii:
        fallback_count += 1

print(f"Fallbacks triggered: {fallback_count} / {len(ai_data.get('sections', []))}")

