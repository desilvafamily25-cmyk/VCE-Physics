"""Deterministic extraction from VCAA examination reports published as PDF
(2017-2019's VCE Physics reports; every year from 2020 onward switched to
docx, handled instead by report_extraction_lib.py). Mirrors that module's
overall shape and output contract (same curated answer-record schema) but
every low-level technique is different, because a PDF report exposes no
document object model at all -- everything here is reconstructed from raw
page geometry: word positions (page.get_text("words")) and vector drawings
(page.get_drawings()), the same primitives generate_paper_assets.py already
uses to find ruled answer lines on the exam PDFs themselves.

Two structural discoveries this module is built around, both confirmed by
direct inspection of 2019's report (see docs/DATA-ARCHITECTURE.md):

1. Section A's correct-answer column is not a text column at all -- VCAA
   shades the correct percentage cell with a light grey fill instead
   (confirmed RGB (0.827, 0.827, 0.827), consistently, across every page of
   every year inspected). There is no "Correct answer" text anywhere on the
   page; the answer must be read off which of the four %A-%D cells in a row
   has that fill.
2. Section B has no tables in the Word sense either -- each subquestion's
   marks-distribution table ("Marks | 0 | 1 | 2 | Average") is a grid of
   thin ruled lines (the same vector line primitives generate_paper_assets.
   answer_line_rows already parses for exam PDFs) with plain text laid on
   top, not an embedded OOXML table structure.
"""
import re
from pathlib import Path

import fitz

_GREY_FILL = (0.827, 0.827, 0.827)
_LETTERS = ("A", "B", "C", "D")


def _is_grey(fill, tol=0.03):
    return fill is not None and all(abs(fill[i] - _GREY_FILL[i]) < tol for i in range(3))


def find_column_headers(page):
    """Finds the 'A B C D' header row of a Section A results table on this
    page: four single-letter words at the same y, evenly spaced ~28pt
    apart (confirmed stable across every page of 2019's report). Returns
    ({"A": x, "B": x, "C": x, "D": x}, y) or (None, None) if this page has
    no such header (e.g. a page with no Section A content, or a stray
    single "A"/"B" elsewhere in body text that doesn't come as a genuine
    set of four)."""
    words = page.get_text("words")
    by_y = {}
    for w in words:
        if w[4] in _LETTERS:
            by_y.setdefault(round(w[1], 1), []).append(w)
    for y, ws in by_y.items():
        found = {w[4]: w[0] for w in ws}
        if set(found) != set(_LETTERS):
            continue
        xs = [found[letter] for letter in _LETTERS]
        gaps = [xs[i + 1] - xs[i] for i in range(3)]
        if all(20 < g < 40 for g in gaps):
            return found, y
    return None, None


def shaded_cells(page):
    """Returns the rects of every light-grey-filled drawing on this page --
    Section A's correct-answer markers are the only thing this fill colour
    is ever used for, confirmed across every report page inspected."""
    return [d["rect"] for d in page.get_drawings() if _is_grey(d.get("fill"))]


def _nearest_letter(x, col_x):
    return min(col_x, key=lambda letter: abs(col_x[letter] - x))


def question_number_rows(page, col_x, header_y):
    """Returns [(question_number, y0)] for each Section A table row on this
    page, found from the leftmost ('Question') column's digit words below
    the header row. Cross-validated against the presence of numeric words
    at all four %A-%D column positions on the same row (within 1pt) to
    reject stray digits elsewhere on the page (e.g. a percentage or a year
    number in unrelated body text) rather than trusting an isolated digit
    in the left margin alone."""
    words = page.get_text("words")
    candidates = []
    for w in words:
        text = w[4].strip().rstrip(".")
        if w[0] < 100 and w[1] > header_y + 1 and text.isdigit():
            candidates.append((int(text), w[1]))

    rows = []
    for qnum, y0 in candidates:
        matches = 0
        for letter in _LETTERS:
            col = col_x[letter]
            if any(col - 12 <= w[0] <= col + 5 and abs(w[1] - y0) < 1.5 for w in words):
                matches += 1
        if matches >= 3:  # allow one column to be a blank/dash on rare rows
            rows.append((qnum, y0))
    rows.sort(key=lambda r: r[1])
    return rows


