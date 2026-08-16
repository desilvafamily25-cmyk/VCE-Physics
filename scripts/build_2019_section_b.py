"""Section B interaction geometry for the 2019 VCE Physics exam.

Same method as the docx-report years' own build_<year>_section_b.py
scripts (see e.g. build_2023_section_b.py's docstring) -- 2019's exam PDF
has a real text layer, so make_written_fields_labelled recovers most
subparts automatically. This year's false positives are all "decorative
preview figure shown before the actual task" cases: a diagram is shown for
context immediately under a "Question N (...)" heading, before any subpart
letter has been seen, and its own outline/axis is mistaken for a ruled
answer line.

  1. Two false-positive detections excluded outright (a projectile-path
     figure's trajectory arc, a photoelectric-effect results grid shown
     before its own lettered part).
  2. One false positive is a special case: Question 7g's task is itself
     "sketch on Figure 7", but Figure 6 (an unlabelled preview graph shown
     just above it, for reference) also produced a detection and happened
     to consume the "g" label first, leaving the real Figure 7 target as an
     orphaned "B7g-2" duplicate. Both auto-detections are dropped and
     replaced with one manual entry using Figure 7's own bounds.
  3. Seven subparts have no ruled answer line at all: a blank sketch-a-
     field-lines area, a small terminal-choice box, a draw-an-arrow-on-the-
     figure task, two bare unit boxes, a circle-the-correct-word task, and
     a pair of short side-by-side answer lines ("Point X ___ Point Y ___",
     each individually narrower than the ruled-line detector's half-page-
     width threshold).

Fixing this year also surfaced a bug shared by every text-layer paper:
make_written_fields_labelled's "exclude a single ruled line very near the
top of the page" heuristic (meant only to catch Section B's own
Instructions-block divider on its first page) was applying on every page,
silently discarding a genuine short single-line answer box that happened
to sit near the top of an unrelated continuation page (2019's own
Question 7c). Now gated to the Section B's first page only, matching how
the Instructions-block exclusion itself is already gated.

Output: data/2019-interactions.json / public/interactions/2019.json.
"""
import json
import sys
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_paper_assets import (  # noqa: E402
    detect_section_b_start,
    find_formula_sheet_range,
    make_written_fields_labelled,
)

ROOT = Path(__file__).resolve().parents[1]
EXAM_PATH = ROOT / "previous-design-2017-2023" / "2019-physics-exam.pdf"
RAW_REPORT = ROOT / "data" / "raw" / "2019-report-extract.json"
EXISTING_INTERACTIONS = ROOT / "public" / "interactions" / "2019.json"
OUT_PATH = ROOT / "data" / "2019-interactions.json"
PUBLIC_OUT = ROOT / "public" / "interactions" / "2019.json"

EXCLUDE_GROUPS = {
    (27, "B10"),
    (34, "B16"),
    (22, "B7g"),
    (22, "B7g-2"),
}

MANUAL_ENTRIES = [
    {
        "id": "B2", "page": 13, "type": "drawing",
        "rect": {"x": 0.121, "y": 0.145, "width": 0.750, "height": 0.214},
        "note": "Manually placed: 'sketch the electric field lines on Figure 2' has no ruled answer lines to detect.",
    },
    {
        "id": "B3a", "page": 14, "type": "text",
        "rect": {"x": 0.097, "y": 0.449, "width": 0.193, "height": 0.043},
        "note": "Manually placed: 'which terminal (X or Y)' answered in a small bordered box, narrower than "
                "the ruled-line detector's half-page-width threshold.",
    },
    {
        "id": "B3b", "page": 14, "type": "drawing",
        "rect": {"x": 0.218, "y": 0.167, "width": 0.532, "height": 0.192},
        "note": "Manually placed: 'draw an arrow on Figure 3' has no ruled answer lines to detect.",
    },
    {
        "id": "B4a", "page": 16, "type": "text",
        "rect": {"x": 0.097, "y": 0.491, "width": 0.218, "height": 0.043},
        "note": "Manually placed: bare unit box (N kg^-1) with no ruled working lines above it.",
    },
    {
        "id": "B7a", "page": 20, "type": "text",
        "rect": {"x": 0.169, "y": 0.465, "width": 0.580, "height": 0.035},
        "note": "Manually placed: 'circle the name that best describes...' -- a line of four words to circle, "
                "not a ruled answer line.",
    },
    {
        "id": "B7bi", "page": 20, "type": "text",
        "rect": {"x": 0.133, "y": 0.538, "width": 0.193, "height": 0.038},
        "note": "Manually placed: bare unit box (Wb) with no ruled working lines above it.",
    },
    {
        "id": "B7g", "page": 22, "type": "drawing",
        "rect": {"x": 0.188, "y": 0.475, "width": 0.544, "height": 0.228},
        "note": "Manually placed using Figure 7's own bounds (the actual sketch target): the auto-detector "
                "matched Figure 6 (an unlabelled preview graph shown just above it) to the 'g' label first, "
                "leaving Figure 7 an orphaned duplicate -- both auto detections excluded, this replaces them.",
    },
    {
        "id": "B15b", "page": 32, "type": "text",
        "rect": {"x": 0.097, "y": 0.638, "width": 0.762, "height": 0.030},
        "note": "Manually placed: 'Point X ___ Point Y ___' -- two short side-by-side answer lines, each "
                "individually narrower than the ruled-line detector's half-page-width threshold.",
    },
]


def main():
    doc = fitz.open(EXAM_PATH)
    section_b_first = detect_section_b_start(doc, True, 20)
    formula_range = find_formula_sheet_range(doc)
    section_b_last = (formula_range[0] - 1) if formula_range else doc.page_count

    items = make_written_fields_labelled(doc, section_b_first, section_b_last)
    items = [item for item in items if (item["page"], item["id"]) not in EXCLUDE_GROUPS]

    detected_ids = {item["id"] for item in items}
    for entry in MANUAL_ENTRIES:
        if entry["id"] in detected_ids:
            continue
        items.append({
            "id": entry["id"],
            "section": "B",
            "question": entry["id"][1:],
            "page": entry["page"],
            "type": entry["type"],
            "rect": entry["rect"],
            "note": entry["note"],
        })

    existing = json.loads(EXISTING_INTERACTIONS.read_text(encoding="utf-8-sig"))
    section_a = [item for item in existing if item.get("section") == "A"]
    combined = section_a + items

    OUT_PATH.write_text(json.dumps(combined, indent=2), encoding="utf-8")
    PUBLIC_OUT.write_text(json.dumps(combined, indent=2), encoding="utf-8")

    expected_ids = [q["interactionId"] for q in json.loads(RAW_REPORT.read_text(encoding="utf-8"))["sectionB"]]
    got_ids = [item["id"] for item in items]
    got_set = set(got_ids)
    missing = [i for i in expected_ids if i not in got_set]
    extra = [i for i in got_set if i not in set(expected_ids)]
    dupes = sorted({i for i in got_ids if got_ids.count(i) > 1})
    print(f"Section A preserved: {len(section_a)}")
    print(f"Section B placed: {len(items)} / {len(expected_ids)} expected")
    if missing:
        print(f"Missing: {missing}")
    if extra:
        print(f"Extra/unexpected: {extra}")
    if dupes:
        print(f"DUPLICATES: {dupes}")
    if not missing and not extra and not dupes:
        print("All Section B subparts matched exactly.")


if __name__ == "__main__":
    main()
