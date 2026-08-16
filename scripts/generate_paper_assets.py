"""Discovers every exam PDF across the three source eras, copies each into
public/papers/, extracts that paper's own era-correct formula sheet (VCAA
appends it to the back of every exam PDF -- confirmed by inspecting 2025,
2017, 2016 and 2002's own PDFs directly) into public/formula-sheets/, and
writes best-effort interaction geometry + public/papers.json.

Structural invariants baked in here are from direct reconnaissance of the
source cover pages (see docs/DATA-ARCHITECTURE.md), not guessed:
  - current-design-2024-2027 (2024-2025): 15 min reading, 150 min writing,
    Section A = 20 MCQ (20 marks), Section B = 100 marks, total 120.
  - previous-design-2017-2023 (2017-2023): 15 min reading, 150 min writing,
    Section A = 20 MCQ (20 marks), Section B = 110 marks, total 130.
  - archive-2002-2016: NO multiple choice at all -- "Section A" there means
    compulsory Area-of-Study short-answer questions and "Section B" means a
    pick-one-of-six elective Detailed Study, a fundamentally different
    structure. 2013-2016 is a single 150-mark, 150-minute exam; 2002-2012
    split into two 90-mark, 90-minute sittings (Exam 1 in June, Exam 2 in
    November), each with its own elective options -- both confirmed off
    those years' own cover pages. Every archive interaction is modelled as
    Section B (written) regardless of VCAA's own Section A/B labelling,
    because this app's Section A always means auto-gradeable MCQ.

Per the build brief's sequence, only 2025 is meant to be airtight right now:
its interaction geometry is hand-verified and checked into
data/2025-interactions.json, loaded verbatim below rather than
auto-generated. Every other paper gets best-effort auto-generated geometry
so Timed Mode works immediately; those get refined working backward through
years, matching how 2025 was done.
"""
import json
import re
import shutil
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PAPERS_DIR = PUBLIC / "papers"
INTERACTIONS_DIR = PUBLIC / "interactions"
FORMULA_DIR = PUBLIC / "formula-sheets"

SOURCE_FOLDERS = [
    ("current-design-2024-2027", "current"),
    ("previous-design-2017-2023", "previous"),
    ("archive-2002-2016", "archive"),
]

# (readingMinutes, writingMinutes, totalMarks) -- see module docstring for
# how each was confirmed.
ERA_DURATIONS = {
    "current": (15, 150, 120),
    "previous": (15, 150, 130),
}
ARCHIVE_SINGLE = (15, 150, 150)  # 2013-2016
ARCHIVE_DUAL = (15, 90, 90)  # 2002-2012 (and the 2004 pilot), per sitting

# Interaction geometry hand-verified against the rendered PDF for 2025 --
# the "airtight" flagship year -- takes precedence over auto-generation.
TUNED_INTERACTIONS = {"2025", "2024", "2023", "2022", "2021"}

# 2024's exam has no text layer at all (confirmed: 0 fonts, every character
# a vector path -- see Missing_Resources.md), so Section A geometry can't be
# found by searching "Question N"/"A."-"D." text the way every other year
# is. The vector-path line-clustering heuristic (make_mcqs_no_text_layer)
# correctly recovers 12 of the 20 -- exactly the plain-list questions --
# but questions whose options are a 2x2 grid of diagrams/graphs or a
# genuine multi-column table (Force|Torque, Current direction|Induced
# field, etc.) don't form its "4 evenly-spaced single-line labels" pattern.
# Rather than layer more heuristics onto a page-layout quirk this
# subject-specific, this is a complete, hand-confirmed table for all 20
# questions -- mirroring exactly how the sibling VCE Chemistry app handled
# its own text-layer-less 2024 exam (a full MANUAL_MCQ_POSITIONS table, not
# a partial one).
#
# Every (page, x, y[, height]) entry below was cross-checked pixel-precisely
# against a clean 110dpi render of the actual page: a numpy ink-row/ink-
# column scan of the rendered grayscale image (thresholding, then finding
# contiguous dark bands) locates the true bottom edge of each option block
# and the top edge of whatever follows it, so every box sits in a genuinely
# blank gap rather than an eyeballed guess -- an eyeballed first pass on
# this same table originally clipped into option diagrams on 4 questions
# and into the next question's heading on 3 others; both classes of error
# are what this scan-based re-derivation exists to rule out. height is
# omitted (defaults to 0.032) except where the gap before the next heading
# is too narrow for that default and a shorter box is used instead.
# See docs/INTERACTION-GEOMETRY-REVIEW.md.
MANUAL_MCQ_POSITIONS_2024 = {
    1: (2, 0.059, 0.660),
    2: (2, 0.059, 0.883),
    3: (3, 0.06, 0.608),    # 2x2 grid of force-diagram options -- placed below the whole grid (D row bottom = 769px/1287)
    4: (4, 0.059, 0.818),
    5: (5, 0.06, 0.747),    # 2x2 grid of energy-vs-time graphs -- below the whole grid (D row bottom = 947px/1287)
    6: (6, 0.059, 0.316),
    7: (7, 0.14, 0.621),    # Force/Torque comparison table -- precise (D row y1=519.9pt)
    8: (8, 0.059, 0.476, 0.024),   # D line bottom=608px, "Question 9" heading top=647px -- shortened to clear it
    9: (8, 0.059, 0.743),
    10: (9, 0.14, 0.598),   # 2x2 grid of magnetic-flux graphs -- below the whole grid (D row bottom = 759px/1287)
    11: (9, 0.141, 0.812),
    12: (10, 0.06, 0.576),  # Current-direction/induced-field table -- precise (D row y1=482.0pt)
    13: (11, 0.141, 0.446, 0.024),  # D line bottom=573px, "Question 14" heading top=609px -- shortened to clear it
    14: (11, 0.14, 0.841),  # wrapped-text options (relativistic length measurements) -- D wraps to 2 lines, ending at 1075px/1287
    15: (12, 0.059, 0.285, 0.024),  # D line bottom=366px, "Question 16" heading top=402px -- shortened to clear it
    16: (12, 0.059, 0.803),
    17: (13, 0.14, 0.450),  # 2x2 grid of standing-wave diagrams -- below the whole grid (D row bottom = 564px/1287)
    18: (14, 0.059, 0.540),
    19: (15, 0.39, 0.40),   # 2x2 grid of v-vs-r graphs -- "Question 20" follows immediately below, so placed in
                             # the blank gap between the A/B and C/D columns instead (x=312-567px is empty for the
                             # full row height, confirmed by an ink-column scan) rather than shortened below the grid
    20: (15, 0.141, 0.623),
}