def _row_bottom(rows, index, page_height):
    """The y0 of the next row, or the page's own footer boundary for the
    last row on a page -- used as the bottom edge when collecting a row's
    percentage values and comment text/images."""
    if index + 1 < len(rows):
        return rows[index + 1][1] - 2
    return page_height - 60  # VCAA's own footer ("© VCAA  Page N") sits here


def extract_section_a_table_pdf(doc, section_a_page_range):
    """PDF equivalent of report_extraction_lib.extract_section_a_table,
    returning the same normalised shape: a list of
    [Question, Correct answer, % A, % B, % C, % D, Comments] rows (header
    row first), so build_section_a_answers (already shared with the docx
    path) can consume it unmodified.

    `section_a_page_range` is (first_page, last_page), 1-indexed inclusive
    -- the caller finds this once (see extract_2019_report.py) by locating
    "Section A" / "Section B" headings in the report's own text.
    """
    rows = [["Question", "Correct answer", "% A", "% B", "% C", "% D", "Comments"]]
    first, last = section_a_page_range
    for page_number in range(first, last + 1):
        page = doc[page_number - 1]
        col_x, header_y = find_column_headers(page)
        if col_x is None:
            continue
        q_rows = question_number_rows(page, col_x, header_y)
        grey = shaded_cells(page)
        words = page.get_text("words")

        for index, (qnum, y0) in enumerate(q_rows):
            bottom = _row_bottom(q_rows, index, page.rect.height)
            percents = {}
            for letter in _LETTERS:
                col = col_x[letter]
                match = next((w for w in words if col - 12 <= w[0] <= col + 5 and abs(w[1] - y0) < 1.5), None)
                percents[letter] = match[4].strip() if match else ""

            correct = ""
            for rect in grey:
                if y0 - 2 <= rect.y0 <= y0 + 14:
                    letter = _nearest_letter((rect.x0 + rect.x1) / 2, col_x)
                    correct += letter

            comment_x0 = col_x["D"] + 20
            comment_words = [
                w for w in words
                if w[0] >= comment_x0 and y0 - 2 <= w[1] < bottom
            ]
            comment_words.sort(key=lambda w: (round(w[1], 1), w[0]))
            comment = _words_to_text(comment_words)

            rows.append([str(qnum), correct, percents["A"], percents["B"], percents["C"], percents["D"], comment])
    return rows


def _words_to_text(words):
    """Joins word tuples back into readable text, inserting a newline
    whenever a word's y jumps to a new line rather than continuing the
    same one (a plain space-join would run every line of a multi-line
    comment together)."""
    if not words:
        return ""
    lines = []
    current_y = round(words[0][1], 1)
    current = []
    for w in words:
        y = round(w[1], 1)
        if abs(y - current_y) > 2:
            lines.append(" ".join(current))
            current = []
            current_y = y
        current.append(w[4])
    if current:
        lines.append(" ".join(current))
    return "\n".join(lines).strip()


_QUESTION_HEADING_RE = re.compile(r"^Question\s+(\d+)([a-h])?\.?([ivx]+)?\.?\s*$", re.I)


_SECTION_B_HEADING_RE = re.compile(r"(?:^|\n)\s*Section B\s*\n", re.I)


def find_section_b_start_page(doc):
    """First page whose text contains a standalone 'Section B' heading line
    (VCAA prints a trailing space after it before the line break on at
    least one year's report -- confirmed on 2019's -- so this matches on
    the line's content with surrounding whitespace stripped, not an exact
    "\\nSection B\\n" substring)."""
    for page_number in range(1, doc.page_count + 1):
        text = doc[page_number - 1].get_text("text")
        if _SECTION_B_HEADING_RE.search(text):
            return page_number
    return None


