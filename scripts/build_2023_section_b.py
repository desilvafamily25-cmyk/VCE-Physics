"""Section B interaction geometry for the 2023 VCE Physics exam.

2023 has a real text layer (unlike 2024), so generate_paper_assets.py's
make_written_fields_labelled already recovers 45 of the 52 subparts with
correct VCAA-matching ids (B1a, B1b, ...) automatically. This script layers
two corrections on top of that generic pass, both individually confirmed by
rendering the relevant page:

  1. Four detected groups are false positives -- ruled-line-shaped elements
     inside a figure (a circuit diagram's wire, a photoelectric-effect
     graph's own axis/gridlines) picked up before any subpart letter had
     been seen on that page, landing as a bare "B4"/"B15"/"B17"/"B17-2".
     EXCLUDE_GROUPS removes them by their exact (page, id) pair.
  2. Seven subparts have no ruled answer line at all: five are "draw
     directly on the provided figure" tasks (arrows on a force diagram,
     field lines around a wire, a current direction on a loop, a line of
     best fit on a graph, a transition arrow on an energy-level diagram)
     and two are a set of narrow bordered boxes / a table column (neither
     wide enough to trigger the ruled-line detector's half-page-width
     threshold). MANUAL_ENTRIES places all seven, each rect read directly
     off a clean 110dpi render of that exact page.

Output: data/2023-interactions.json (Section A preserved from the existing
audited auto-generated file, Section B replaced by this script's output),
copied straight into public/interactions/2023.json. generate_paper_assets.py
reloads this same file verbatim on every run once "2023" is added to its
TUNED_INTERACTIONS set, so this is the single source of truth going forward
-- not a one-off patch that a later regeneration would silently undo.
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
EXAM_PATH = ROOT / "previous-design-2017-2023" / "2023-physics-exam.pdf"
RAW_REPORT = ROOT / "data" / "raw" / "2023-report-extract.json"
EXISTING_INTERACTIONS = ROOT / "public" / "interactions" / "2023.json"
OUT_PATH = ROOT / "data" / "2023-interactions.json"
PUBLIC_OUT = ROOT / "public" / "interactions" / "2023.json"

# (page, id) pairs to drop -- confirmed spurious by rendering each page and
# finding no genuine ruled answer line at that position (see module
# docstring point 1).
EXCLUDE_GROUPS = {
    (16, "B4"),
    (36, "B15"),
    (40, "B17"),
    (40, "B17-2"),
}

MANUAL_ENTRIES = [
    {
        "id": "B1a", "page": 12, "type": "drawing",
        "rect": {"x": 0.367, "y": 0.342, "width": 0.262, "height": 0.187},
        "note": "Manually placed: 'draw the three forces on Figure 1' has no ruled answer lines to detect.",
    },
    {
        "id": "B3a", "page": 15, "type": "drawing",
        "rect": {"x": 0.525, "y": 0.117, "width": 0.262, "height": 0.194},
        "note": "Manually placed: 'sketch the magnetic field on Figure 2b' has no ruled answer lines to detect.",
    },
    {
        "id": "B5b", "page": 19, "type": "drawing",
        "rect": {"x": 0.336, "y": 0.14, "width": 0.13, "height": 0.10},
        "note": "Manually placed: 'show the induced current direction on Figure 5' has no ruled answer lines to detect.",
    },
    {
        "id": "B15c", "page": 36, "type": "drawing",
        "rect": {"x": 0.094, "y": 0.163, "width": 0.63, "height": 0.443},
        "note": "Manually placed: part c.'s instruction ('draw the graph on the grid in Figure 16') refers back "
                "to the figure on this earlier page, which has no ruled answer lines of its own to detect.",
    },
    {
        "id": "B16b", "page": 39, "type": "drawing",
        "rect": {"x": 0.357, "y": 0.089, "width": 0.493, "height": 0.229},
        "note": "Manually placed: 'draw an arrow on the energy-level diagram in Figure 18' has no ruled answer lines to detect.",
    },
    {
        "id": "B17d", "page": 42, "type": "text",
        "rect": {"x": 0.115, "y": 0.225, "width": 0.386, "height": 0.128},
        "note": "Manually placed: spans the three narrow bordered boxes (independent/dependent/controlled "
                "variable), each narrower than the ruled-line detector's half-page-width threshold.",
    },
    {
        "id": "B17e", "page": 42, "type": "text",
        "rect": {"x": 0.39, "y": 0.431, "width": 0.179, "height": 0.145},
        "note": "Manually placed: fill-in-the-table question; box spans the table's r^2 column across all four rows.",
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
            continue  # already found automatically -- manual entry is a pure fallback
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
        print("All 52 Section B subparts matched exactly.")


if __name__ == "__main__":
    main()
