import requests
import re
from fastapi.testclient import TestClient
from src.app import app
import os
import io

client = TestClient(app)

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

response = client.post("/render-magic", data={"data": raw_text})
if response.status_code == 200:
    with open("user_payload_output.html", "w", encoding='utf-8') as f:
        f.write(response.text)
    print("✅ Rendered to user_payload_output.html")
else:
    print(f"Error: {response.text}")