def find_marks_table(page, y_from):
    """Finds the next 'Marks | 0 | 1 | ... | Average' ruled-line table at
    or below `y_from` on this page. Returns (max_marks, distribution_pct,
    average, table_bottom_y) or None if no such table exists below y_from
    on this page (the subquestion's table may be on the next page instead,
    e.g. when the heading falls at the very bottom of a page).

    The table is a grid of thin ruled lines with plain text on top (see
    module docstring) -- located here by its own literal "Marks" / "%"
    row-label text rather than by reconstructing the ruled-line grid,
    since the text labels are simpler to anchor on and just as reliable.

    page.get_text("words") is NOT guaranteed sorted by y -- confirmed
    directly (a page with three "Marks" labels returned them in the order
    605pt, 212pt, 432pt, not top-to-bottom) -- so every candidate search
    below picks the *smallest* qualifying y via sorting, not simply the
    first hit in extraction order; taking the first hit silently matched
    a "Marks" label belonging to a *later* subquestion's table on three
    separate subquestions during development, each one then reporting an
    empty distribution for itself while duplicating a table far below."""
    words = page.get_text("words")
    marks_candidates = sorted((w for w in words if w[4] == "Marks" and w[1] >= y_from - 2), key=lambda w: w[1])
    marks_word = marks_candidates[0] if marks_candidates else None
    if marks_word is None:
        return None
    row_y = round(marks_word[1], 1)
    pct_candidates = sorted(
        (w for w in words if w[4] == "%" and w[1] > row_y + 10), key=lambda w: w[1]
    )
    pct_word = pct_candidates[0] if pct_candidates else None
    if pct_word is None:
        return None
    pct_y = round(pct_word[1], 1)

    header_cols = [w for w in words if abs(w[1] - row_y) < 1.5 and w[0] > marks_word[0]]
    header_cols.sort(key=lambda w: w[0])

    # The data row's own baseline sits a few points below the "%" label's
    # (confirmed directly: a "%" at y=625.0 with its own row's data at
    # y=628.4, a 3.4pt gap) -- rather than guess a single fixed tolerance,
    # widened enough to cover that jitter but still short of the ~20pt gap
    # to the next table, which is comfortably far by comparison.
    distribution = {}
    average = None
    for w in header_cols:
        label = w[4].strip()
        if label.lower() == "average":
            avg_word = next((w2 for w2 in words if pct_y - 1 <= w2[1] <= pct_y + 6 and w2[0] > w[0] - 5), None)
            if avg_word:
                try:
                    average = float(avg_word[4].strip())
                except ValueError:
                    pass
            continue
        if not label.isdigit():
            continue
        mark_value = label
        pct_val = next((w2 for w2 in words if pct_y - 1 <= w2[1] <= pct_y + 6 and abs(w2[0] - w[0]) < 8), None)
        if pct_val:
            try:
                distribution[mark_value] = float(pct_val[4].strip())
            except ValueError:
                pass

    max_marks = max((int(k) for k in distribution if k.isdigit()), default=0)
    table_bottom = pct_y + 14
    return max_marks, distribution, average, table_bottom


