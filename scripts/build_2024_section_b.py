"""Section B interaction geometry for the 2024 VCE Physics exam.

2024's exam PDF has no extractable text layer at all (confirmed: 0 fonts,
every character rendered as a vector outline -- see Missing_Resources.md),
so build_2025_section_b.py's approach (find "Question N"/"a."/"b." text
tokens by position) cannot work here. Ruled answer lines are still real
vector drawings though, so answer_line_rows/raster_answer_line_rows still
find them -- what's missing is only the *label* for each detected line
group.

Method: the examination report's own question walk (extract_section_b_
questions) already gives the true, ordered sequence of subpart ids for the
whole paper (B1a, B1b, B2a, ... in document order) -- VCAA's report always
follows the same order as the exam questions. Zipping the auto-detected
line-groups against that ordered id list 1:1 would work, EXCEPT the counts
don't match exactly (54 detected groups vs 52 expected subparts for 2024 --
confirmed by direct count), meaning some subpart has two separate answer
lines (e.g. a working box plus a separate final-answer box). A silent 1:1
zip would misassign every subpart after the first such mismatch.

So this script renders every Section B page with its auto-detected groups
numbered in sequence-order, alongside the expected id list, specifically to
make that kind of drift fast to catch by eye (see render_debug()) --
checked once, then the confirmed mapping is hard-coded into
GROUP_TO_SUBPART below, the same way generate_paper_assets.py's
MANUAL_MCQ_POSITIONS records a hand-confirmed correction rather than
re-deriving it on every run.
"""
import json
import sys
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_paper_assets import (  # noqa: E402
    answer_line_rows,
    line_groups,
    raster_answer_line_rows,
)

ROOT = Path(__file__).resolve().parents[1]
EXAM_PATH = ROOT / "current-design-2024-2027" / "2024-physics-exam.pdf"
RAW_REPORT = ROOT / "data" / "raw" / "2024-report-extract.json"
EXISTING_INTERACTIONS = ROOT / "public" / "interactions" / "2024.json"
OUT_PATH = ROOT / "data" / "2024-interactions.json"
PUBLIC_OUT = ROOT / "public" / "interactions" / "2024.json"

SECTION_B_FIRST_PAGE = 16
SECTION_B_LAST_PAGE = 48


def detected_groups():
    """Returns [(page_number, group)] for every auto-detected ruled-line
    group on Section B pages, in reading order (page, then y-position)."""
    doc = fitz.open(EXAM_PATH)
    out = []
    for page_number in range(SECTION_B_FIRST_PAGE, SECTION_B_LAST_PAGE + 1):
        page = doc[page_number - 1]
        rows = answer_line_rows(page)
        from_raster = False
        if not rows:
            rows = raster_answer_line_rows(page)
            from_raster = True
        for group in line_groups(rows):
            if from_raster and len(group) == 1:
                continue
            if len(group) == 1 and group[0][1] < 0.15:
                continue
            out.append((page_number, group))
    return out


def render_debug():
    """Renders every Section B page with its detected groups numbered in
    sequence order, so a mismatch against the expected 52-id sequence is a
    quick visual scan rather than blind trust in a 1:1 zip. Run once,
    manually; not part of the normal build."""
    groups = detected_groups()
    expected_ids = [q["interactionId"] for q in json.loads(RAW_REPORT.read_text(encoding="utf-8"))["sectionB"]]
    print(f"detected groups: {len(groups)}, expected subparts: {len(expected_ids)}")

    doc = fitz.open(EXAM_PATH)
    by_page = {}
    for index, (page_number, group) in enumerate(groups):
        by_page.setdefault(page_number, []).append((index, group))

    out_dir = ROOT / "scratch-2024-debug"
    out_dir.mkdir(exist_ok=True)
    for page_number, items in sorted(by_page.items()):
        page = doc[page_number - 1]
        for index, group in items:
            first, last = group[0], group[-1]
            rect = fitz.Rect(
                first[0] * page.rect.width,
                max(0.05, first[1] - 0.022) * page.rect.height,
                (first[0] + first[2]) * page.rect.width,
                (last[1] + 0.03) * page.rect.height,
            )
            page.draw_rect(rect, color=(1, 0, 0), width=1.2)
            label = f"#{index}"
            if index < len(expected_ids):
                label += f" ({expected_ids[index]})"
            page.insert_text((rect.x0, rect.y0 - 3), label, fontsize=9, color=(0, 0, 0.8))
        pix = page.get_pixmap(dpi=100)
        pix.save(str(out_dir / f"p{page_number}.png"))
    print(f"Rendered {len(by_page)} pages to {out_dir}")


