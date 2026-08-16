"""Deterministic extraction of the 2019 VCE Physics examination report --
same curated-answer-dataset contract as extract_2023_report.py and its
siblings (data/raw/<year>-report-extract.json, data/answers/<year>.json,
public/answer-images/<year>-*.png), built on top of the shared classification
helpers in report_extraction_lib.py (build_section_a_answers,
build_section_b_answers, spans_text, classify_paragraph, ...), but every
low-level extraction step comes from pdf_report_extraction_lib.py instead:
2017-2019's reports are PDF, not docx, and expose no document object model
at all -- see that module's own docstring for the two structural
discoveries (grey-cell-shaded correct answers, ruled-line marks tables)
this whole approach is built around.

Outputs:
  data/raw/2019-report-extract.json
  data/answers/2019.json
  public/answer-images/2019-b*.png
"""
import json
import sys
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pdf_report_extraction_lib import (  # noqa: E402
    extract_section_a_table_pdf,
    extract_section_b_questions_pdf,
    find_section_b_start_page,
)
from report_extraction_lib import (  # noqa: E402
    build_section_a_answers,
    build_section_b_answers,
)

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "previous-design-2017-2023" / "2019-physics-report.pdf"
SOURCE_DOCUMENT = "2019-physics-report.pdf"
YEAR = "2019"
RAW_OUT = ROOT / "data" / "raw" / "2019-report-extract.json"
ANSWERS_OUT = ROOT / "data" / "answers" / "2019.json"
IMAGE_OUT_DIR = ROOT / "public" / "answer-images"
IMAGE_URL_PREFIX = "/answer-images"


def main():
    doc = fitz.open(REPORT_PATH)

    section_b_start = find_section_b_start_page(doc)
    if section_b_start is None:
        raise SystemExit("Could not locate 'Section B' heading in the report")
    section_a_range = (1, section_b_start)
    section_b_range = (section_b_start, doc.page_count)

    section_a_rows = extract_section_a_table_pdf(doc, section_a_range)
    section_b_questions = extract_section_b_questions_pdf(doc, section_b_range, IMAGE_OUT_DIR, IMAGE_URL_PREFIX, YEAR)

    RAW_OUT.parent.mkdir(parents=True, exist_ok=True)
    RAW_OUT.write_text(
        json.dumps(
            {
                "source": str(REPORT_PATH.relative_to(ROOT)).replace("\\", "/"),
                "sectionA": {"tableRows": section_a_rows},
                "sectionB": section_b_questions,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    section_a_answers = build_section_a_answers(section_a_rows, SOURCE_DOCUMENT, YEAR)
    section_b_answers = build_section_b_answers(section_b_questions, SOURCE_DOCUMENT, YEAR)
    all_answers = section_a_answers + section_b_answers

    ANSWERS_OUT.parent.mkdir(parents=True, exist_ok=True)
    ANSWERS_OUT.write_text(json.dumps(all_answers, indent=2, ensure_ascii=False), encoding="utf-8")

    uncertain_count = sum(1 for a in all_answers if a["uncertain"])
    withdrawn_count = sum(1 for a in all_answers if a.get("withdrawn"))
    total_marks = sum(a["marks"] or 0 for a in all_answers)
    print(f"Section A: {len(section_a_answers)} questions")
    print(f"Section B: {len(section_b_answers)} subquestions")
    print(f"Total: {len(all_answers)}")
    print(f"Total marks: {total_marks}")
    print(f"Flagged uncertain: {uncertain_count}")
    print(f"Withdrawn: {withdrawn_count}")


if __name__ == "__main__":
    main()
