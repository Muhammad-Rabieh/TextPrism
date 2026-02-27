import requests
import re
from fastapi.testclient import TestClient
from app import app
import os
import io

client = TestClient(app)

raw_text = """
{
  "title": "C++ Templates: Build Once, Use Everywhere",
  "summary": "C++ templates enable generic programming, eliminate duplication, enforce compile-time safety, and power the STL ecosystem.",
  "summary_keywords": ["doodle blueprint", "doodle rocket"],
  "sections": [
    {
      "title": "Generic Code Engine",
      "sentences": [
        {
          "text": "A C++ template lets you create generic functions or classes.",
          "keyword": "doodle blueprint"
        },
        {
          "text": "You write the logic once, and it works with any data type.",
          "keyword": "doodle factory"
        }
      ],
      "bullets": [
        "Supports int, float, double, string, custom types",
        "No rewriting for every data type",
        "Compiler generates type-specific versions automatically"
      ]
    },
    {
      "title": "No More Duplication",
      "sentences": [
        {
          "text": "Templates eliminate repeated code by allowing a single reusable definition.",
          "keyword": "doodle stack"
        },
        {
          "text": "This keeps programs cleaner and easier to manage.",
          "keyword": "doodle broom"
        }
      ],
      "bullets": [
        "One implementation instead of many",
        "Reduces copy-paste functions",
        "Easier updates and maintenance"
      ]
    },
    {
      "title": "Safety + Specialization",
      "sentences": [
        {
          "text": "Templates are type-safe and checked at compile time.",
          "keyword": "doodle shield"
        },
        {
          "text": "They can also be specialized for specific data types when custom behavior is required.",
          "keyword": "doodle wrench"
        }
      ],
      "bullets": [
        "Compile-time type checking",
        "Safer than void* and macros",
        "Supports template specialization"
      ]
    },
    {
      "title": "Foundation of the STL",
      "sentences": [
        {
          "text": "Templates form the backbone of the Standard Template Library (STL).",
          "keyword": "colorful building"
        },
        {
          "text": "They power flexible containers and reusable algorithms.",
          "keyword": "doodle engine"
        }
      ],
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

