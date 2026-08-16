"""Shared, style-name-robust helpers for extracting VCE Physics examination
report data from .docx files across different years' VCAA templates.

Different years use different Word style names for the same structural role
(e.g. 2025 uses "Heading 1"/"Heading 2"/"Bullet"; 2024 may use "VCAA Heading
1"/"VCAA Heading 2"/"VCAA Heading 3"/"VCAA bullet", mirroring what was
observed in VCE Chemistry's reports from the same VCAA template family).
Rather than hardcode a style name per year, these helpers match on substrings
("heading", "bullet") and on the actual "Question ..." text pattern, which
has been stable across every year inspected so far. Keep this file the
single source of truth for that matching logic so a template change only
needs fixing in one place.

This library is deliberately near-identical to the VCE Chemistry app's
report_extraction_lib.py (this app's architecture is modelled on it
directly) -- the VCAA report template family is shared across subjects, and
the technique (ruled-line-free docx body walking, shading/highlight-based
correct-answer detection, marks-table parsing) is subject-agnostic. Only the
subject name in a few strings differs.
"""
import re
import sys
from pathlib import Path

from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

sys.path.insert(0, str(Path(__file__).resolve().parent))
from metafile_convert import metafile_or_raster_to_png  # noqa: E402

# Namespace URIs for the two ways a paragraph run can embed an image:
# legacy OLE (Word Equation Editor/MathType -- what every equation in the
# 2025 report actually is) and modern inline pictures (w:drawing/pic:pic).
_NS_V = "urn:schemas-microsoft-com:vml"
_NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
_NS_WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
_EMU_PER_PT = 12700  # OOXML EMU units per point
_PT_TO_PX = 96 / 72  # CSS px per point, at the standard 96dpi assumption

# Matches every subquestion-heading format seen across years so far:
# "Question 1a." (letter subpart), "Question 4c.iii" (nested roman numeral,
# with or without a dot before it -- different years format this
# differently). The letter and roman parts are both optional and
# independently followed by an optional dot.
QUESTION_HEADING_RE = re.compile(r"^Question\s+\d+[a-h]?\.?[ivx]*\.?\s*$", re.I)

DIFFICULTY_BANDS = [
    (0.70, "Easy"),
    (0.40, "Medium"),
    (0.20, "Hard"),
    (0.0, "Very Hard"),
]
DIFFICULTY_RULE = (
    "Derived from official cohort performance in the examination report: for "
    "Section A, the percentage of the cohort who chose the correct option; for "
    "Section B, the average mark achieved divided by the marks available. "
    "Bands: ratio >= 0.70 Easy, 0.40-0.69 Medium, 0.20-0.39 Hard, < 0.20 Very Hard. "
    "'unknown' is used only when no official statistic exists for the question."
)

MARK_POINT_RE = re.compile(r"\bmark(?:s)? (?:was|were|could be) awarded\b", re.I)
# Different years phrase "every option counted as correct" differently: some
# reports put a literal marker like "ABCD" in the Correct-answer cell; others
# leave that cell blank and explain it in the Comments column instead. Both
# are deterministic, verbatim-sourced signals -- no physics judgement
# involved.
ALL_ACCEPTED_RE = re.compile(r"all (?:four )?options? (?:were|was|are|is) accepted", re.I)

# VCAA occasionally withdraws a Section A question after the exam (printing
# error, ambiguity, etc.) -- its report row has no correct answer and no
# percentages, just a note like "This question is no longer available." This
# is fundamentally different from "we couldn't determine the answer": there
# IS no answer, and a real student's response to it must never be marked
# wrong. Detected here so the app can exclude it from scoring entirely
# rather than lumping it into the generic "uncertain" bucket -- see
# types.ts's "withdrawn" QuestionOutcome (a first-class case from day one).
WITHDRAWN_RE = re.compile(r"no longer available|question (?:has been |was )?withdrawn|not (?:included|counted|scored)", re.I)
# Distinct from WITHDRAWN_RE: VCAA sometimes moderates a Section B
# subquestion so every student receives full marks (a fairness/scoring
# adjustment, not "this question has no correct answer") -- confirmed
# verbatim in the 2024 report ("As a result of psychometric analysis and
# review, all students were awarded full marks for this question"), which
# genuinely omits the mark value from its own text (no distribution table
# either, since there's nothing to distribute). Detected here so it's
# surfaced as a clearly-labelled, confirm-against-the-source-paper case
# rather than silently reported as a generic extraction gap.
FULL_MARKS_AWARDED_RE = re.compile(r"all students were awarded full marks", re.I)
COMMENT_RE = re.compile(
    r"\b(common error|most common|misconception|struggled|confusion|confused|"
    r"could not be (accepted|awarded)|did not|significant number|frequently|"
    r"causing issues|caused issues|issue arose|issues arose)\b",
    re.I,
)


