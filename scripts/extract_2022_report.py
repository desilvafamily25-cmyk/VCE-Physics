"""Deterministic extraction of the 2022 VCE Physics examination report --
identical technique to extract_2023_report.py (same shared
report_extraction_lib.py, same image-extraction pipeline for embedded
equation objects). See that script's docstring for the full rationale.

2022 uses the 2017-2023 study design (see data/curriculum/study-design-
2016.json), and its report docx uses the same table/heading structure as
the other docx-report years (Section A percentage-per-option table, Section
B "Question Na." headings with marks-distribution tables) -- confirmed by
direct inspection -- so no extraction-logic changes were needed, only new
source paths.

Outputs:
  data/raw/2022-report-extract.json
  data/answers/2022.json
  public/answer-images/2022-*.png
"""
import json
import sys
from pathlib import Path

import docx

sys.path.insert(0, str(Path(__file__).resolve().parent))
from report_extraction_lib import (  # noqa: E402
    ImageExtractor,
    build_section_a_answers,
    build_section_b_answers,
    extract_section_a_comment_spans,
    extract_section_a_table,
    extract_section_b_questions,
)

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "previous-design-2017-2023" / "2022-physics-report.docx"
SOURCE_DOCUMENT = "2022-physics-report.docx"
YEAR = "2022"
RAW_OUT = ROOT / "data" / "raw" / "2022-report-extract.json"
ANSWERS_OUT = ROOT / "data" / "answers" / "2022.json"
IMAGE_OUT_DIR = ROOT / "public" / "answer-images"
IMAGE_URL_PREFIX = "/answer-images"


def main():
    document = docx.Document(REPORT_PATH)
    image_extractor = ImageExtractor(document, IMAGE_OUT_DIR, IMAGE_URL_PREFIX, YEAR)

    section_a_rows = extract_section_a_table(document)
    section_a_comment_spans = extract_section_a_comment_spans(document, image_extractor)
    section_b_questions = extract_section_b_questions(document, image_extractor)

    RAW_OUT.parent.mkdir(parents=True, exist_ok=True)
    RAW_OUT.write_text(
        json.dumps(
            {
                "source": str(REPORT_PATH.relative_to(ROOT)).replace("\\", "/"),
                "sectionA": {"tableRows": section_a_rows, "commentSpans": section_a_comment_spans},
                "sectionB": section_b_questions,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    section_a_answers = build_section_a_answers(section_a_rows, SOURCE_DOCUMENT, YEAR, section_a_comment_spans)
    section_b_answers = build_section_b_answers(section_b_questions, SOURCE_DOCUMENT, YEAR)
    all_answers = section_a_answers + section_b_answers

    ANSWERS_OUT.parent.mkdir(parents=True, exist_ok=True)
    ANSWERS_OUT.write_text(json.dumps(all_answers, indent=2, ensure_ascii=False), encoding="utf-8")

    uncertain_count = sum(1 for a in all_answers if a["uncertain"])
    withdrawn_count = sum(1 for a in all_answers if a.get("withdrawn"))
    print(f"Section A: {len(section_a_answers)} questions")
    print(f"Section B: {len(section_b_answers)} subquestions")
    print(f"Total: {len(all_answers)}")
    print(f"Flagged uncertain: {uncertain_count}")
    print(f"Withdrawn: {withdrawn_count}")
    print(f"Embedded images extracted: {image_extractor._counter}")


if __name__ == "__main__":
    main()
