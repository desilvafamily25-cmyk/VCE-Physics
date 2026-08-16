"""Section B interaction geometry for the 2022 VCE Physics exam.

Same method as build_2023_section_b.py (see its docstring): 2022 has a real
text layer, so generate_paper_assets.py's make_written_fields_labelled
recovers most subparts automatically with correct VCAA-matching ids. This
script layers two corrections on top, both confirmed by rendering the
relevant page:

  1. One detected group is a false positive -- Figure 9's own ground-line
     drawing (a projectile-motion diagram) picked up before any subpart
     letter had been seen on that page, landing as a bare "B10".
  2. Eight subparts have no ruled answer line at all: two are "draw
     directly on the provided figure" tasks (a force-direction arrow, an
     energy-level transition arrow), two more are sketch-a-graph tasks on a
     blank set of axes (no ruled lines, just axes), a fill-in-the-table
     classification question, a large blank grid for plotting data with
     uncertainty bars (dense grid lines don't match the ruled-line
     detector's few-evenly-spaced-lines pattern), and two bare read-off-the-
     graph unit boxes with no ruled working lines above them.

Fixing this year also fixed two bugs shared with every other text-layer
paper (see generate_paper_assets.py's make_written_fields_labelled and
first_question_heading_y_fraction): 2022's Section B opening page prints a
"SECTION B – Question 1 – continued" running footer, which the unfiltered
heading search matched instead of the true top-of-page heading, silently
discarding Question 1a's real answer box.

Output: data/2022-interactions.json (Section A preserved from the existing
audited auto-generated file, Section B replaced by this script's output),
copied straight into public/interactions/2022.json.
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
EXAM_PATH = ROOT / "previous-design-2017-2023" / "2022-physics-exam.pdf"
RAW_REPORT = ROOT / "data" / "raw" / "2022-report-extract.json"
EXISTING_INTERACTIONS = ROOT / "public" / "interactions" / "2022.json"
OUT_PATH = ROOT / "data" / "2022-interactions.json"
PUBLIC_OUT = ROOT / "public" / "interactions" / "2022.json"

EXCLUDE_GROUPS = {
    (28, "B10"),
}

MANUAL_ENTRIES = [
    {
        "id": "B8b", "page": 26, "type": "drawing",
        "rect": {"x": 0.542, "y": 0.154, "width": 0.288, "height": 0.150},
        "note": "Manually placed: 'draw the net force direction on Figure 8b' has no ruled answer lines to detect.",
    },
    {
        "id": "B10a", "page": 28, "type": "text",
        "rect": {"x": 0.381, "y": 0.368, "width": 0.283, "height": 0.137},
        "note": "Manually placed: classification/variable fill-in-the-table question; box spans the Variable column.",
    },
    {
        "id": "B10b", "page": 29, "type": "drawing",
        "rect": {"x": 0.185, "y": 0.209, "width": 0.485, "height": 0.393},
        "note": "Manually placed: 'plot the data with uncertainty bars and a curve of best fit' -- a dense grid, "
                "not the ruled-line detector's few-evenly-spaced-lines pattern.",
    },
    {
        "id": "B10c", "page": 29, "type": "text",
        "rect": {"x": 0.127, "y": 0.701, "width": 0.392, "height": 0.090},
        "note": "Manually placed: spans the two bare unit boxes (maximum range, angle) with no ruled working lines above them.",
    },
    {
        "id": "B14b", "page": 37, "type": "drawing",
        "rect": {"x": 0.30, "y": 0.145, "width": 0.35, "height": 0.16},
        "note": "Manually placed: 'sketch the resulting graph on Figure 14' -- blank axes, no ruled answer lines to detect.",
    },
    {
        "id": "B14c", "page": 37, "type": "drawing",
        "rect": {"x": 0.30, "y": 0.419, "width": 0.35, "height": 0.14},
        "note": "Manually placed: 'sketch the resulting graph on Figure 15' -- blank axes, no ruled answer lines to detect.",
    },
    {
        "id": "B15b", "page": 40, "type": "drawing",
        "rect": {"x": 0.225, "y": 0.128, "width": 0.306, "height": 0.21},
        "note": "Manually placed: 'draw an arrow on Figure 17' has no ruled answer lines to detect.",
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