class ImageExtractor:
    """Resolves, converts and saves every embedded equation/picture found
    while walking a report's paragraphs, so report_extraction_lib's own
    paragraph-to-spans logic never has to know about OOXML relationship
    plumbing or WMF/EMF conversion directly.

    Every image is written once (by relationship id, memoised) as a PNG
    under `out_dir`, named `<paperId>-<n>.png`, and referenced from the
    generated answers JSON by `<url_prefix>/<paperId>-<n>.png` -- see
    scripts/extract_2025_report.py for how out_dir/url_prefix are wired to
    public/answer-images/.
    """

    def __init__(self, document, out_dir, url_prefix, paper_id):
        self.document = document
        self.out_dir = out_dir
        self.url_prefix = url_prefix
        self.paper_id = paper_id
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self._counter = 0
        self._cache = {}  # r_id -> span dict

    def _next_path(self, ext):
        self._counter += 1
        name = f"{self.paper_id}-{self._counter}.png"
        return name, self.out_dir / name

    def _resolve_bytes(self, r_id):
        part = self.document.part.related_parts[r_id]
        blob = part.blob
        ext = part.partname.ext if hasattr(part.partname, "ext") else str(part.partname).rsplit(".", 1)[-1]
        return blob, ext

    def from_ole_object(self, object_el, display_pt=None):
        """`object_el` is a <w:object> element; its <v:imagedata r:id="..."/>
        points at the rendered WMF/EMF preview. `display_pt` is an optional
        (width, height) in points read from the v:shape's own style
        attribute -- Word's own intended on-page display size, which is a
        more reliable size hint than anything derivable from the raw
        metafile bounding box (that box already gets a comfortable margin
        added at raster time, deliberately not 1:1 with the display size)."""
        imagedata = object_el.find(f".//{{{_NS_V}}}imagedata")
        if imagedata is None:
            return None
        r_id = imagedata.get(f"{{{_NS_R}}}id")
        if not r_id:
            return None
        if r_id in self._cache:
            return dict(self._cache[r_id])

        blob, ext = self._resolve_bytes(r_id)
        name, path = self._next_path("png")
        px_w, px_h = metafile_or_raster_to_png(blob, ext, str(path))

        if display_pt:
            width, height = round(display_pt[0] * _PT_TO_PX), round(display_pt[1] * _PT_TO_PX)
        else:
            width, height = round(px_w / 3), round(px_h / 3)

        span = {"imageUrl": f"{self.url_prefix}/{name}", "width": width, "height": height}
        self._cache[r_id] = span
        return dict(span)

    def from_drawing(self, drawing_el):
        """`drawing_el` is a <w:drawing> element (modern inline picture);
        <a:blip r:embed="..."/> points at the actual image part directly
        (no OLE indirection), and <wp:extent cx cy> (EMU) gives display size."""
        blip = drawing_el.find(f".//{{{_NS_A}}}blip")
        if blip is None:
            return None
        r_id = blip.get(f"{{{_NS_R}}}embed")
        if not r_id:
            return None
        if r_id in self._cache:
            return dict(self._cache[r_id])

        blob, ext = self._resolve_bytes(r_id)
        name, path = self._next_path("png")
        px_w, px_h = metafile_or_raster_to_png(blob, ext, str(path))

        extent = drawing_el.find(f".//{{{_NS_WP}}}extent")
        if extent is not None:
            width = round(int(extent.get("cx")) / _EMU_PER_PT * _PT_TO_PX)
            height = round(int(extent.get("cy")) / _EMU_PER_PT * _PT_TO_PX)
        else:
            width, height = px_w, px_h

        span = {"imageUrl": f"{self.url_prefix}/{name}", "width": width, "height": height}
        self._cache[r_id] = span
        return dict(span)


