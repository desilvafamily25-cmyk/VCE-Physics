"""Deterministic extraction of the 2024 VCE Physics examination report --
identical technique to extract_2025_report.py (same shared
report_extraction_lib.py, same image-extraction pipeline for embedded
equation objects). See that script's docstring for the full rationale.

Outputs:
  data/raw/2024-report-extract.json
  data/answers/2024.json
  public/answer-images/2024-*.png
"""
import json
import sys
from pathlib import Path

import docx

sys.path.insert(0, str(Path(__file__).resolve().parent))
from report_extraction_lib import (  # noqa: E402
    DIFFICULTY_RULE,
    ImageExtractor,
    build_section_a_answers,
    build_section_b_answers,
    extract_section_a_comment_spans,
    extract_section_a_table,
    extract_section_b_questions,
)

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "current-design-2024-2027" / "2024-physics-report.docx"
SOURCE_DOCUMENT = "2024-physics-report.docx"
YEAR = "2024"
RAW_OUT = ROOT / "data" / "raw" / "2024-report-extract.json"
ANSWERS_OUT = ROOT / "data" / "answers" / "2024.json"
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

    # Question 13d: the report states "As a result of psychometric analysis
    # and review, all students were awarded full marks for this question"
    # but never states the marks value itself (and there's correspondingly
    # no distribution table to infer it from -- see FULL_MARKS_AWARDED_RE).
    # Confirmed as 1 mark from two independent sources: (1) the exam paper's
    # own "Question 13 (9 marks)" heading, cross-checked against 13a=1,
    # 13b=2, 13c=2, 13e=3 (1+2+2+3=8, so 13d=9-8=1); (2) this exactly
    # accounts for the 1-mark gap between this extraction's Section A+B
    # total (119) and the official 120-mark spec total confirmed in
    # docs/DATA-ARCHITECTURE.md. Not a fabricated value -- a confirmed
    # correction to a genuine gap in the report's own text.
    for answer in all_answers:
        if answer["canonicalId"] == "2024-B13d":
            answer["marks"] = 1
            answer["marksDistributionPct"] = {"1": 100.0}
            answer["averageMark"] = 1.0
            answer["uncertain"] = False
            answer["uncertainReason"] = ""
            answer["difficulty"] = {
                "level": "Easy",
                "ratio": 1.0,
                "source": "Marks value confirmed against the exam paper's own 'Question 13 (9 marks)' heading and the official 120-mark exam total, not stated directly in the report text -- see the comment above this override in extract_2024_report.py.",
                "rule": DIFFICULTY_RULE,
            }

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
