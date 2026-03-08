import os
import time
import requests
import subprocess
import signal
import sys
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8000"

# The specific payload that caused the reported issue
TEST_DATA = r"""
{
  "title": "Understanding Euclid’s Parallel Postulate and Its Geometric Consequences",
  "explanation": "[compass] The parallel postulate is one of the most historically significant ideas in geometry because it determines how straight lines behave in space and how geometric worlds are structured. [map] Unlike Euclid’s other axioms, which appear simple and obvious, the fifth postulate introduces a deeper rule about how lines intersect and how angles guide their eventual meeting. [bridge] Over centuries, mathematicians struggled to prove this statement from simpler axioms, eventually discovering that changing or removing it produces entirely new types of geometry. [galaxy] As a result, the parallel postulate became the gateway that separates Euclidean geometry from other geometric universes such as hyperbolic and elliptic geometry.",
  "explanation_keywords": ["compass", "map", "bridge", "galaxy"],
  "sections": [
    {
      "title": "[compass] The Original Statement of the Parallel Postulate",
      "content": "[road] The fifth postulate in Euclid’s Elements describes how two straight lines behave when a third line crosses them and forms interior angles. [triangle] If the interior angles on the same side of the crossing line add up to less than two right angles, Euclid states that the two lines must eventually meet when extended far enough. [telescope] This idea introduces the concept that geometric relationships at a local point can predict what happens infinitely far away along the lines. [anchor] The statement is distinctive because it describes a conditional relationship between angles and intersections rather than a simple construction rule.",
      "bullets": [
        "Appears as the fifth postulate in Euclid’s Elements",
        "Relates angle sums to whether two lines eventually intersect",
        "Applies to straight lines intersected by a transversal"
      ]
    },
    {
      "title": "[mirror] Equivalent Formulations and the Role of the Converse",
      "content": "[balance] Mathematicians later expressed the postulate in an equivalent form stating that two interior angles are less than two right angles if and only if the lines meet on that side. [loop] The phrase 'if and only if' adds the converse condition, meaning the logical implication works in both directions. [lens] This refinement clarifies that angle size completely determines whether the lines converge on that side. [key] The distinction between the original statement and its converse is important because Euclid originally proved only one direction while the other direction requires additional reasoning.",
      "bullets": [
        "Equivalent formulation introduces a bidirectional condition",
        "Adds logical symmetry between angles and intersection",
        "Highlights the importance of the converse statement"
      ]
    },
    {
      "title": "[bridge] How Parallel Lines Emerge from the Postulate",
      "content": "[scale] Although the original statement never explicitly mentions parallel lines, its logical consequences naturally lead to their definition. [path] If the interior angles formed by the transversal add exactly to two right angles, the lines will never meet no matter how far they extend. [frame] This behavior matches Euclid’s definition of parallel lines as lines that remain separate indefinitely. [book] Euclid placed the formal definition of parallel lines in Book I before listing the postulates, showing that the concept relies on the fifth postulate to function fully.",
      "bullets": [
        "Parallel lines are defined as lines that never intersect",
        "Angle sums equal to two right angles imply parallelism",
        "Euclid defines parallels before presenting the postulates"
      ]
    },
    {
      "title": "[galaxy] Euclidean and Non-Euclidean Geometries",
      "content": "[grid] Euclidean geometry is the geometric system that satisfies all five of Euclid’s postulates, including the rule governing parallel lines. [curve] When mathematicians modified or rejected the parallel postulate, they discovered new geometries with different properties. [wave] Hyperbolic geometry violates the original form of the postulate, allowing multiple lines through a point that never intersect a given line. [sphere] Elliptic or spherical geometry violates the converse, meaning that lines such as great circles on a sphere can intersect twice.",
      "bullets": [
        "Euclidean geometry obeys the parallel postulate",
        "Hyperbolic geometry rejects the original statement",
        "Elliptic geometry allows two intersections between lines"
      ]
    },
    {
      "title": "[torch] The Historical Search for a Proof",
      "content": "[puzzle] For centuries mathematicians believed the parallel postulate should be provable from Euclid’s other axioms because it appeared more complicated than the rest. [labyrinth] Many attempted proofs failed because they unknowingly assumed hidden forms of the same postulate they were trying to prove. [discovery] Eventually scholars realized that replacing the postulate with a different rule creates logically consistent geometries rather than contradictions. [foundation] This insight led to the idea of absolute or neutral geometry, which studies the properties of figures using only the first four postulates without committing to the fifth.",
      "bullets": [
        "Attempts to prove the postulate lasted over two thousand years",
        "Failure revealed the independence of the fifth postulate",
        "Absolute geometry studies results that do not depend on it"
      ]
    }
  ]
}

=== ASCII SECTION 1 ===
```text
        (TRANSVERSAL)
              |
              |
--------------+----------------
              |\
              | \  < interior angles
              |  \
--------------+----------------
      Line A           Line B

If the interior angles on one side
sum to LESS than two right angles,
the lines eventually meet here →  X
```
=== ASCII SECTION 2 ===
```text
      LOGIC OF THE POSTULATE
       Angles < 180°
             │
             ▼
      Lines must meet
             │
             │
             ▲
             │
  Lines meet on that side
             │
             ▼
       Angles < 180°
   (The "if and only if" loop)
```
=== ASCII SECTION 3 ===
```text
Case A: Angles < 180°         Case B: Angles = 180°

 \            /                 |            |
  \          /                  |            |
   \        /                   |            |
    \      /                    |            |
     \    /                     |            |
      \  /                      |            |
       \/                       |            |
       X  (intersect)          |            |
                           Parallel lines
                           never intersect
```
=== ASCII SECTION 4 ===
```text
            GEOMETRY WORLDS
        +-------------------+
        |  Euclidean        |
        |  One parallel     |
        +---------+---------+
                  |
     +------------+-------------+
     |                          |
+----+----+                +----+----+
| Hyperbolic|              | Elliptic|
| Many      |              | Lines   |
| parallels |              | meet    |
| possible  |              | twice   |
+-----------+              +---------+
```
=== ASCII SECTION 5 ===
```text
      HISTORY OF THE FIFTH POSTULATE
 Euclid
   |
   v
 Centuries of attempted proofs
   |
   v
 Failures reveal hidden assumptions
   |
   v
 Discovery: new geometries exist
   |
   v
 Absolute Geometry
 (first four postulates only)
```
"""