def _shape_display_size_pt(object_el):
    """Reads width/height in points from a <w:object>'s <v:shape
    style="width:128pt;height:107.5pt">, if present."""
    shape = object_el.find(f".//{{{_NS_V}}}shape")
    if shape is None:
        return None
    style = shape.get("style") or ""
    m = re.search(r"width:\s*([\d.]+)pt", style)
    n = re.search(r"height:\s*([\d.]+)pt", style)
    if not (m and n):
        return None
    return float(m.group(1)), float(n.group(1))


def _omml_wrap(text, force_parens=False):
    """Parenthesises a linearised OMML sub-expression when leaving it bare
    would be ambiguous once flattened to plain text -- e.g. a superscript of
    "-2" must render as "^(-2)" (matching how everyone actually writes this
    in plain text/calculators), not "^-2" which reads as "^ minus 2" applied
    to whatever follows. Single alphanumeric tokens are left bare (`x^2`,
    not `x^(2)`) since that's how physics working is normally written."""
    if force_parens or not re.fullmatch(r"[A-Za-z0-9]+", text):
        return f"({text})"
    return text


def _omml_to_text(el):
    """Linearises a OMML (Office Math Markup Language) element tree to a
    plain-text approximation ("a=6.0x10^-2 m s^-2", "sqrt(-1.8/4.905)") --
    used for the VCE Physics reports that embed equations as native Word
    math zones rather than Equation Editor OLE objects/images (confirmed:
    2024's report uses m:oMath exclusively, 0 OLE objects; 2025's uses OLE
    objects exclusively, 0 m:oMath -- different Office versions/authors
    apparently produce different embeddings for the same VCAA report
    template, so both extraction paths are needed).

    Handles the constructs actually observed in these reports (fractions,
    super/subscripts, radicals, delimiters, n-ary operators, functions);
    anything unrecognised falls back to concatenating all descendant m:t
    text nodes in document order, so no content is ever silently dropped
    even if the formatting isn't perfectly reconstructed.
    """
    tag = el.tag.split("}")[-1]

    if tag == "t":
        return el.text or ""

    if tag == "f":
        num = el.find(qn("m:num"))
        den = el.find(qn("m:den"))
        num_text = _omml_to_text(num) if num is not None else ""
        den_text = _omml_to_text(den) if den is not None else ""
        return f"({num_text})/({den_text})"

    if tag in ("sSup", "sSub", "sSubSup"):
        base = el.find(qn("m:e"))
        base_text = _omml_to_text(base) if base is not None else ""
        out = base_text
        sub = el.find(qn("m:sub"))
        if sub is not None:
            out += f"_{_omml_wrap(_omml_to_text(sub))}"
        sup = el.find(qn("m:sup"))
        if sup is not None:
            out += f"^{_omml_wrap(_omml_to_text(sup))}"
        return out

    if tag == "rad":
        base = el.find(qn("m:e"))
        base_text = _omml_to_text(base) if base is not None else ""
        deg = el.find(qn("m:deg"))
        deg_text = _omml_to_text(deg) if deg is not None else ""
        return f"root({deg_text}, {base_text})" if deg_text.strip() else f"sqrt({base_text})"

    if tag == "d":
        # Delimiter (parentheses/brackets/braces around one or more m:e
        # sub-expressions, e.g. "(x + y)"). Falls back to plain parens if
        # the source didn't specify custom delimiter characters.
        d_pr = el.find(qn("m:dPr"))
        beg = "("
        end = ")"
        if d_pr is not None:
            beg_el = d_pr.find(qn("m:begChr"))
            end_el = d_pr.find(qn("m:endChr"))
            if beg_el is not None and beg_el.get(qn("m:val")):
                beg = beg_el.get(qn("m:val"))
            if end_el is not None and end_el.get(qn("m:val")):
                end = end_el.get(qn("m:val"))
        parts = [_omml_to_text(e) for e in el.findall(qn("m:e"))]
        return f"{beg}{', '.join(parts)}{end}"

    if tag == "func":
        name_el = el.find(qn("m:fName"))
        arg_el = el.find(qn("m:e"))
        name_text = _omml_to_text(name_el) if name_el is not None else ""
        arg_text = _omml_to_text(arg_el) if arg_el is not None else ""
        return f"{name_text}({arg_text})"

    if tag == "nary":
        # Sum/product/integral: symbol + subscript (lower limit) + superscript
        # (upper limit) + the summand/integrand expression.
        nary_pr = el.find(qn("m:naryPr"))
        chr_el = nary_pr.find(qn("m:chr")) if nary_pr is not None else None
        symbol = chr_el.get(qn("m:val")) if chr_el is not None and chr_el.get(qn("m:val")) else "∑"
        sub = el.find(qn("m:sub"))
        sup = el.find(qn("m:sup"))
        base = el.find(qn("m:e"))
        out = symbol
        if sub is not None:
            out += f"_{_omml_wrap(_omml_to_text(sub))}"
        if sup is not None:
            out += f"^{_omml_wrap(_omml_to_text(sup))}"
        if base is not None:
            out += _omml_to_text(base)
        return out

    if tag in ("acc", "bar", "box", "borderBox", "groupChr"):
        # Accent/overline/box decorations -- the decoration itself doesn't
        # linearise meaningfully to plain text, so just surface the base
        # expression it's decorating rather than dropping it.
        base = el.find(qn("m:e"))
        return _omml_to_text(base) if base is not None else "".join(_omml_to_text(c) for c in el)

    # Generic container (m:r, m:num, m:den, m:e, m:sub, m:sup, m:deg,
    # m:oMath, m:oMathPara, or anything not special-cased above): recurse
    # into every child in document order.
    return "".join(_omml_to_text(child) for child in el)