# ---------------------------------------------------------------------------
# Hand-confirmed mapping from detected-group sequence index -> subpart id,
# for every one of the 54 groups detected() finds. This replaced an earlier
# "skip a few spurious groups, otherwise consume expected_ids sequentially"
# approach: that assumption broke the moment a *genuinely undetectable*
# subpart appeared (five of them do -- see MANUAL_ENTRIES below), because
# sequential consumption has no way to know a slot must be skipped without a
# group to skip it *at*. A fully explicit index -> id table sidesteps that
# rather than layering more special-casing onto the sequential version.
#
# Built by rendering every Section B page via render_debug() and walking it
# page by page against the report's own ordered subpart sequence (see module
# docstring). `None` means the detected group is a false positive from the
# line-clustering heuristic picking up ruled-look page furniture that isn't
# an answer box at all -- confirmed by inspecting the actual page render in
# each case, not inferred from the count mismatch alone:
#   0  -- a rule line under the Section B instructions header
#   5  -- the ground/cliff hatching in Question 3's Figure 3
#   9  -- the wall hatching in Question 4's Figure 4 (crash-test wall)
#   10 -- the x-axis of Question 4's Figure 5 (preview graph, shown before
#         the question asking students to use it)
#   13 -- the floor hatching in Question 5's Figure 7
#   26 -- the t-axis of Question 10's Figure 14
#   35 -- the ground baseline in Question 13's Figure 17
# (54 detected - 7 false positives = 47 real matches; 47 + the 5
# MANUAL_ENTRIES below = 52, the report's true subpart count.)
# ---------------------------------------------------------------------------
GROUP_TO_SUBPART_OVERRIDES = {
    0: None, 1: "B1a", 2: "B1b", 3: "B2a", 4: "B2b", 5: None, 6: "B3a",
    7: "B3b", 8: "B3c", 9: None, 10: None, 11: "B4a", 12: "B4b", 13: None,
    14: "B5a", 15: "B5b", 16: "B6", 17: "B7a", 18: "B7b", 19: "B7c",
    20: "B8b", 21: "B8c", 22: "B9a", 23: "B9b", 24: "B9c", 25: "B10a",
    26: None, 27: "B10c", 28: "B11a", 29: "B11b", 30: "B11c", 31: "B12a",
    32: "B12b", 33: "B12c", 34: "B12d", 35: None, 36: "B13a", 37: "B13b",
    38: "B13c", 39: "B13d", 40: "B13e", 41: "B14a", 42: "B14b", 43: "B15a",
    44: "B15b", 45: "B15c", 46: "B15d", 47: "B16b", 48: "B16ci",
    49: "B16d", 50: "B16e", 51: "B16f", 52: "B16g", 53: "B16h",
}

