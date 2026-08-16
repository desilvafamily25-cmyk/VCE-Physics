"""Section B interaction geometry for the 2020 VCE Physics exam.

Same method as build_2023_section_b.py / build_2021_section_b.py /
build_2022_section_b.py (see those docstrings). This year's gaps skew
towards small bare-word answer boxes ("clockwise or anticlockwise?",
"increase, decrease or stay the same?") that are far narrower than the
ruled-line detector's half-page-width threshold, and towards direct-read-
off-a-figure tasks with genuinely no ruled line to detect at all.

  1. Two false-positive ruled-line detections excluded: a spring-launch
     figure's own ground line (Question 9, picked up as a bogus bare "B9"
     before any letter was seen) and a helium emission-spectrum figure's
     bar chart (Question 17, similarly landing as a bogus bare "B17").
  2. Eleven subparts have no ruled answer line at all: three small bare-
     word answer boxes, four "draw/sketch/label directly on the provided
     figure" tasks, a table cell fill-in that's positioned above the
     question text asking for it (Question 18d), and two more of the same
     drawing pattern.

Output: data/2020-interactions.json / public/interactions/2020.json.
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
EXAM_PATH = ROOT / "previous-design-2017-2023" / "2020-physics-exam.pdf"
RAW_REPORT = ROOT / "data" / "raw" / "2020-report-extract.json"
EXISTING_INTERACTIONS = ROOT / "public" / "interactions" / "2020.json"
OUT_PATH = ROOT / "data" / "2020-interactions.json"
PUBLIC_OUT = ROOT / "public" / "interactions" / "2020.json"

EXCLUDE_GROUPS = {
    (25, "B9"),
    (34, "B17"),
}

MANUAL_ENTRIES = [
    {
        "id": "B1", "page": 12, "type": "drawing",
        "rect": {"x": 0.358, "y": 0.350, "width": 0.260, "height": 0.175},
        "note": "Manually placed: 'sketch field lines within the dashed border' has no ruled answer lines to detect.",
    },
    {
        "id": "B3ci", "page": 15, "type": "text",
        "rect": {"x": 0.162, "y": 0.085, "width": 0.182, "height": 0.039},
        "note": "Manually placed: 'at which point X, Y or Z' answered in a small bordered box, narrower than "
                "the ruled-line detector's half-page-width threshold.",
    },
    {
        "id": "B5a", "page": 18, "type": "text",
        "rect": {"x": 0.115, "y": 0.432, "width": 0.182, "height": 0.043},
        "note": "Manually placed: 'clockwise or anticlockwise' answered in a small bordered box.",
    },
    {
        "id": "B5c", "page": 19, "type": "drawing",
        "rect": {"x": 0.242, "y": 0.107, "width": 0.519, "height": 0.141},
        "note": "Manually placed: 'sketch the output EMF on the axes' -- blank axes, no ruled answer lines to detect.",
    },
    {
        "id": "B6a", "page": 20, "type": "text",
        "rect": {"x": 0.115, "y": 0.466, "width": 0.182, "height": 0.041},
        "note": "Manually placed: 'increase, decrease or stay the same' answered in a small bordered box.",
    },
    {
        "id": "B8a", "page": 24, "type": "drawing",
        "rect": {"x": 0.208, "y": 0.120, "width": 0.438, "height": 0.231},
        "note": "Manually placed: 'use labelled arrows to indicate the forces on Figure 8' has no ruled answer lines to detect.",
    },
    {
        "id": "B13b", "page": 30, "type": "drawing",
        "rect": {"x": 0.115, "y": 0.598, "width": 0.738, "height": 0.214},
        "note": "Manually placed: 'draw the new standing wave envelope' -- only a short reference line "
                "(narrower than the ruled-line detector's half-page-width threshold), not a ruled box.",
    },
    {
        "id": "B14", "page": 31, "type": "drawing",
        "rect": {"x": 0.231, "y": 0.175, "width": 0.381, "height": 0.115},
        "note": "Manually placed: 'correctly label Figure 13' has no ruled answer lines to detect.",
    },
    {
        "id": "B15a", "page": 32, "type": "drawing",
        "rect": {"x": 0.231, "y": 0.444, "width": 0.461, "height": 0.145},
        "note": "Manually placed: 'draw the trace on Figure 15' has no ruled answer lines to detect.",
    },
    {
        "id": "B17a", "page": 34, "type": "text",
        "rect": {"x": 0.115, "y": 0.380, "width": 0.182, "height": 0.043},
        "note": "Manually placed: 'which spectral line' is a bare unit box (nm) with no ruled working lines above it.",
    },
    {
        "id": "B18d", "page": 37, "type": "text",
        "rect": {"x": 0.542, "y": 0.120, "width": 0.228, "height": 0.188},
        "note": "Manually placed: 'write the values in the last column of Table 1' -- the table is above the "
                "question text asking for it on this page, and is a bordered table column, not ruled lines.",
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