def paragraph_to_spans(paragraph, image_extractor):
    """Walks a paragraph's direct XML children (not `paragraph.runs` --
    OMML math zones are `m:oMathPara` elements that sit as paragraph-level
    siblings of `w:r` runs, not nested inside one, so run-only iteration
    would skip them entirely and silently drop every embedded equation in a
    report that uses native Word math instead of Equation Editor OLE
    objects; see _omml_to_text's docstring) in document order, returning a
    list of InlineSpan-shaped dicts (`{"text": ...}` or `{"imageUrl",
    "width", "height"}`). Consecutive text runs are merged into one span,
    so a mid-sentence equation image/OMML zone never gets wrenched out of
    its sentence -- confirmed directly against the 2025 report's own XML
    that images genuinely sit mid-sentence ("Many responses simply stated
    that [equation image] , that force would ..."). An image_extractor of
    None degrades to text-only (every image silently skipped, OMML still
    converted to text) for callers without the document/paper context
    needed to resolve embedded images.
    """
    spans = []
    text_buffer = []

    def flush_text():
        if text_buffer:
            joined = "".join(text_buffer)
            if joined:
                spans.append({"text": joined})
            text_buffer.clear()

    for child in paragraph._p.iterchildren():
        child_tag = child.tag.split("}")[-1]

        if child_tag == "oMathPara" or child_tag == "oMath":
            text_buffer.append(_omml_to_text(child))
            continue

        if child_tag != "r":
            continue  # paragraph-level metadata (pPr, bookmarks, etc.) -- not content

        if image_extractor is not None:
            object_el = child.find(qn("w:object"))
            if object_el is not None:
                flush_text()
                span = image_extractor.from_ole_object(object_el, _shape_display_size_pt(object_el))
                if span:
                    spans.append(span)
                continue
            drawing_el = child.find(qn("w:drawing"))
            if drawing_el is not None and drawing_el.find(f".//{{{_NS_A}}}blip") is not None:
                flush_text()
                span = image_extractor.from_drawing(drawing_el)
                if span:
                    spans.append(span)
                continue

        run_text = "".join(t.text or "" for t in child.findall(f".//{qn('w:t')}"))
        if run_text:
            text_buffer.append(run_text)

    flush_text()
    return spans


