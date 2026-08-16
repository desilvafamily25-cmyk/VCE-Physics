"""Section B interaction geometry for the 2018 VCE Physics exam.

Same method as the other text-layer years' own build_<year>_section_b.py
scripts (see e.g. build_2019_section_b.py's docstring) -- 2018's exam PDF
has a real text layer, so make_written_fields_labelled recovers most
subparts automatically. This year's false positives are all "a context
figure's own outline/axis/gridlines mistaken for a ruled answer line,
before any lettered subpart has been seen" cases, the same pattern already
seen in prior years:

  1. Four false-positive detections excluded outright: Figure 5's y-axis
     tick row (Question 4, before "a."), Figure 8's dashed dimension line
     (Question 6, before "a."), Figure 9's table-leg lines (Question 7,
     before "a."), and Figure 19's spectrum tick-mark row (Question 19,
     before "a.").
  2. One of those false positives sits right next to a real, but
     too-narrow, detection: Question 4b's actual task is "sketch on
     Figure 6" (the whole graph grid), but the auto-detector only grabbed
     a ~5%-tall sliver of it (matching the same sliver height as the
     Figure 5 false positive above -- both are catching one grid row, not
     the full sketch area). Replaced with Figure 6's own full grid bounds
     (found via its vector-drawing bbox).
  3. Two subparts have no ruled answer line at all and were never
     detected: Question 17a(i) ("write the name in the box provided" --
     a small bordered box) and Question 19a ("circle the colour" -- a
     line of four words to circle, not a ruled line).
  4. Question 8b's answer is two short side-by-side bordered boxes ("N"
     value + a direction box), individually narrower than the ruled-line
     detector's half-page-width threshold and with no ruled lines above
     them -- never detected, added as one manual entry spanning both.

Output: data/2018-interactions.json / public/interactions/2018.json.
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
EXAM_PATH = ROOT / "previous-design-2017-2023" / "2018-physics-exam.pdf"
RAW_REPORT = ROOT / "data" / "raw" / "2018-report-extract.json"
EXISTING_INTERACTIONS = ROOT / "public" / "interactions" / "2018.json"
OUT_PATH = ROOT / "data" / "2018-interactions.json"
PUBLIC_OUT = ROOT / "public" / "interactions" / "2018.json"

EXCLUDE_GROUPS = {
    (18, "B4"),
    (19, "B4b"),
    (22, "B6"),
    (23, "B7"),
    (36, "B17"),
    (39, "B19"),
}

MANUAL_ENTRIES = [
    {
        "id": "B4b", "page": 19, "type": "drawing",
        "rect": {"x": 0.225, "y": 0.366, "width": 0.531, "height": 0.179},
        "note": "Manually placed using Figure 6's own vector-drawing bounds: 'sketch the output on Figure 6' -- "
                "the auto-detector only matched a ~5%-tall sliver of the grid (one row), not the full sketch area.",
    },
    {
        "id": "B8b", "page": 24, "type": "text",
        "rect": {"x": 0.097, "y": 0.526, "width": 0.430, "height": 0.040},
        "note": "Manually placed: two short side-by-side bordered boxes ('N' value + direction), each "
                "individually narrower than the ruled-line detector's half-page-width threshold and with no "
                "ruled lines above them.",
    },
    {
        "id": "B17ai", "page": 37, "type": "text",
        "rect": {"x": 0.146, "y": 0.141, "width": 0.191, "height": 0.040},
        "note": "Manually placed: 'write the name in the box provided' -- a small bordered box, not a ruled "
                "answer line.",
    },
    {
        "id": "B19a", "page": 39, "type": "text",
        "rect": {"x": 0.193, "y": 0.363, "width": 0.436, "height": 0.031},
        "note": "Manually placed: 'circle the colour...' -- a line of four words to circle, not a ruled "
                "answer line.",
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