def slug_for(path: Path) -> str:
    name = path.stem.lower()
    name = name.replace("-physics-", "-")
    name = re.sub(r"-exam$", "", name)  # single-sitting years: "2025-exam" -> "2025" (keeps "-exam1"/"-exam2")
    name = re.sub(r"[^a-z0-9]+", "-", name).strip("-")
    return name


def title_for(path: Path, era: str) -> str:
    name = path.stem
    year_match = re.search(r"(20\d{2})", name)
    year = year_match.group(1) if year_match else "Sample"
    if "pilot" in name.lower():
        suffix = " Pilot"
    else:
        suffix = ""
    if "exam1" in name.lower():
        return f"{year} VCE Physics{suffix} Exam 1"
    if "exam2" in name.lower():
        return f"{year} VCE Physics{suffix} Exam 2"
    return f"{year} VCE Physics{suffix}"


def find_exam_pdfs():
    results = []
    for folder_name, era in SOURCE_FOLDERS:
        folder = ROOT / folder_name
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.pdf")):
            if "exam" not in path.stem.lower():
                continue
            results.append((path, era))
    # Most recent first, dual exams in sitting order.
    def sort_key(item):
        path, era = item
        year_match = re.search(r"(20\d{2})", path.stem)
        year = int(year_match.group(1)) if year_match else 0
        era_rank = {"current": 0, "previous": 1, "archive": 2}[era]
        exam_rank = 1 if "exam2" in path.stem.lower() else 0
        pilot_rank = 1 if "pilot" in path.stem.lower() else 0
        return (era_rank, -year, pilot_rank, exam_rank)

    return sorted(results, key=sort_key)


def page_text(page):
    return page.get_text("text").replace("\n", " ")


_OPTION_LABEL_RE = re.compile(r"^[A-D]\.$")


def _vector_text_line_rects(page):
    """For pages with no extractable text layer at all (confirmed: 0 fonts
    -- 2024's exam PDF renders every character as an individually-drawn
    vector path, not a font glyph), PyMuPDF's get_drawings() still groups
    each contiguous run of character paths into one compound fill ('f')
    drawing per visual text line, complete with a real bounding box --
    confirmed directly: a rect like (37.7, 508.4, 47.1, 516.3) is exactly
    where a rendered "B." option label sits, even though there is no way to
    ask what text it contains. This recovers line *positions* (never
    content) from that, which is enough to find the option-label column
    pattern below without OCR."""
    rects = []
    for d in page.get_drawings():
        if d.get("type") != "f":
            continue
        r = d.get("rect")
        if r is None:
            continue
        rects.append(r)
    return rects


def _known_margin_x(page_number):
    """VCAA alternates which side carries the content margin between facing
    pages (confirmed independently for both Section A and Section B: even
    pages start at x~36.9pt, odd pages at x~87.9pt, on this exam's own
    layout). Physics answers routinely include scientific notation
    ("4.0 x 10^-2 N"), whose superscript exponent digits are short enough
    to otherwise pass the option-label size filter and get clustered as
    spurious extra "questions" at the *value* column's x position --
    confirmed directly (2024 page 8: 7 raw clusters detected for what are
    really only 2 real questions). Restricting to the known label-column x
    eliminates this: exponents never sit exactly at the margin."""
    return 36.9 if page_number % 2 == 0 else 87.9


def find_option_label_clusters_no_text(page, page_number=None):
    """No-text-layer equivalent of scanning for "A." "B." "C." "D." word
    tokens: finds groups of exactly 4 short vector-drawn lines (the option
    labels' own glyph runs are short -- a letter plus a period, confirmed
    ~7-11pt wide, ~6-9pt tall) sharing the same left x-position (the option
    column) with the regular ~18-21pt line spacing confirmed between actual
    "A."/"B."/"C."/"D." labels on this exam's own pages. Returns
    [(x0, y0_of_A, y1_of_D)] sorted top-to-bottom -- one entry per detected
    question on this page, in reading order. Not perfect (options laid out
    as a table, or a fraction spanning two lines, can suppress or split a
    match -- see build_2024's manual-override pattern for the residual
    cases caught by visual review), but accounts for the large majority
    without any per-question hand placement.
    """
    margin_x = _known_margin_x(page_number) if page_number is not None else None
    candidates = []
    for r in _vector_text_line_rects(page):
        w, h = r.x1 - r.x0, r.y1 - r.y0
        if not (5 <= h <= 9 and 3 <= w <= 13):
            continue
        if margin_x is not None and abs(r.x0 - margin_x) > 2.0:
            continue
        candidates.append((r.x0, r.y0, r.y1))
    candidates.sort(key=lambda c: c[0])

    x_groups = []
    for c in candidates:
        for g in x_groups:
            if abs(g[-1][0] - c[0]) <= 2.0:
                g.append(c)
                break
        else:
            x_groups.append([c])

    clusters = []
    for g in x_groups:
        g.sort(key=lambda c: c[1])
        i = 0
        while i < len(g):
            group = [g[i]]
            j = i + 1
            while j < len(g):
                gap = g[j][1] - group[-1][1]
                if 14 <= gap <= 26:
                    group.append(g[j])
                    j += 1
                else:
                    break
            if len(group) == 4:
                clusters.append((group[0][0], group[0][1], group[-1][2]))
                i = j
            else:
                i += 1
    return sorted(clusters, key=lambda c: c[1])