def spans_text(spans):
    """Flattens spans back to plain text (images become a bracketed marker)
    -- used only for regex classification (classify_paragraph) and the
    plain-text uncertainReason/officialExplanation fallback fields, never
    for the primary rendered content."""
    return "".join(s["text"] if "text" in s else "[equation]" for s in spans)


def style_name(paragraph: Paragraph) -> str:
    return (paragraph.style.name or "") if paragraph.style else ""


def is_heading(paragraph: Paragraph) -> bool:
    return "heading" in style_name(paragraph).lower()


def is_question_heading(paragraph: Paragraph) -> bool:
    return is_heading(paragraph) and bool(QUESTION_HEADING_RE.match(paragraph.text.strip()))


def bullet_level(paragraph: Paragraph) -> int:
    name = style_name(paragraph).lower()
    if "level 2" in name or "level2" in name:
        return 2
    if "bullet" in name or "list" in name:
        return 1
    return 0


def heading_to_interaction_id(heading: str) -> str:
    """'Question 1a.' -> 'B1a'; 'Question 4c.iii' -> 'B4ciii'; handles both
    dotted and undotted roman-numeral subpart forms."""
    label = heading.replace("Question", "").strip().rstrip(".")
    label = label.replace(".", "")
    return f"B{label}"


def walk_body(document):
    """Yield ('para', Paragraph) / ('table', Table) in true document order."""
    body = document.element.body
    for child in body.iterchildren():
        if child.tag.endswith("}p"):
            yield "para", Paragraph(child, document)
        elif child.tag.endswith("}tbl"):
            yield "table", Table(child, document)


def table_to_rows(table: Table):
    return [[cell.text.strip() for cell in row.cells] for row in table.rows]


def parse_marks_table(rows):
    """Rows like [['Marks','0','1','2','Average'], ['%','9','48','42','1.4']]
    (VCE Chemistry's header) or [['Mark','0','1','2','Average'], [...]] (VCE
    Physics uses the singular "Mark" -- confirmed against the 2025 report;
    accept both rather than assuming one subject's wording holds for another).
    Returns (maxMarks, distributionPct, average) or None if not a marks table.
    """
    if len(rows) < 2:
        return None
    header, pct_row = rows[0], rows[1]
    if not header or header[0].strip().lower() not in ("marks", "mark"):
        return None
    if not pct_row or pct_row[0].strip() != "%":
        return None

    mark_cols = []
    average = None
    for idx in range(1, len(header)):
        label = header[idx].strip()
        if not label:
            continue
        if label.lower() == "average":
            try:
                average = float(pct_row[idx])
            except (ValueError, IndexError):
                average = None
            continue
        if label.isdigit():
            mark_cols.append((idx, int(label)))

    if not mark_cols:
        return None

    distribution = {}
    for idx, mark_value in mark_cols:
        try:
            distribution[str(mark_value)] = float(pct_row[idx])
        except (ValueError, IndexError):
            continue

    max_marks = max(v for _, v in mark_cols)
    return {"maxMarks": max_marks, "distributionPct": distribution, "average": average}


def classify_paragraph(text: str) -> str:
    if MARK_POINT_RE.search(text):
        return "markingPoint"
    if COMMENT_RE.search(text):
        return "examinerComment"
    return "note"


def difficulty_from_ratio(ratio, source_note="Examination report cohort statistics."):
    if ratio is None:
        return {
            "level": "unknown",
            "ratio": None,
            "source": "No official cohort statistic available for this question.",
            "rule": DIFFICULTY_RULE,
        }
    for threshold, label in DIFFICULTY_BANDS:
        if ratio >= threshold:
            return {"level": label, "ratio": round(ratio, 4), "source": source_note, "rule": DIFFICULTY_RULE}
    return {"level": "Very Hard", "ratio": round(ratio, 4), "source": source_note, "rule": DIFFICULTY_RULE}