def extract_section_b_questions_pdf(doc, section_b_page_range, image_out_dir, image_url_prefix, year):
    """PDF equivalent of report_extraction_lib.extract_section_b_questions.
    Walks every page in `section_b_page_range` (1-indexed inclusive) for
    'Question N[letter][roman].' headings, and for each one collects its
    marks-distribution table (find_marks_table) and the comment content
    between that heading and the next one -- as plain text plus a single
    cropped-page-region image for any embedded diagram (PDF reports draw
    diagrams as native vector content directly on the page, not as an
    embeddable object the way a docx OLE equation is, so the fix here is
    to rasterise the region rather than parse it -- the comment text itself
    still round-trips character-for-character since it's real text, only
    the diagram becomes an image).

    Returns [{"heading", "interactionId", "marksTable", "spans"}], one per
    subquestion, in document order -- the same shape
    report_extraction_lib.extract_section_b_questions returns, so
    build_section_b_answers (shared with the docx path) can consume it
    unmodified.
    """
    from metafile_convert import Image  # noqa: F401  (Pillow, already a dependency)

    image_out_dir = Path(image_out_dir)
    image_out_dir.mkdir(parents=True, exist_ok=True)
    image_counter = 0

    first, last = section_b_page_range
    headings = []  # (page_number, y0, question_num, letter, roman)
    for page_number in range(first, last + 1):
        page = doc[page_number - 1]
        text = page.get_text("text")
        if re.search(r"END OF (QUESTION|SECTION)|FORMULA SHEET", text, re.I):
            continue
        for block in page.get_text("blocks"):
            block_text = block[4].strip()
            m = _QUESTION_HEADING_RE.match(block_text)
            if m:
                headings.append((page_number, block[1], int(m.group(1)), (m.group(2) or "").lower(), (m.group(3) or "").lower()))

    questions = []
    for index, (page_number, y0, qnum, letter, roman) in enumerate(headings):
        next_page, next_y0 = (headings[index + 1][0], headings[index + 1][1]) if index + 1 < len(headings) else (last + 1, 0)

        page = doc[page_number - 1]
        marks_result = find_marks_table(page, y0)
        table_bottom = marks_result[3] if marks_result else y0 + 10

        # Collect comment text (and one cropped image, if this subquestion's
        # content includes a non-text diagram) from just below the marks
        # table to the next heading, possibly spanning onto later pages.
        spans = []
        scan_page_number = page_number
        scan_y = table_bottom
        while scan_page_number <= last:
            scan_page = doc[scan_page_number - 1]
            end_y = next_y0 if scan_page_number == next_page else scan_page.rect.height - 55
            words = [w for w in scan_page.get_text("words") if scan_y - 1 <= w[1] < end_y]
            if words:
                spans.append({"kind": "paragraph", "level": 0, "spans": [{"text": _words_to_text(words)}]})

            art_bbox = _vector_art_bbox(scan_page, scan_y, end_y)
            if art_bbox is not None:
                image_counter += 1
                img_path = image_out_dir / f"{year}-b{image_counter}.png"
                clip = fitz.Rect(
                    max(0, art_bbox.x0 - 6), max(0, art_bbox.y0 - 6),
                    min(scan_page.rect.width, art_bbox.x1 + 6), min(scan_page.rect.height, art_bbox.y1 + 6),
                )
                pix = scan_page.get_pixmap(dpi=200, clip=clip)
                pix.save(str(img_path))
                spans.append({
                    "kind": "paragraph", "level": 0,
                    "spans": [{"imageUrl": f"{image_url_prefix}/{img_path.name}", "width": pix.width, "height": pix.height}],
                })

            if scan_page_number == next_page:
                break
            scan_page_number += 1
            scan_y = 60

        interaction_id = f"B{qnum}{letter}{roman}"
        max_marks, distribution, average, _ = marks_result or (0, {}, None, None)
        questions.append({
            "heading": f"Question {qnum}{letter}{roman}.".rstrip("."),
            "interactionId": interaction_id,
            "marksTable": {"maxMarks": max_marks, "distributionPct": distribution, "average": average} if marks_result else None,
            "items": spans,
        })
    return questions


def _vector_art_bbox(page, y0, y1, min_segments=8):
    """Returns the tight union bounding box of this page region's diagram
    content, or None if there is none. VCAA's Section B report diagrams
    (force arrows, circuit schematics, energy-level figures) are embedded
    raster images (page.get_image_info()), confirmed directly -- not
    vector line art the way generate_paper_assets.py's exam-PDF ruled-line
    detection expects, despite the superficially similar name this
    function kept from an earlier vector-based attempt. Falls back to a
    genuine vector-drawing bbox (dozens of line/curve segments, unlike a
    stray single-segment ruled divider) only if no embedded image is found,
    in case a future year's report draws a diagram natively instead."""
    bbox = None
    for info in page.get_image_info():
        bx0, by0, bx1, by1 = info["bbox"]
        if y0 - 5 <= by0 and by1 <= y1 + 5:
            r = fitz.Rect(bx0, by0, bx1, by1)
            bbox = r if bbox is None else bbox | r
    if bbox is not None:
        return bbox

    segments = 0
    for d in page.get_drawings():
        r = d.get("rect")
        if r is None or not (y0 - 5 <= r.y0 and r.y1 <= y1 + 5):
            continue
        if r.width < 2 and r.height < 2:
            continue  # a thin ruled line/divider, not diagram content
        segments += len(d.get("items", [])) or 1
        bbox = r if bbox is None else bbox | r
    if segments < min_segments:
        return None
    return bbox
