"""Hand-verifiable Section B interaction geometry for the 2025 VCE Physics
exam -- replaces the sequentially-numbered auto-detected geometry (B1, B2,
B3...) with geometry whose interaction ids match the actual VCAA subpart
labels (B1a, B1b, B11ci, B11cii, ...), which is what data/answers/2025.json's
interactionId values (built from the examination report's own "Question
11c.i" style headings) actually look like. Without this, Practice Mode could
never join an on-page answer box to its official answer.

Method: merge three independently-detected signals into one top-to-bottom
event stream per page, then assign each detected ruled-answer-line group to
whichever (question, letter, roman-numeral) label most recently preceded it:
  1. "Question N" headings (page.get_text("words"), the literal word
     "Question" followed by a digit token).
  2. Subpart letter labels "a." .. "h." at the page's left content margin.
  3. Nested roman-numeral labels "i." "ii." etc, indented further right than
     the letters (confirmed at x~112-116pt vs letters' x~37/88pt across the
     pages inspected -- but not actually needed for matching since "i."/"ii."
     never collides with the [a-h]. letter pattern).
Ruled answer lines are found the same way generate_paper_assets.py finds
them (its own answer_line_rows/raster_answer_line_rows + line_groups).

A question with no subpart letter at all (e.g. "Question 9") keeps the
letter/roman slots empty, giving interactionId "B9" -- matching
report_extraction_lib.py's heading_to_interaction_id("Question 9") -> "B9".

Output: data/2025-interactions.json (Section A preserved from the existing
audited auto-generated file, Section B replaced by this script's output).
Also copies straight into public/interactions/2025-exam.json so a rebuild
isn't required to see the result immediately; scripts/generate_paper_assets.py
regenerates that same file from data/2025-interactions.json on every run
regardless (2025-exam is in TUNED_INTERACTIONS), so this is just a
convenience, not a second source of truth.
"""
import json
import re
import sys
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_paper_assets import (  # noqa: E402
    answer_line_rows,
    first_question_heading_y_fraction,
    line_groups,
    page_text,
    raster_answer_line_rows,
)

ROOT = Path(__file__).resolve().parents[1]
EXAM_PATH = ROOT / "current-design-2024-2027" / "2025-physics-exam.pdf"
EXISTING_INTERACTIONS = ROOT / "public" / "interactions" / "2025.json"
OUT_PATH = ROOT / "data" / "2025-interactions.json"
PUBLIC_OUT = ROOT / "public" / "interactions" / "2025.json"

SECTION_B_FIRST_PAGE = 16
SECTION_B_LAST_PAGE = 47  # page 48 is "End of Question and Answer Book"; 49+ is the formula sheet

LETTER_RE = re.compile(r"^([a-h])\.$")
ROMAN_RE = re.compile(r"^([ivx]+)\.$", re.I)
QUESTION_HEADER_RE = re.compile(r"^Question\s+(\d+)\s*\(")


def heading_x0(page):
    """Returns the x0 of this page's own 'Question N' heading, or None if
    this is a continuation page with no heading of its own."""
    words = page.get_text("words")
    for index, word in enumerate(words[:-1]):
        if word[4].strip().lower().rstrip(".:()") == "question":
            nxt = words[index + 1][4].strip(".:()")
            if nxt.isdigit():
                return word[0]
    return None