def _highlighted_letter(row_cells):
    """Some years' reports drop the explicit "Correct answer" column
    entirely and instead mark the correct option by applying a Word
    text-highlight to its percentage cell. Returns the single highlighted
    option letter among the %A-%D cells, or None if zero or more than one
    cell is highlighted (caller decides how to handle that)."""
    letters = ["A", "B", "C", "D"]
    found = []
    for letter, cell in zip(letters, row_cells):
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                rpr = run._element.find(qn("w:rPr"))
                if rpr is None:
                    continue
                highlight = rpr.find(qn("w:highlight"))
                if highlight is not None and highlight.get(qn("w:val")) not in (None, "none"):
                    found.append(letter)
                    break
    return found[0] if len(found) == 1 else None


def extract_section_a_table(document):
    """Section A is the first table with header
    Question | Correct answer | % A | % B | % C | % D | Comments -- OR,
    in years whose report omits the "Correct answer" column entirely,
    Question | % A | % B | % C | % D [| % N/A] | Comments (the "% N/A"
    no-answer column is itself optional -- confirmed present for some years,
    absent for others, e.g. 2020's own report has none), where the correct
    option is instead indicated by a text highlight on its percentage cell
    (see `_highlighted_letter`). Either way, the return shape is normalised
    to [Question, Correct answer, %A, %B, %C, %D, Comments] so
    `build_section_a_answers` never needs to know which format it came from.

    Column-header spacing is not consistent between years either ("%A" vs
    "% A", confirmed on 2020's own report using the latter) -- matched with
    whitespace stripped rather than assuming one exact spelling, and the
    Comments column is located by name (always last) rather than by a
    hardcoded index, since a missing "% N/A" column shifts it over by one.
    """
    for kind, node in walk_body(document):
        if kind == "table":
            rows = table_to_rows(node)
            if not rows:
                continue
            header = [cell.replace(" ", "") for cell in rows[0]]
            if header[:2] == ["Question", "Correctanswer"]:
                return rows
            if header[:1] == ["Question"] and header[1:5] == ["%A", "%B", "%C", "%D"]:
                normalised = [["Question", "Correct answer", "% A", "% B", "% C", "% D", "Comments"]]
                for table_row, text_row in zip(node.rows[1:], rows[1:]):
                    correct = _highlighted_letter(table_row.cells[1:5])
                    normalised.append(
                        [text_row[0], correct or "", text_row[1], text_row[2], text_row[3], text_row[4], text_row[-1]]
                    )
                return normalised
    raise RuntimeError("Section A results table not found")


def extract_section_a_comment_spans(document, image_extractor):
    """Re-walks the same Section A results table `extract_section_a_table`
    finds, this time reading the Comments cell (always the last column, in
    both table formats that function normalises between) as rich spans
    rather than flat text -- these cells embed equation images too (7 of
    2025's 20 Section A comments do). Returns {question_num: [spans]}."""
    out = {}
    for kind, node in walk_body(document):
        if kind != "table":
            continue
        rows = table_to_rows(node)
        header = [cell.replace(" ", "") for cell in rows[0]] if rows else []
        is_results_table = rows and (
            header[:2] == ["Question", "Correctanswer"]
            or (header[:1] == ["Question"] and header[1:5] == ["%A", "%B", "%C", "%D"])
        )
        if not is_results_table:
            continue
        for table_row in node.rows[1:]:
            qnum_text = table_row.cells[0].text.strip().rstrip(".")
            if not qnum_text.isdigit():
                continue
            comment_cell = table_row.cells[-1]
            spans = []
            for paragraph in comment_cell.paragraphs:
                spans.extend(paragraph_to_spans(paragraph, image_extractor))
            out[int(qnum_text)] = spans
        return out
    return out