def option_block_bottom(page, heading_y0, next_heading_y0):
    """Finds the y1/x0 to place the MCQ selector just below the last (D.)
    option, between one question heading and the next, by the exact
    left-margin "A." "B." "C." "D." tokens (confirmed stable across the 2025
    exam's own page layout). VCAA alternates which side carries the grey "Do
    not write in this area" margin between facing pages, so the options'
    left x-position genuinely differs page to page -- reading it from the
    real word positions here (rather than a fixed constant) adapts to that
    automatically. Returns (x0_frac, y1_frac) or None if not found (falls
    back to the coarser heading-relative heuristic).

    Some questions lay options out as a table (e.g. a grid of direction
    arrows per option) rather than a plain list -- there the "D." label's own
    text sits well above the true bottom of that option's row/cell, so
    anchoring to the label text alone would land the selector overlapping
    the table. Preferring the lowest ruled table border within a short
    window below the D label (found the same way report extraction finds
    ruled lines, via get_drawings()) accounts for that; plain-list questions
    have no such border below D and fall back to the label position.
    """
    words = page.get_text("words")
    candidates = [
        w for w in words
        if _OPTION_LABEL_RE.match(w[4].strip()) and heading_y0 - 2 <= w[1] < next_heading_y0
    ]
    if not candidates:
        return None
    last = max(candidates, key=lambda w: w[1])
    x0, d_y0, d_y1 = last[0], last[1], last[3]

    # Option D's own answer text can wrap onto a second line below the "D."
    # label itself (long-worded options) -- anchoring to the label word
    # alone would then overlap that wrapped continuation. Extend the anchor
    # to the lowest word that starts at or after D's label, up to the next
    # heading, which naturally includes any wrapped lines belonging to D.
    # Restricted to roughly the same content column as the option labels --
    # the page's rotated "Do not write in this area" sidebar text is split
    # into individual word fragments by PyMuPDF, and at least one of those
    # ("write") lands with a y0 inside this window but a y1 well past it
    # (its bounding box follows the rotated glyph run), which would
    # otherwise corrupt the anchor with a margin note nowhere near the
    # actual options.
    trailing_words = [
        w for w in words
        if d_y0 - 1 <= w[1] < next_heading_y0 and x0 - 20 <= w[0] <= x0 + 480
    ]
    d_y1 = max((w[3] for w in trailing_words), default=d_y1)

    search_bottom = d_y1 + 90  # ~8% of a typical page height, in points
    best_border_y = None
    for d in page.get_drawings():
        r = d.get("rect")
        if r is None or d.get("fill") not in ((0.0, 0.0, 0.0), None):
            continue
        if r.height >= 1.5 or r.width < 20:
            continue  # not a thin horizontal ruled line
        if r.x0 > x0 + 250 or r.x1 < x0:
            continue  # not roughly under the options block
        if d_y1 - 2 <= r.y0 <= search_bottom:
            if best_border_y is None or r.y0 > best_border_y:
                best_border_y = r.y0

    anchor_y1 = best_border_y if best_border_y is not None else d_y1
    return x0 / page.rect.width, anchor_y1 / page.rect.height


def detect_section_b_start(doc, has_mcq, section_a_total):
    if not has_mcq:
        return 1
    for page_index in range(doc.page_count):
        text = page_text(doc[page_index])
        if "Contents" in text[:900]:
            continue
        section_match = re.search(r"\bSECTION\s+B\b|\bSection\s+B\b", text)
        if section_match and section_match.start() < 350:
            return page_index + 1
    if all(not page_text(doc[i]).strip() for i in range(min(4, doc.page_count))):
        return 16  # no text layer at all -- 2024's known layout
    return None


# Registry of complete, hand-confirmed Section A tables for no-text-layer
# papers where the auto-detection heuristic can't reach every question
# (see MANUAL_MCQ_POSITIONS_2024's docstring above for why). Keyed by slug.
MANUAL_MCQ_POSITIONS_BY_SLUG = {"2024": MANUAL_MCQ_POSITIONS_2024}


def _mcq_item_from_position(question, page_number, x_fraction, y_fraction, note, height=0.032):
    rect = {
        "x": round(x_fraction, 3),
        "y": round(y_fraction, 3),
        "width": 0.145,
        "height": round(height, 3),
    }
    return {
        "id": f"A{question}",
        "section": "A",
        "question": str(question),
        "page": page_number,
        "type": "mcq",
        "rect": rect,
        "note": note,
    }


