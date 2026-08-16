# Missing Resources

Official VCAA Physics holdings checked 2026-08-16, against the four source folders described in `INDEX.md` (downloaded 2026-08-08 from vcaa.vic.edu.au).

VCAA does not publish a separate answer key for any exam year. **The examination report is the sole official answer/marking source.** Every exam file in this project has a matching report file, confirmed by direct folder listing — no gaps found across archive-2002-2016, previous-design-2017-2023 or current-design-2024-2027.

| Year(s) | Examination paper(s) | Examination report(s) | Answers/solutions | Notes |
|---|---|---|---|---|
| 2024–2025 | Found | Found (.docx) | Contained in report | Current design (2024-2027). |
| 2017–2023 | Found | Found (2017-2019: .pdf; 2020-2023: .docx) | Contained in report | Previous design. |
| 2013–2016 | Found | Found (.pdf) | Contained in report | Single end-of-year exam. |
| 2002–2012 | Found (Exam 1 + Exam 2 each year) | Found (Report 1 + Report 2 each year) | Contained in report | Two sittings/year (Exam 1 mid-year, Exam 2 end-of-year). |
| 2004 pilot | Found (Exam 1 + Exam 2) | Found (Report 1 + Report 2) | Contained in report | Pilot sitting alongside the regular 2004 papers. |

## `reference/` folder

| File | What it is | Caveat |
|---|---|---|
| `exam-specifications-v2-2025.docx` | Official current-design (2024-2027) exam specification | Confirms Section A = 20 MCQ/20 marks, Section B = 100 marks, total 120 — used directly in `docs/DATA-ARCHITECTURE.md` rather than assumed. |
| `formula-sheet-2026-02.pdf` | Current standalone formula sheet (4 pages) | Only the most-recent copy. The app does **not** rely on this file for per-paper formula sheets — each paper's own era-correct sheet is extracted from the back of that paper's own exam PDF instead (see `scripts/generate_paper_assets.py`), since VCAA appends a formula sheet to every exam booklet and the content has evolved between eras. |
| `mc-answer-sheet.pdf` | A **blank** multiple-choice bubble-answer-sheet template | Not an answer key — it's the physical sheet students bubble their own answers onto. Confirmed by reading its content directly (erase-mistake instructions, empty bubble grid, no answers of any kind). |
| `sample-exam-2024.pdf` | VCAA's sample examination for the current design | **Partially** contradicts `INDEX.md`'s note that it "has no published solutions": the last page *does* list Section A (MCQ) answers, but there is no Section B marking guide of any kind. Not used as a data source for this app (it's a sample, not a real sitting), but flagged here since the discrepancy is worth knowing. |

## A data-quality note, not a missing resource

`current-design-2024-2027/2024-physics-exam.pdf` has **no extractable text layer at all** (0 fonts, every character rendered as a vector outline) — confirmed via PyMuPDF (`fitz.open(...).get_fonts()` returns `[]`, `get_text()` returns empty on every page). `2025-physics-exam.pdf` has a normal embedded-font text layer. This doesn't block anything (interaction rects are hand-placed/verified visually regardless of text extraction), but it does mean 2024's paper-asset generation falls back to positional heuristics (`durationSource`/formula-sheet-boundary "positional-fallback" notes in `public/papers.json`) rather than text-search detection, and its interaction geometry will need the same visual, page-by-page verification pass 2025 already had before it's considered airtight.
