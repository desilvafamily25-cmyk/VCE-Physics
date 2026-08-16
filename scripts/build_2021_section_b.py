"""Section B interaction geometry for the 2021 VCE Physics exam.

Same method as build_2023_section_b.py / build_2022_section_b.py (see those
docstrings). This year's false positives are dense-grid graphs specifically:
2021 prints major gridlines heavy/dark enough (unlike 2022's own blank
grids, which the detector correctly found nothing in) that several of them
individually match the ruled-line pattern, producing multiple bogus
detections under one subpart instead of zero.

  1. Four false-positive ruled-line detections excluded: a bar-magnet-and-
     compass diagram's own box borders (Question 1's Figure 1, picked up
     before any letter was seen), a Doppler-effect sketch axis's dashed
     reference line and solid baseline counted as two separate groups
     (Question 14a), a physical-apparatus figure's ground line (Question
     8b's Figure 7, picked up as a false "part b." continuation), and all
     five gridlines the centripetal-force investigation's blank plotting
     grid produced (Question 20e).
  2. Five subparts have no ruled answer line at all (or none usable): two
     "draw directly on the provided figure" tasks, a "circle the correct
     multiple-choice-style answer" sub-question inside Section B whose
     answer is a small bordered box (not a full-width ruled line), a
     sketch-a-graph task on essentially blank axes, and the same dense
     plotting grid mentioned above once its five false positives are
     excluded.

Output: data/2021-interactions.json / public/interactions/2021.json.
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
EXAM_PATH = ROOT / "previous-design-2017-2023" / "2021-physics-exam.pdf"
RAW_REPORT = ROOT / "data" / "raw" / "2021-report-extract.json"
EXISTING_INTERACTIONS = ROOT / "public" / "interactions" / "2021.json"
OUT_PATH = ROOT / "data" / "2021-interactions.json"
PUBLIC_OUT = ROOT / "public" / "interactions" / "2021.json"

EXCLUDE_GROUPS = {
    (24, "B8b-2"),
    (32, "B14"),
    (32, "B14a"),
    (32, "B14a-2"),
    (41, "B20e"),
    (41, "B20e-2"),
    (41, "B20e-3"),
    (41, "B20e-4"),
    (41, "B20e-5"),
}

MANUAL_ENTRIES = [
    {
        "id": "B1a", "page": 13, "type": "drawing",
        "rect": {"x": 0.438, "y": 0.329, "width": 0.127, "height": 0.051},
        "note": "Manually placed: 'draw an arrow at point P' has no ruled answer lines to detect.",
    },
    {
        "id": "B2a", "page": 14, "type": "drawing",
        "rect": {"x": 0.260, "y": 0.496, "width": 0.490, "height": 0.252},
        "note": "Manually placed: 'draw four magnetic field lines on Figure 3' has no ruled answer lines to detect.",
    },
    {
        "id": "B2b", "page": 15, "type": "text",
        "rect": {"x": 0.125, "y": 0.167, "width": 0.074, "height": 0.038},
        "note": "Manually placed: multiple-choice-style sub-question answered in a small bordered box, "
                "narrower than the ruled-line detector's half-page-width threshold.",
    },
    {
        "id": "B14a", "page": 32, "type": "drawing",
        "rect": {"x": 0.196, "y": 0.410, "width": 0.565, "height": 0.205},
        "note": "Manually placed: 'sketch the frequency Chris hears' on a near-blank reference graph -- the only "
                "lines present are the dashed 500 Hz reference and the axis baseline, both excluded as false positives.",
    },
    {
        "id": "B20e", "page": 41, "type": "drawing",
        "rect": {"x": 0.162, "y": 0.205, "width": 0.646, "height": 0.500},
        "note": "Manually placed: 'plot Mg vs 1/T^2 with uncertainty bars and a line of best fit' -- a dense grid "
                "whose own gridlines produced five false-positive detections (excluded) rather than one usable box.",
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