def make_mcqs_no_text_layer(doc, total, section_b_start, slug=None):
    """No-text-layer equivalent of make_mcqs's main loop: since there's no
    "Question N" text to key off of, this zips the detected 4-option
    clusters (find_option_label_clusters_no_text) sequentially against
    question numbers 1..total in page/reading order -- safe when every
    Section A question is laid out as a plain option list, since VCAA lays
    Section A out strictly in question-number order and detection then
    finds exactly one cluster per question, in order.

    That assumption breaks for any question whose options are a 2x2 grid of
    diagrams/graphs or a genuine multi-column table -- those produce zero
    clusters, silently shifting every subsequent question's auto-assigned
    number (confirmed for 2024 by direct page-by-page visual audit -- see
    MANUAL_MCQ_POSITIONS_2024). For a slug with a complete hand-confirmed
    table in MANUAL_MCQ_POSITIONS_BY_SLUG, that table is used directly
    instead of trusting the sequential zip at all."""
    if slug in MANUAL_MCQ_POSITIONS_BY_SLUG:
        positions = MANUAL_MCQ_POSITIONS_BY_SLUG[slug]
        items, seen = [], set()
        for question in range(1, total + 1):
            if question not in positions:
                continue
            entry = positions[question]
            page_number, x_fraction, y_fraction = entry[0], entry[1], entry[2]
            height = entry[3] if len(entry) > 3 else 0.032
            items.append(_mcq_item_from_position(
                question, page_number, x_fraction, y_fraction,
                "Hand-confirmed placement (no text layer to auto-detect from); "
                "see MANUAL_MCQ_POSITIONS_BY_SLUG in generate_paper_assets.py.",
                height=height,
            ))
            seen.add(question)
        return items, seen

    clusters = []  # (page_number, x0, y0, y1)
    for page_number in range(1, min(section_b_start, doc.page_count + 1)):
        page = doc[page_number - 1]
        for x0, y0, y1 in find_option_label_clusters_no_text(page, page_number):
            clusters.append((page_number, x0, y0, y1))

    items = []
    seen = set()
    for question, (page_number, x0, y0, y1) in enumerate(clusters[:total], start=1):
        page = doc[page_number - 1]
        rect = {
            "x": round(x0 / page.rect.width, 3),
            "y": min(0.94, round((y1 + 3) / page.rect.height, 3)),
            "width": 0.145,
            "height": 0.032,
        }
        items.append({
            "id": f"A{question}",
            "section": "A",
            "question": str(question),
            "page": page_number,
            "type": "mcq",
            "rect": rect,
            "note": "Auto-placed from vector-path line clustering (no text layer to search); confirm with developer coordinate mode.",
        })
        seen.add(question)
    return items, seen


def _page_footer_y0(page):
    """Returns the y0 of this page's own running footer ('SECTION A --
    continued' or similar), or None if not found. Used as a ceiling for MCQ
    placement in place of the raw page height when a question is the last
    heading on its page: without this, option_block_bottom's trailing-words
    search window (bounded by "the next heading, or the page height if
    there is none on this page") would extend all the way past the footer
    to the literal bottom edge of the page, sweeping the footer's own text
    into the option block and placing the selector box far below the real
    options (confirmed on 2023's Question 1, whose selector landed at
    y=0.89 -- past the footer -- when the true D option sat at y=0.44 with
    nothing else on the rest of the page)."""
    words = page.get_text("words")
    for index, word in enumerate(words[:-1]):
        if word[4].strip().upper() == "SECTION" and word[1] > page.rect.height * 0.5:
            nxt = words[index + 1][4].strip() if index + 1 < len(words) else ""
            if nxt.upper() in ("A", "B"):
                return word[1]
    return None


