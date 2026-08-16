"""Section B interaction geometry for the 2017 VCE Physics exam.

Same method as the other text-layer years' own build_<year>_section_b.py
scripts (see e.g. build_2019_section_b.py's docstring) -- 2017's exam PDF
has a real text layer, so make_written_fields_labelled recovers most
subparts automatically. This year's gaps are the same two recurring
patterns seen in every prior year:

  1. Three false-positive detections excluded outright (a context
     figure's own trajectory/dimension line mistaken for a ruled answer
     line, before its subpart's own lettered box was reached, or -- for
     Figure 14 on page 32 -- appearing *after* "a." had already been used
     for the real Q15a box, producing a harmless "a-2" duplicate).
  2. Six subparts have no ruled answer line at all -- each is a "draw/
     sketch on this figure" task reusing a diagram already shown earlier
     in the question, so there was never a ruled-line box to detect:
     Question 1 (draw an arrow at point X on Figure 1), Question 5c
     (sketch a waveform on blank axes), Question 7a (draw force arrows
     on a small diagram), Question 14b (sketch a ray on Figure 12),
     Question 17b (sketch a curve on Figure 16, shown on the *previous*
     page from where the task itself is set), and Question 18a (draw an
     arrow on Figure 17's energy-level diagram).

Also fixed two real bugs in pdf_report_extraction_lib.py's Section A
comment extraction while building this year (2017's report is the only
one of the three PDF-report years with an extra "% No Answer" column
between %D and Comments): see that module's _extra_column_exclusion_band
and _answer_label_y docstrings.

Output: data/2017-interactions.json / public/interactions/2017.json.
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
EXAM_PATH = ROOT / "previous-design-2017-2023" / "2017-physics-exam.pdf"
RAW_REPORT = ROOT / "data" / "raw" / "2017-report-extract.json"
EXISTING_INTERACTIONS = ROOT / "public" / "interactions" / "2017.json"
OUT_PATH = ROOT / "data" / "2017-interactions.json"
PUBLIC_OUT = ROOT / "public" / "interactions" / "2017.json"

EXCLUDE_GROUPS = {
    (23, "B9"),
    (32, "B15a-2"),
    (36, "B17"),
}

MANUAL_ENTRIES = [
    {
        "id": "B1", "page": 12, "type": "drawing",
        "rect": {"x": 0.20, "y": 0.295, "width": 0.50, "height": 0.10},
        "note": "Manually placed: 'draw an arrow at point X on Figure 1' has no ruled answer lines to detect.",
    },
    {
        "id": "B5c", "page": 19, "type": "drawing",
        "rect": {"x": 0.28, "y": 0.645, "width": 0.46, "height": 0.09},
        "note": "Manually placed using the blank EMF-vs-time axes' own vector-drawing bounds: 'sketch the EMF "
                "graph' has no ruled answer lines (it's a blank set of axes, not a grid, so the ruled-line "
                "detector never matched it).",
    },
    {
        "id": "B7a", "page": 21, "type": "drawing",
        "rect": {"x": 0.13, "y": 0.33, "width": 0.32, "height": 0.16},
        "note": "Manually placed: 'draw all of the forces...as arrows' on a small triangle diagram has no "
                "ruled answer lines to detect.",
    },
    {
        "id": "B14b", "page": 30, "type": "drawing",
        "rect": {"x": 0.20, "y": 0.14, "width": 0.42, "height": 0.16},
        "note": "Manually placed using Figure 12's own vector-drawing bounds: 'sketch the ray or rays...on "
                "Figure 12' reuses the diagram already shown for part a., with no ruled answer lines of its own.",
    },
    {
        "id": "B17b", "page": 36, "type": "drawing",
        "rect": {"x": 0.13, "y": 0.39, "width": 0.62, "height": 0.18},
        "note": "Manually placed using Figure 16's own vector-drawing bounds: 'sketch the curve...on Figure 16' "
                "reuses the graph shown earlier on the same page (under part a.'s context), with no ruled "
                "answer lines of its own.",
    },
    {
        "id": "B18a", "page": 38, "type": "drawing",
        "rect": {"x": 0.20, "y": 0.12, "width": 0.52, "height": 0.30},
        "note": "Manually placed using Figure 17's own vector-drawing bounds: 'draw an arrow on the "
                "energy-level diagram in Figure 17' has no ruled answer lines to detect.",
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