# Subparts with no ruled-line answer box at all -- a sketch-on-the-provided-
# figure task, a table cell, or a bare unit box with no working lines above
# it -- so line_groups() has nothing to detect. Rects were read directly off
# a clean 110dpi page render using the same numpy ink-row/ink-column scan
# technique as generate_paper_assets.py's MANUAL_MCQ_POSITIONS_2024 (see that
# table's docstring), not eyeballed.
MANUAL_ENTRIES = [
    {
        "id": "B8a", "section": "B", "question": "8a", "page": 28, "type": "drawing",
        "rect": {"x": 0.178, "y": 0.241, "width": 0.367, "height": 0.113},
        "note": "Hand-placed: 'sketch field lines on Figure 10' has no ruled answer box -- "
                "rect covers the blank gap between the thundercloud and the ground in the figure itself.",
    },
    {
        "id": "B10b", "section": "B", "question": "10b", "page": 32, "type": "text",
        "rect": {"x": 0.094, "y": 0.872, "width": 0.418, "height": 0.040},
        "note": "Hand-placed: 'read peak-to-peak voltage and frequency off the graph' has no ruled "
                "working box, only two bare unit boxes (V, Hz) side by side -- rect spans both.",
    },
    {
        "id": "B16a", "section": "B", "question": "16a", "page": 43, "type": "text",
        "rect": {"x": 0.310, "y": 0.563, "width": 0.320, "height": 0.082},
        "note": "Hand-placed: the classification/variable response is a 3-row table, not ruled "
                "lines -- rect covers the 'Variable' column across all three rows.",
    },
    {
        "id": "B16cii", "section": "B", "question": "16cii", "page": 45, "type": "text",
        "rect": {"x": 0.176, "y": 0.331, "width": 0.184, "height": 0.042},
        "note": "Hand-placed: 'threshold frequency' is a bare unit box (Hz) with no ruled working lines above it.",
    },
    {
        "id": "B16ciii", "section": "B", "question": "16ciii", "page": 45, "type": "text",
        "rect": {"x": 0.176, "y": 0.431, "width": 0.184, "height": 0.041},
        "note": "Hand-placed: 'work function of the metal' is a bare unit box (eV) with no ruled working lines above it.",
    },
]

# Subparts whose answer is a sketch/plot on a provided figure or axes, rather
# than free text -- rendered with a "Drawing response placeholder" instead
# of a blank textarea (see WrittenControl.tsx). Everything else defaults to
# "text"; MANUAL_ENTRIES set their own type explicitly above.
DRAWING_SUBPARTS = {"B4b", "B16b"}


def main():
    if "--debug" in sys.argv:
        render_debug()
        return

    expected_ids = [q["interactionId"] for q in json.loads(RAW_REPORT.read_text(encoding="utf-8"))["sectionB"]]
    groups = detected_groups()

    items = []
    for group_index, (page_number, group) in enumerate(groups):
        subpart_id = GROUP_TO_SUBPART_OVERRIDES.get(group_index, "__unmapped__")
        if subpart_id is None:
            continue
        if subpart_id == "__unmapped__":
            print(f"WARNING: detected group {group_index} (page {page_number}) has no mapping -- skipped")
            continue

        first, last = group[0], group[-1]
        rect = {
            "x": first[0],
            "y": max(0.08, round(first[1] - 0.022, 3)),
            "width": min(0.78, first[2]),
            "height": min(0.7, round((last[1] - first[1]) + 0.053, 3)),
        }
        items.append({
            "id": subpart_id,
            "section": "B",
            "question": subpart_id[1:],
            "page": page_number,
            "type": "drawing" if subpart_id in DRAWING_SUBPARTS else "text",
            "rect": rect,
            "note": "Auto-placed from ruled-line geometry, hand-confirmed against the report's own "
                    "subpart sequence via a page-by-page visual review (no text layer to detect labels "
                    "from directly) -- see GROUP_TO_SUBPART_OVERRIDES in this script.",
        })

    for entry in MANUAL_ENTRIES:
        items.append(entry)

    existing = json.loads(EXISTING_INTERACTIONS.read_text(encoding="utf-8-sig"))
    section_a = [item for item in existing if item.get("section") == "A"]
    combined = section_a + items

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(combined, indent=2), encoding="utf-8")
    PUBLIC_OUT.write_text(json.dumps(combined, indent=2), encoding="utf-8")

    got_ids = [item["id"] for item in items]
    got_set = set(got_ids)
    missing = [i for i in expected_ids if i not in got_set]
    dupes = sorted({i for i in got_ids if got_ids.count(i) > 1})
    print(f"Section A preserved: {len(section_a)}")
    print(f"Section B placed: {len(items)} / {len(expected_ids)} expected")
    if missing:
        print(f"Missing: {missing}")
    if dupes:
        print(f"DUPLICATES: {dupes}")
    if not missing and not dupes and len(items) == len(expected_ids):
        print("All 52 Section B subparts matched exactly.")


if __name__ == "__main__":
    main()