def wait_for_server(url, timeout=15):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200: return True
        except: pass
        time.sleep(1)
    return False

def check_for_gaps():
    print("🚀 Starting TextPrism server for gap analysis...")
    proc = subprocess.Popen([sys.executable, "src/app.py"], preexec_fn=os.setsid)
    
    try:
        if not wait_for_server(BASE_URL):
            raise RuntimeError("Server failed to start")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Use A4 dimensions for consistent gap detection (96 DPI)
            page.set_viewport_size({"width": 800, "height": 1123})
            
            page.goto(BASE_URL)
            page.fill("#text-input", "PDF Gap Test")
            page.click("#magic-prompt-btn")
            page.wait_for_selector("#magic-prompt-modal", state="visible")
            page.fill("#ai-response-input", TEST_DATA)
            page.click("#process-ai-btn")
            page.wait_for_selector(".explanation-box", timeout=15000)
            
            # Emulate Print Media
            page.emulate_media(media="print")
            
            # Analyze elements
            # We look for large vertical jumps between adjacent section-blocks
            blocks = page.query_selector_all(".section-block")
            page_height = 1123
            
            for i in range(len(blocks) - 1):
                box1 = blocks[i].bounding_box()
                box2 = blocks[i+1].bounding_box()
                
                if not box1 or not box2: continue
                
                bottom1 = box1['y'] + box1['height']
                top2 = box2['y']
                
                gap = top2 - bottom1
                
                # If gap is huge (e.g. > 300px) and they are on different pages
                page1 = int(bottom1 / page_height)
                page2 = int(top2 / page_height)
                
                if page2 > page1:
                    # Calculate how much space was left on the previous page
                    space_left = (page1 + 1) * page_height - bottom1
                    
                    # If space left > 400px, and the next block's header + chart 
                    # clearly fits in that space, we have a problem.
                    header = blocks[i+1].query_selector(".section-header")
                    chart = blocks[i+1].query_selector(".ascii-box")
                    
                    if header and chart:
                        # Get height in current layout (might be zero if on next page, 
                        # so we check their potential height)
                        # Actually bounding_box should work even if moved
                        h_box = header.bounding_box()
                        c_box = chart.bounding_box()
                        combined_h = (h_box['height'] if h_box else 0) + (c_box['height'] if c_box else 0)
                        
                        if combined_h < space_left - 100: # 100px buffer
                            print(f"❌ UNNECESSARY GAP DETECTED between section {i+1} and {i+2}")
                            print(f"   Space left on page {page1+1}: {space_left:.1f}px")
                            print(f"   Block height: {combined_h:.1f}px")
                            print(f"   Gap is approximately {gap:.1f}px")
                            assert False, f"Gap detected on page {page1+1}"

            print("✅ No significant unnecessary gaps detected.")
            browser.close()

    finally:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

if __name__ == "__main__":
    try:
        check_for_gaps()
    except Exception as e:
        print(f"FAILED: {e}")
        exit(1)