def build_section_a_answers(rows, source_document, year, comment_spans_by_qnum=None):
    comment_spans_by_qnum = comment_spans_by_qnum or {}
    entries = []
    for row in rows[1:]:
        # The question-number cell isn't consistently formatted even within
        # one report -- some rows are "1." (trailing period), some are "5"
        # (no period). Strip it before checking, otherwise inconsistently
        # formatted rows are silently dropped instead of erroring loudly.
        question_cell = row[0].strip().rstrip(".") if row else ""
        if not row or not question_cell.isdigit():
            continue
        question_num = int(question_cell)
        correct_raw = row[1].strip()
        percents = {}
        for label, value in zip(["A", "B", "C", "D"], row[2:6]):
            value = value.strip()
            if value:
                try:
                    percents[label] = float(value)
                except ValueError:
                    pass
        comment = row[6].strip() if len(row) > 6 else ""
        comment_spans = comment_spans_by_qnum.get(question_num, [])
        # Prefer the rich, image-preserving spans for the flat-text fallback
        # too, if present -- spans_text and the docx cell's plain .text
        # agree character-for-character except spans_text substitutes an
        # "[equation]" marker where an image sat, which is more honest than
        # silently concatenating the surrounding words as if nothing were
        # missing there.
        comment = spans_text(comment_spans) if comment_spans else comment

        # The "Correct answer" cell can name one letter ("B"), several
        # ("AD" -- multiple responses accepted after review), or be blank with
        # the Comments column stating all four were accepted. Parse generally
        # rather than special-casing only the single- and all-four-letter
        # cases, so a genuine multi-but-not-all case doesn't silently mark a
        # correct student answer wrong.
        withdrawn = not correct_raw and not percents and bool(WITHDRAWN_RE.search(comment))

        letters_found = sorted(set(re.findall(r"[ABCD]", correct_raw.upper())))
        all_accepted = len(letters_found) == 4 or bool(ALL_ACCEPTED_RE.search(comment))
        accepted_answers = ["A", "B", "C", "D"] if all_accepted else letters_found
        single_correct = accepted_answers[0] if len(accepted_answers) == 1 else None

        entry = {
            "interactionId": f"A{question_num}",
            "canonicalId": f"{year}-A{question_num}",
            "section": "A",
            "questionLabel": str(question_num),
            "marks": 0 if withdrawn else 1,
            "correctAnswer": single_correct,
            "acceptedAnswers": accepted_answers,
            "allOptionsAccepted": all_accepted,
            "withdrawn": withdrawn,
            "cohortPercentCorrect": percents.get(single_correct) if single_correct else None,
            "optionPercents": percents,
            "officialExplanation": comment,
            "examinerComments": [{"type": "examinerComment", "level": 0, "spans": comment_spans}] if comment_spans else [],
            "source": {"document": source_document, "location": "Section A results table"},
            "uncertain": (not accepted_answers) and not withdrawn,
            "uncertainReason": "" if (accepted_answers or withdrawn) else "No correct-answer letter recorded in the report table.",
        }
        ratio = (
            sum(percents.get(letter, 0) for letter in accepted_answers) / 100.0
            if accepted_answers and not all_accepted
            else None
        )
        entry["difficulty"] = (
            {"level": "unknown", "ratio": None, "source": "Question withdrawn -- not scored.", "rule": DIFFICULTY_RULE}
            if withdrawn
            else difficulty_from_ratio(ratio, source_note=f"{year} VCE Physics Examination Report cohort statistics.")
        )
        entries.append(entry)
    return entries


def extract_section_b_questions(document, image_extractor=None):
    """Group every paragraph/table between one question heading and the
    next into a per-question record, style-name-agnostic (see module
    docstring). `image_extractor` (an ImageExtractor, or None to skip images
    entirely) resolves embedded equation images to spans -- see
    paragraph_to_spans. A paragraph that is ENTIRELY an equation image (no
    surrounding text at all -- confirmed as the majority case: 64 of 2025's
    84 embedded images sit in their own image-only paragraph) has empty
    `.text`, so the emptiness check here must be "no spans at all", not "no
    text", or the whole paragraph -- and the only content it carries -- gets
    silently dropped.
    """
    questions = []
    current = None

    for kind, node in walk_body(document):
        if kind == "para":
            text = node.text.strip()
            if is_question_heading(node):
                current = {"heading": text, "interactionId": heading_to_interaction_id(text), "marksTable": None, "items": []}
                questions.append(current)
                continue
            if current is None:
                continue
            spans = paragraph_to_spans(node, image_extractor)
            if not spans:
                continue
            current["items"].append({"kind": "paragraph", "level": bullet_level(node), "spans": spans})
        elif kind == "table":
            if current is None:
                continue
            rows = table_to_rows(node)
            marks_info = parse_marks_table(rows)
            if marks_info is not None and current["marksTable"] is None:
                current["marksTable"] = marks_info
            else:
                current["items"].append({"kind": "table", "level": 0, "rows": rows})

    return questions