def label_events(page, margin_x0):
    """Returns [(y0, kind, value)] for 'question'/'letter'/'roman' label
    tokens on this page, in the same units as ruled-line group y-fractions
    (0-1 of page height) so both can be merged into one sorted stream.

    Physics running text routinely contains bare single-letter variable
    names followed by a full stop ("...the initial value of a.") or diagram
    point labels, which are lexically indistinguishable from a genuine
    subpart label ("a.") by text alone -- confirmed on the 2025 exam itself
    (a stray "c." inside Question 17's body, a stray "a." inside Question
    18's body, both away from the margin). Real VCAA subpart labels always
    sit at the page's exact left content margin (identical x0 to that page's
    own "Question N" heading); filtering on x0 eliminates both false
    positives cleanly while keeping every real label. `margin_x0` is that
    page's known margin (from its own heading, or inherited from the same
    facing-page parity elsewhere in the document for continuation pages that
    have no heading of their own -- see main()'s per-parity tracking).
    """
    events = []
    words = page.get_text("words")
    height = page.rect.height
    for index, word in enumerate(words[:-1]):
        text = word[4].strip()
        x0 = word[0]
        if text.lower().rstrip(".:()") == "question":
            nxt = words[index + 1][4].strip(".:()")
            if nxt.isdigit():
                events.append((word[1] / height, "question", int(nxt)))
                continue
        if margin_x0 is None:
            continue
        m = LETTER_RE.match(text)
        if m and abs(x0 - margin_x0) <= 3:
            events.append((word[1] / height, "letter", m.group(1)))
            continue
        m = ROMAN_RE.match(text)
        if m and 15 <= (x0 - margin_x0) <= 45:
            events.append((word[1] / height, "roman", m.group(1).lower()))
    return events


def build_interaction_id(question, letter, roman):
    if question is None:
        return None
    return f"B{question}{letter or ''}{roman or ''}"


def response_type_for(text):
    return "drawing" if re.search(r"\bdraw|diagram|graph|sketch\b", text, re.I) else "text"


# The ruled-line detector only ever finds full-width horizontal answer
# lines (by design -- see generate_paper_assets.answer_line_rows's
# line_width > 0.5-page-width requirement) or, on pages with no vector
# lines at all, wide raster line-bands. Four 2025 subquestions genuinely
# have neither: two ask the student to annotate an existing figure directly
# (no ruled space at all, just blank room around/below the diagram) and two
# use narrower bordered boxes (a table cell column, two side-by-side boxes)
# that don't meet the "at least half the page wide" ruled-line heuristic.
# Every rect below was read directly off this exam PDF's own word/vector
# positions (figure captions, table borders, box borders -- see the
# reconnaissance in this script's git history/session notes) and confirmed
# by rendering it back onto the page image, not estimated by eye.
MANUAL_ENTRIES = [
    {
        "id": "B3a",
        "page": 20,
        "type": "drawing",
        "rect": {"x": 0.08, "y": 0.374, "width": 0.75, "height": 0.27},
        "note": "Manually placed: annotate-the-figure question (Figure 5) with no ruled answer lines to detect.",
    },
    {
        "id": "B11ci",
        "page": 33,
        "type": "text",
        "rect": {"x": 0.177, "y": 0.398, "width": 0.466, "height": 0.05},
        "note": "Manually placed: spans both the T1: and T2: bordered boxes (each narrower than the ruled-line detector's half-page-width threshold).",
    },
    {
        "id": "B18b",
        "page": 42,
        "type": "drawing",
        "rect": {"x": 0.08, "y": 0.449, "width": 0.75, "height": 0.252},
        "note": "Manually placed: annotate-the-figure question (Figure 21) with no ruled answer lines to detect.",
    },
    {
        "id": "B19a",
        "page": 45,
        "type": "text",
        "rect": {"x": 0.359, "y": 0.223, "width": 0.364, "height": 0.111},
        "note": "Manually placed: fill-in-the-table question; box spans the table's Variable column across all three rows.",
    },
]