def make_mcqs(doc, total, section_b_start, slug=None):
    if total <= 0:
        return []
    if not doc[0].get_fonts():
        # No embedded fonts anywhere on the cover page is the confirmed
        # signal for "this whole PDF has no text layer" (see 2024's exam --
        # every character is a vector path, not a font glyph).
        items, seen = make_mcqs_no_text_layer(doc, total, section_b_start, slug)
    else:
        items, seen = [], set()
    if len(seen) == total:
        return sorted(items, key=lambda item: int(item["question"]))

    for page_number in range(1, min(section_b_start, doc.page_count + 1)):
        page = doc[page_number - 1]
        words = page.get_text("words")
        headings = []  # (question_number, y0_abs)
        for index, word in enumerate(words[:-1]):
            if word[4].lower().strip(".:") == "question":
                nxt = words[index + 1][4].strip(".:")
                if nxt.isdigit():
                    headings.append((int(nxt), word[1]))
        headings.sort(key=lambda h: h[1])
        page_ceiling = _page_footer_y0(page) or page.rect.height

        for idx, (question, heading_y0) in enumerate(headings):
            if not (1 <= question <= total) or question in seen:
                continue
            next_y0 = headings[idx + 1][1] if idx + 1 < len(headings) else page_ceiling
            found = option_block_bottom(page, heading_y0, next_y0)
            seen.add(question)
            if found:
                x0_frac, y1_frac = found
                next_y0_frac = next_y0 / page.rect.height
                # Hard ceiling: the box's bottom edge must never reach the
                # next question's heading. Prefer a full-height box with a
                # comfortable pad below D; when the page is laid out too
                # tightly for that, shrink the box (down to a usable floor)
                # rather than let it run into the next question's number --
                # a slightly shorter selector reads far better than one that
                # visually strikes through the next heading.
                y = round(y1_frac + 0.004, 3)
                height = min(0.032, max(0.016, next_y0_frac - y - 0.004))
                note = None
                if height < 0.032:
                    note = "Little vertical room before the next question; box height reduced. Confirm with developer coordinate mode."
                y = min(0.94, y)
                item = {
                    "id": f"A{question}",
                    "section": "A",
                    "question": str(question),
                    "page": page_number,
                    "type": "mcq",
                    "rect": {
                        "x": round(x0_frac, 3),
                        "y": y,
                        "width": 0.145,
                        "height": height,
                    },
                }
                if note:
                    item["note"] = note
                items.append(item)
            else:
                # Couldn't find the option-label tokens (e.g. options span an
                # unusual layout) -- fall back to a position just below the
                # question heading itself, flagged for manual review.
                items.append(
                    {
                        "id": f"A{question}",
                        "section": "A",
                        "question": str(question),
                        "page": page_number,
                        "type": "mcq",
                        "rect": {
                            "x": 0.06,
                            "y": min(0.92, max(0.08, round(heading_y0 / page.rect.height + 0.2, 3))),
                            "width": 0.145,
                            "height": 0.032,
                        },
                        "note": "Could not locate A-D option labels; confirm with developer coordinate mode.",
                    }
                )
    for question in range(1, total + 1):
        if question not in seen:
            page_number = min(2 + (question - 1) // 3, max(1, section_b_start - 1))
            y = 0.14 + ((question - 1) % 3) * 0.26
            items.append(
                {
                    "id": f"A{question}",
                    "section": "A",
                    "question": str(question),
                    "page": page_number,
                    "type": "mcq",
                    "rect": {"x": 0.858, "y": round(y, 3), "width": 0.112, "height": 0.035},
                    "note": "Generated fallback position (no text layer to detect from); confirm with developer coordinate mode.",
                }
            )
    return sorted(items, key=lambda item: int(item["question"]))


def answer_line_rows(page):
    rows = []
    width = page.rect.width
    height = page.rect.height
    for drawing in page.get_drawings():
        for item in drawing.get("items", []):
            if item[0] != "l":
                continue
            p1, p2 = item[1], item[2]
            line_width = abs(p2.x - p1.x) / width
            y = p1.y / height
            if abs(p1.y - p2.y) < 1.2 and line_width > 0.5 and 0.08 < y < 0.95:
                x1 = min(p1.x, p2.x) / width
                x2 = max(p1.x, p2.x) / width
                if x1 < 0 or x2 > 1 or x2 <= x1:
                    continue
                rows.append((round(x1, 3), round(y, 3), round(x2 - x1, 3)))
    rows.sort(key=lambda row: row[1])
    deduped = []
    for row in rows:
        if deduped and abs(row[1] - deduped[-1][1]) < 0.012:
            continue
        deduped.append(row)
    return deduped


def raster_answer_line_rows(page):
    pix = page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
    width = pix.width
    height = pix.height
    samples = pix.samples
    rows = []
    for y in range(int(height * 0.08), int(height * 0.95)):
        start = None
        runs = []
        offset = y * width * 3
        left = int(width * 0.09)
        right = int(width * 0.86)
        for x in range(left, right):
            i = offset + x * 3
            red, green, blue = samples[i], samples[i + 1], samples[i + 2]
            grey_line = (
                120 < red < 235
                and 120 < green < 235
                and 120 < blue < 235
                and max(red, green, blue) - min(red, green, blue) < 18
            )
            if grey_line and start is None:
                start = x
            elif not grey_line and start is not None:
                if x - start > width * 0.45:
                    runs.append((start, x))
                start = None
        if start is not None and right - start > width * 0.45:
            runs.append((start, right))
        for x1, x2 in runs:
            norm_x = x1 / width
            norm_width = (x2 - x1) / width
            if 0.08 <= norm_x <= 0.22 and norm_width >= 0.62:
                rows.append((round(norm_x, 3), round(y / height, 3), round(norm_width, 3)))

    deduped = []
    for row in rows:
        if deduped and abs(row[1] - deduped[-1][1]) < 0.01:
            old = deduped[-1]
            deduped[-1] = (min(old[0], row[0]), old[1], max(old[2], row[2]))
        else:
            deduped.append(row)
    return [row for row in deduped if row[2] > 0.5]


def line_groups(rows):
    groups = []
    current = []
    for row in rows:
        if current and row[1] - current[-1][1] > 0.055:
            groups.append(current)
            current = []
        current.append(row)
    if current:
        groups.append(current)
    return groups


def _is_skippable_section_b_page(text):
    """True for a page that's entirely 'this page is blank' filler, a
    formula-sheet cover, or the 'END OF QUESTION AND ANSWER BOOK' end
    marker with nothing else on it -- true for every one of those, since
    each is short enough that the marker text makes up virtually the whole
    page. Deliberately NOT a bare substring search: VCAA prints "END OF
    QUESTION AND ANSWER BOOK" as a one-line footer at the very bottom of the
    genuine final content page (confirmed on 2023's own exam, where that
    page still carries two full, real, ruled answer boxes above the
    footer) -- a substring search would discard real answer geometry along
    with the footer merely for sharing a page with it."""
    return bool(re.search(r"This page is blank|End of question|FORMULA SHEET|Formula Sheet", text[:80], re.I))


def first_question_heading_y_fraction(page):
    """Returns the y-fraction of the first 'Question N' heading on this page,
    or None if there isn't one. Section B's opening page carries an
    Instructions block above Question 1, whose own horizontal divider rule
    line is otherwise indistinguishable from a genuine ruled answer line to
    the geometry detector below -- excluding anything above the first real
    heading avoids manufacturing a phantom interaction out of that rule.

    Must apply the same "SECTION B -- Question N -- continued" footer
    filter as _is_real_question_heading: left unfiltered, this can find
    that bottom-of-page footer instead of the true top-of-page heading on
    a paper that prints it (confirmed on 2022's own Section B opening page,
    where the unfiltered version returned y=0.87 from the footer -- which
    then excluded every ruled row above it, silently discarding Question
    1a's own real answer box along with the Instructions block it was
    actually meant to strip)."""
    words = page.get_text("words")
    for index, word in enumerate(words[:-1]):
        if word[4].lower().strip(".:()") == "question" and _is_real_question_heading(words, index):
            return word[1] / page.rect.height
    return None


def make_written_fields(doc, section_b_start, start_counter=1, id_prefix="B"):
    start = section_b_start or 1
    items = []
    counter = start_counter
    for page_number in range(start, doc.page_count + 1):
        page = doc[page_number - 1]
        text = page_text(page)
        if _is_skippable_section_b_page(text):
            continue
        rows = answer_line_rows(page)
        if not rows:
            rows = raster_answer_line_rows(page)
        from_raster = not answer_line_rows(page)
        if page_number == start:
            # Only Section B's own opening page carries the Instructions
            # block (with its own horizontal divider rule, indistinguishable
            # from a genuine ruled answer line by geometry alone) above
            # Question 1 -- applying this on every page would also strip a
            # legitimate answer line that happens to sit above THAT page's
            # own heading on a continuation page (e.g. part b.'s lines at
            # the top of a page whose Question N+1 heading appears further
            # down the same page).
            heading_y = first_question_heading_y_fraction(page)
            if heading_y is not None:
                rows = [row for row in rows if row[1] >= heading_y - 0.005]
        groups = line_groups(rows)
        for group in groups:
            if from_raster and len(group) == 1:
                continue
            first = group[0]
            last = group[-1]
            if len(group) == 1 and first[1] < 0.15:
                continue
            rect = {
                "x": first[0],
                "y": max(0.08, round(first[1] - 0.022, 3)),
                "width": min(0.78, first[2]),
                "height": min(0.7, round((last[1] - first[1]) + 0.053, 3)),
            }
            response_type = "drawing" if re.search(r"\bdraw|diagram|graph|sketch\b", text, re.I) else "text"
            items.append(
                {
                    "id": f"{id_prefix}{counter}",
                    "section": "B",
                    "question": str(counter),
                    "page": page_number,
                    "type": response_type,
                    "rect": rect,
                    "note": "Generated from PDF answer-line geometry; refine with developer coordinate mode if needed.",
                }
            )
            counter += 1
    return items


_LETTER_RE = re.compile(r"^([a-h])\.$")
_ROMAN_RE = re.compile(r"^([ivx]+)\.$", re.I)


def _is_real_question_heading(words, index):
    """True if the 'Question' token at `index` is a genuine question heading
    ('Question N (M marks)'), not the 'SECTION B – Question N – continued'
    running footer some previous-design years print at the bottom of every
    Section B page (confirmed on 2023's exam: same word text and even the
    same x0 as a real heading on some pages, differing only in that the
    footer's question number is followed by '–' rather than the opening
    paren of its mark allocation -- '(5', '(3', etc -- which a genuine
    heading always has immediately after the number)."""
    if index + 2 >= len(words):
        return False
    nxt = words[index + 1][4].strip(".:()")
    if not nxt.isdigit():
        return False
    return words[index + 2][4].startswith("(")


def _section_b_heading_x0(page):
    """Returns the x0 of this page's own 'Question N' heading, or None if
    this is a continuation page with no heading of its own."""
    words = page.get_text("words")
    for index, word in enumerate(words[:-1]):
        if word[4].strip().lower().rstrip(".:()") == "question" and _is_real_question_heading(words, index):
            return word[0]
    return None


def _section_b_label_events(page, margin_x0):
    """Returns [(y0_fraction, kind, value)] for 'question'/'letter'/'roman'
    label tokens on this page, in the same units as ruled-line group
    y-fractions so both can be merged into one sorted per-page stream.

    Physics running text routinely contains bare single-letter variable
    names followed by a full stop ("...the initial value of a.") or diagram
    point labels, lexically indistinguishable from a genuine subpart label
    ("a.") by text alone -- confirmed on the 2025 exam itself. Real VCAA
    subpart labels always sit at the page's exact left content margin
    (identical x0 to that page's own "Question N" heading); filtering on x0
    eliminates false positives cleanly while keeping every real label.
    `margin_x0` is that page's known margin (from its own heading, or
    inherited from the same facing-page parity elsewhere in the document for
    continuation pages with no heading of their own -- see the per-parity
    tracking in make_written_fields_labelled)."""
    events = []
    words = page.get_text("words")
    height = page.rect.height
    for index, word in enumerate(words[:-1]):
        text = word[4].strip()
        x0 = word[0]
        if text.lower().rstrip(".:()") == "question" and _is_real_question_heading(words, index):
            nxt = words[index + 1][4].strip(".:()")
            events.append((word[1] / height, "question", int(nxt)))
            continue
        if margin_x0 is None:
            continue
        m = _LETTER_RE.match(text)
        if m and abs(x0 - margin_x0) <= 3:
            events.append((word[1] / height, "letter", m.group(1)))
            continue
        m = _ROMAN_RE.match(text)
        if m and 15 <= (x0 - margin_x0) <= 45:
            events.append((word[1] / height, "roman", m.group(1).lower()))
    return events


def make_written_fields_labelled(doc, section_b_first, section_b_last, id_prefix="B"):
    """Text-layer equivalent of make_written_fields that labels each ruled
    answer-line group with the actual VCAA subpart id (B1a, B1b, B11ci, ...)
    it belongs to, instead of a flat sequential counter (B1, B2, B3...).
    This matters because the examination report's own answer records are
    keyed by these same subpart ids (built from the report's "Question 11c.i"
    style headings) -- a flat sequential id can never be joined to its
    official answer.

    Method: on each page, merge three independently-detected signals into
    one top-to-bottom event stream: "Question N" headings, subpart letter
    labels "a."-"h." at the page's left content margin, and nested roman-
    numeral labels "i.", "ii." indented further right than the letters. Each
    detected ruled-line answer group is then labelled with whichever
    (question, letter, roman) label most recently preceded it. A question
    with no subpart letter at all keeps the letter/roman slots empty, giving
    id "B9" -- matching report_extraction_lib.py's own heading_to_
    interaction_id("Question 9") -> "B9". First hand-verified end to end
    against 2025 (49/49 exact match against that year's report ids -- see
    the now-retired scripts/build_2025_section_b.py this generalises from)
    before becoming the shared default for every text-layer paper.

    Callers should still individually verify each paper against its own
    report once extracted -- annotate-the-figure questions and narrow
    bordered-box answers (neither wide enough to trigger the ruled-line
    detector) have no line group to label at all and need a per-paper
    MANUAL_ENTRIES fallback, the same as 2025's and 2024's own scripts."""
    from collections import Counter

    x0_samples = {0: [], 1: []}
    for page_number in range(section_b_first, section_b_last + 1):
        x0 = _section_b_heading_x0(doc[page_number - 1])
        if x0 is not None:
            x0_samples[page_number % 2].append(round(x0, 1))
    margin_x0_by_parity = {
        parity: (Counter(samples).most_common(1)[0][0] if samples else None)
        for parity, samples in x0_samples.items()
    }

    items = []
    seen_ids = {}
    current_question = None
    current_letter = None
    current_roman = None

    for page_number in range(section_b_first, section_b_last + 1):
        page = doc[page_number - 1]
        margin_x0 = margin_x0_by_parity[page_number % 2]
        text = page_text(page)
        if _is_skippable_section_b_page(text):
            continue

        events = _section_b_label_events(page, margin_x0)

        rows = answer_line_rows(page)
        from_raster = False
        if not rows:
            rows = raster_answer_line_rows(page)
            from_raster = True
        if page_number == section_b_first:
            # Only this page carries the Instructions block above Question 1
            # -- see make_written_fields for why this must not apply to
            # every page.
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
                if current_question is None:
                    continue  # a ruled line before any question heading was ever seen -- skip
                interaction_id = f"{id_prefix}{current_question}{current_letter or ''}{current_roman or ''}"
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

                response_type = "drawing" if re.search(r"\bdraw|diagram|graph|sketch\b", text, re.I) else "text"
                items.append(
                    {
                        "id": interaction_id,
                        "section": "B",
                        "question": interaction_id[1:],
                        "page": page_number,
                        "type": response_type,
                        "rect": rect,
                        "note": "Auto-placed from ruled-line geometry, labelled by detected subpart; verify visually.",
                    }
                )
    return items


def parse_duration_minutes(text):
    """Extracts (readingMinutes, writingMinutes) from cover-page prose like
    'Reading time: ... (15 minutes)' / 'Writing time: ... (2 hours 30
    minutes)' or 'Writing time is 2 hours 30 minutes'. Returns (None, None)
    if not found (e.g. no text layer)."""
    reading = None
    writing = None
    reading_match = re.search(r"Reading time[^(]*\((\d+)\s*minutes?\)", text, re.I)
    if reading_match:
        reading = int(reading_match.group(1))
    else:
        reading_match2 = re.search(r"Reading time is\s*(\d+)\s*minutes?", text, re.I)
        if reading_match2:
            reading = int(reading_match2.group(1))

    writing_match = re.search(r"Writing time[^(]*\((?:(\d+)\s*hours?\s*)?(\d+)?\s*minutes?\)", text, re.I)
    if writing_match:
        hours = int(writing_match.group(1) or 0)
        mins = int(writing_match.group(2) or 0)
        writing = hours * 60 + mins
    else:
        writing_match2 = re.search(r"Writing time is\s*(?:(\d+)\s*hours?\s*)?(\d+)?\s*minutes?", text, re.I)
        if writing_match2 and (writing_match2.group(1) or writing_match2.group(2)):
            hours = int(writing_match2.group(1) or 0)
            mins = int(writing_match2.group(2) or 0)
            writing = hours * 60 + mins

    return reading, writing


def find_formula_sheet_range(doc):
    """Returns (start_page_1indexed, end_page_1indexed) for the embedded
    formula sheet, or None if not detected via text search (e.g. no text
    layer -- caller applies a positional fallback)."""
    for page_index in range(doc.page_count - 1, max(-1, doc.page_count - 12), -1):
        text = page_text(doc[page_index])
        if re.search(r"formula\s*sheet", text, re.I):
            start = page_index
            # Walk backward while the previous page is still part of the
            # formula sheet block (its own title/cover page).
            while start > 0 and re.search(r"formula\s*sheet|victorian certificate", page_text(doc[start - 1]), re.I):
                start -= 1
            return start + 1, doc.page_count
    return None


def extract_formula_sheet(doc, source_path, slug, era):
    result = find_formula_sheet_range(doc)
    if result is None:
        # No text layer (e.g. 2024) -- current/previous-design papers are
        # consistently 52 (current) or ~49 (previous) pages with the formula
        # sheet as the last 4 pages (confirmed against 2025's detected
        # boundary of pages 49-52 of 52, and 2023's of 45-48 of 49). Fall
        # back to "last 4 pages" with a note for manual confirmation.
        if doc.page_count >= 4:
            result = (doc.page_count - 3, doc.page_count)
        else:
            return None, "not-detected"

    start, end = result
    sheet = fitz.open()
    sheet.insert_pdf(doc, from_page=start - 1, to_page=end - 1)
    out_path = FORMULA_DIR / f"{slug}.pdf"
    sheet.save(out_path)
    sheet.close()
    source_note = "detected" if find_formula_sheet_range(doc) else "positional-fallback (no text layer)"
    return f"/formula-sheets/{slug}.pdf", source_note


def main():
    PAPERS_DIR.mkdir(parents=True, exist_ok=True)
    INTERACTIONS_DIR.mkdir(parents=True, exist_ok=True)
    FORMULA_DIR.mkdir(parents=True, exist_ok=True)

    papers = []
    for source, era in find_exam_pdfs():
        slug = slug_for(source)
        title = title_for(source, era)
        public_pdf = PAPERS_DIR / f"{slug}.pdf"
        shutil.copy2(source, public_pdf)
        doc = fitz.open(source)

        has_mcq = era != "archive"
        section_a_total = 20 if has_mcq else 0

        cover_text = " ".join(page_text(doc[i]) for i in range(min(2, doc.page_count)))
        detected_reading, detected_writing = parse_duration_minutes(cover_text)

        is_dual = "exam1" in source.stem.lower() or "exam2" in source.stem.lower()
        if era in ERA_DURATIONS:
            default_reading, default_writing, total_marks = ERA_DURATIONS[era]
        elif is_dual:
            default_reading, default_writing, total_marks = ARCHIVE_DUAL
        else:
            default_reading, default_writing, total_marks = ARCHIVE_SINGLE

        reading_minutes = detected_reading or default_reading
        writing_minutes = detected_writing or default_writing
        duration_source = "detected" if (detected_reading and detected_writing) else f"assumed-standard for {era} era"

        section_b_start = detect_section_b_start(doc, has_mcq, section_a_total)

        tuned_path = ROOT / "data" / f"{slug}-interactions.json"
        if slug in TUNED_INTERACTIONS and tuned_path.exists():
            interactions = json.loads(tuned_path.read_text(encoding="utf-8-sig"))
        else:
            mcqs = make_mcqs(doc, section_a_total, section_b_start or (doc.page_count + 1), slug) if has_mcq else []
            has_text_layer = bool(doc[0].get_fonts())
            if has_text_layer:
                # Prefer subpart-labelled ids (B1a, B1b, ...) over a flat
                # sequential counter whenever there's a text layer to read
                # "Question N"/"a."/"b." labels from -- report data (once
                # extracted for a paper) is keyed by those same subpart ids,
                # so a flat B1/B2/B3 counter can never be joined to its
                # official answer. See make_written_fields_labelled's
                # docstring.
                formula_range = find_formula_sheet_range(doc)
                section_b_last = (formula_range[0] - 1) if formula_range else doc.page_count
                written = make_written_fields_labelled(doc, section_b_start or 1, section_b_last)
            else:
                written = make_written_fields(doc, section_b_start or 1)
            interactions = mcqs + written

        interaction_file = INTERACTIONS_DIR / f"{slug}.json"
        interaction_file.write_text(json.dumps(interactions, indent=2), encoding="utf-8")

        formula_sheet_url, formula_source = extract_formula_sheet(doc, source, slug, era)

        # hasAnswerData/hasCurriculumMap are derived from whether the
        # per-year extraction/mapping pipeline has actually produced data
        # for this paper (data/answers/<slug>.json, data/curriculum/<slug>-
        # mapping.json) -- never hand-toggled, so they can't drift out of
        # sync with what's really been extracted (a hand-edited public/
        # papers.json would just get overwritten the next time this script
        # runs anyway). The static-content JSON itself is copied from data/
        # (the source of truth, reviewed alongside its extraction script)
        # into public/ (what the running app actually fetches) every run,
        # so the two can never silently drift apart the way a manual copy
        # can.
        answers_src = ROOT / "data" / "answers" / f"{slug}.json"
        has_answer_data = answers_src.exists()
        if has_answer_data:
            (PUBLIC / "answers" / f"{slug}.json").write_text(
                answers_src.read_text(encoding="utf-8"), encoding="utf-8"
            )

        curriculum_src = ROOT / "data" / "curriculum" / f"{slug}-mapping.json"
        has_curriculum_map = curriculum_src.exists()
        if has_curriculum_map:
            (PUBLIC / "curriculum" / f"{slug}-mapping.json").write_text(
                curriculum_src.read_text(encoding="utf-8"), encoding="utf-8"
            )
        stimulus_src = ROOT / "data" / "curriculum" / f"{slug}-shared-stimulus.json"
        if stimulus_src.exists():
            (PUBLIC / "curriculum" / f"{slug}-shared-stimulus.json").write_text(
                stimulus_src.read_text(encoding="utf-8"), encoding="utf-8"
            )

        papers.append(
            {
                "id": slug,
                "title": title,
                "era": era,
                "pdfUrl": f"/papers/{slug}.pdf",
                "interactionsUrl": f"/interactions/{slug}.json",
                "formulaSheetUrl": formula_sheet_url,
                "storageKey": f"vce-physics-{slug}-attempt",
                "sectionATotal": section_a_total,
                "totalMarks": total_marks,
                "source": str(source.relative_to(ROOT)).replace("\\", "/"),
                "pageCount": doc.page_count,
                "interactionCount": len(interactions),
                "readingMinutes": reading_minutes,
                "writingMinutes": writing_minutes,
                "durationSource": duration_source,
                "hasAnswerData": has_answer_data,
                "hasCurriculumMap": has_curriculum_map,
                "hasMultipleChoice": has_mcq,
            }
        )
        print(f"{slug}: {title} ({era}) -- {len(interactions)} interactions, formula sheet: {formula_source}")

    (PUBLIC / "papers.json").write_text(json.dumps(papers, indent=2), encoding="utf-8")
    print(f"\nGenerated {len(papers)} papers")


if __name__ == "__main__":
    main()