def build_section_b_answers(questions, source_document, year):
    entries = []
    for q in questions:
        interaction_id = q["interactionId"]
        marks_table = q["marksTable"]
        max_marks = marks_table["maxMarks"] if marks_table else None
        average = marks_table["average"] if marks_table else None

        official_answer = []
        examiner_comments = []
        carried_classification = None
        withdrawn = False
        for item in q["items"]:
            if item["kind"] == "table":
                official_answer.append({"type": "table", "rows": item["rows"]})
                continue
            item_text = spans_text(item["spans"])
            if WITHDRAWN_RE.search(item_text) and max_marks is None:
                withdrawn = True
            if item["level"] > 0 and carried_classification is not None:
                classification = carried_classification
            else:
                classification = classify_paragraph(item_text)
                carried_classification = classification if item["level"] == 0 else None
            record = {"type": classification, "level": item["level"], "spans": item["spans"]}
            if classification == "examinerComment":
                examiner_comments.append(record)
            else:
                official_answer.append(record)

        # VCE Physics reports frequently give a single "most common error
        # was..." paragraph as the ENTIRE substantive content for a
        # subquestion, with no separate formal marking-point statement --
        # classify_paragraph correctly buckets that into examiner_comments,
        # not official_answer, but it is still real, useful, verbatim VCAA
        # content (AnswerPanel renders both sections), so it must not be
        # flagged "uncertain" just because official_answer specifically is
        # empty. Only flag when there is truly nothing captured at all.
        full_marks_awarded = max_marks is None and any(
            FULL_MARKS_AWARDED_RE.search(spans_text(item["spans"]))
            for item in q["items"]
            if item["kind"] != "table"
        )

        has_any_text = bool(official_answer) or bool(examiner_comments)
        uncertain = (max_marks is None or not has_any_text) and not withdrawn
        reasons = []
        if withdrawn:
            reasons = []
        else:
            if max_marks is None and full_marks_awarded:
                reasons.append(
                    "VCAA awarded full marks to every student for this question (stated in the report), "
                    "but the report text doesn't give the marks value itself -- confirm it against the "
                    "original exam paper's own mark allocation and set it explicitly."
                )
            elif max_marks is None:
                reasons.append("No marks-distribution table found immediately after the heading.")
            if not has_any_text:
                reasons.append("No marking-guide or examiner-comment text captured under this heading.")
                if max_marks is not None:
                    # A marks table exists (so the question is real and scored)
                    # but no paragraph/table text follows the heading -- in the
                    # reports seen so far this happens when the official answer
                    # is a hand-drawn diagram/graph in the source document
                    # rather than text, which can't be extracted or guessed at.
                    # This is a factual disclosure, not a fabricated answer.
                    official_answer.append({
                        "type": "note",
                        "level": 0,
                        "spans": [{"text": (
                            "The official answer for this question could not be captured as text "
                            "(likely a drawn diagram/graph in the source report). "
                            f"See {source_document} under '{q['heading']}' directly."
                        )}],
                    })

        entry = {
            "interactionId": interaction_id,
            "canonicalId": f"{year}-{interaction_id}",
            "section": "B",
            "questionLabel": q["heading"].replace("Question", "").strip().rstrip("."),
            "marks": max_marks,
            "withdrawn": withdrawn,
            "marksDistributionPct": marks_table["distributionPct"] if marks_table else {},
            "averageMark": average,
            "officialAnswer": official_answer,
            "examinerComments": examiner_comments,
            "source": {"document": source_document, "location": q["heading"]},
            "uncertain": uncertain,
            "uncertainReason": "; ".join(reasons),
        }
        ratio = (average / max_marks) if (average is not None and max_marks) else None
        entry["difficulty"] = (
            {"level": "unknown", "ratio": None, "source": "Question withdrawn -- not scored.", "rule": DIFFICULTY_RULE}
            if withdrawn
            else difficulty_from_ratio(ratio, source_note=f"{year} VCE Physics Examination Report cohort statistics.")
        )
        entries.append(entry)
    return entries