def main():
    doc = fitz.open(EXAM_PATH)
    items = []
    seen_ids = {}

    # VCAA alternates which physical side carries the content margin between
    # facing pages (confirmed: even pages start their "Question"/letter
    # labels at x0=36.9, odd pages at x0=87.9 on this exam). A continuation
    # page with no "Question" heading of its own still has a definite
    # margin -- inherited here from any other page sharing its parity,
    # gathered in a first pass so page order doesn't matter. Using the mode
    # (not just the first or last value seen) guards against the rare page
    # whose only "Question N" text is actually a "Question N continues on
    # the next page" notice sitting mid-paragraph rather than the true
    # heading (confirmed on page 45, whose heading_x0 came back at x0=388
    # because of exactly this -- one outlier must never skew the margin for
    # every other page sharing that parity).
    from collections import Counter

    x0_samples = {0: [], 1: []}
    for page_number in range(SECTION_B_FIRST_PAGE, SECTION_B_LAST_PAGE + 1):
        x0 = heading_x0(doc[page_number - 1])
        if x0 is not None:
            x0_samples[page_number % 2].append(round(x0, 1))
    margin_x0_by_parity = {
        parity: (Counter(samples).most_common(1)[0][0] if samples else None)
        for parity, samples in x0_samples.items()
    }

    current_question = None
    current_letter = None
    current_roman = None

    for page_number in range(SECTION_B_FIRST_PAGE, SECTION_B_LAST_PAGE + 1):
        page = doc[page_number - 1]
        margin_x0 = margin_x0_by_parity[page_number % 2]
        text = page_text(page)
        if re.search(r"This page is blank", text, re.I):
            continue

        events = [(y, kind, value) for y, kind, value in label_events(page, margin_x0)]

        rows = answer_line_rows(page)
        from_raster = False
        if not rows:
            rows = raster_answer_line_rows(page)
            from_raster = True
        if page_number == SECTION_B_FIRST_PAGE:
            # Only this page carries the Instructions block above Question 1
            # -- see generate_paper_assets.py's make_written_fields for why
            # this must not apply to every page.
            heading_y = first_question_heading_y_fraction(page)
            if heading_y is not None:
                rows = [row for row in rows if row[1] >= heading_y - 0.005]
        groups = line_groups(rows)
        for group in groups:
            if from_raster and len(group) == 1:
                continue
            if len(group) == 1 and group[0][1] < 0.15:
                continue
            events.append((group[0][1], "linegroup", group))

        events.sort(key=lambda e: e[0])

        for y, kind, value in events:
            if kind == "question":
                current_question = value
                current_letter = None
                current_roman = None
            elif kind == "letter":
                current_letter = value
                current_roman = None
            elif kind == "roman":
                current_roman = value
            else:  # linegroup
                group = value
                interaction_id = build_interaction_id(current_question, current_letter, current_roman)
                if interaction_id is None:
                    continue  # a ruled line before any question heading was ever seen -- skip
                first, last = group[0], group[-1]
                rect = {
                    "x": first[0],
                    "y": max(0.08, round(first[1] - 0.022, 3)),
                    "width": min(0.78, first[2]),
                    "height": min(0.7, round((last[1] - first[1]) + 0.053, 3)),
                }
                # Two ruled-line groups can legitimately belong to the same
                # subpart (e.g. a working box plus a separate answer box) --
                # suffix a disambiguator rather than silently overwriting.
                base_id = interaction_id
                if base_id in seen_ids:
                    seen_ids[base_id] += 1
                    interaction_id = f"{base_id}-{seen_ids[base_id]}"
                else:
                    seen_ids[base_id] = 1

                items.append(
                    {
                        "id": interaction_id,
                        "section": "B",
                        "question": interaction_id[1:],
                        "page": page_number,
                        "type": response_type_for(text),
                        "rect": rect,
                        "note": "Auto-placed from ruled-line geometry, labelled by detected subpart; verify visually.",
                    }
                )

    detected_ids = {item["id"] for item in items}
    for entry in MANUAL_ENTRIES:
        if entry["id"] in detected_ids:
            continue  # already found automatically -- manual entry is a pure fallback
        items.append(
            {
                "id": entry["id"],
                "section": "B",
                "question": entry["id"][1:],
                "page": entry["page"],
                "type": entry["type"],
                "rect": entry["rect"],
                "note": entry["note"],
            }
        )

    # Preserve the existing (already visually verified) Section A geometry.
    existing = json.loads(EXISTING_INTERACTIONS.read_text(encoding="utf-8-sig"))
    section_a = [item for item in existing if item.get("section") == "A"]

    combined = section_a + items
    OUT_PATH.write_text(json.dumps(combined, indent=2), encoding="utf-8")
    PUBLIC_OUT.write_text(json.dumps(combined, indent=2), encoding="utf-8")

    ids = {item["id"] for item in items}
    print(f"Section A preserved: {len(section_a)}")
    print(f"Section B generated: {len(items)} ({len(ids)} distinct ids)")
    dupes = {k: v for k, v in seen_ids.items() if v > 1}
    if dupes:
        print(f"Split/duplicate base ids (2 boxes for same subpart): {dupes}")


if __name__ == "__main__":
    main()
