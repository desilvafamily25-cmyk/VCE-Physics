"""Deterministic extraction of the 2025 VCE Physics examination report into
structured JSON, plus a curated answer dataset built from that structure.

This script performs NO physics interpretation and invents nothing: it walks
the .docx body in true document order (paragraphs interleaved with tables)
and regroups the report's own text under each question heading. Every field
in the curated output is either copied verbatim from the report or is a
mechanical derivation (e.g. "average / maxMarks" for a difficulty ratio)
whose rule is recorded alongside the data. Shared extraction logic lives in
report_extraction_lib.py (used by every docx-report year's extraction
script).

Outputs:
  data/raw/2025-report-extract.json   -- full verbatim walk of the report,
                                          grouped by question, for audit/review
  data/answers/2025.json              -- curated per-question answer records
                                          keyed by canonical id "2025-<interactionId>"
"""
import json
import sys
from pathlib import Path

import docx

sys.path.insert(0, str(Path(__file__).resolve().parent))
from report_extraction_lib import (  # noqa: E402
    build_section_a_answers,
    build_section_b_answers,
    extract_section_a_table,
    extract_section_b_questions,
)

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "current-design-2024-2027" / "2025-physics-report.docx"
SOURCE_DOCUMENT = "2025-physics-report.docx"
YEAR = "2025"
RAW_OUT = ROOT / "data" / "raw" / "2025-report-extract.json"
ANSWERS_OUT = ROOT / "data" / "answers" / "2025.json"


def main():
    document = docx.Document(REPORT_PATH)

    section_a_rows = extract_section_a_table(document)
    section_b_questions = extract_section_b_questions(document)

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
    print(f"Section A: {len(section_a_answers)} questions")
    print(f"Section B: {len(section_b_answers)} subquestions")
    print(f"Total: {len(all_answers)}")
    print(f"Flagged uncertain: {uncertain_count}")
    print(f"Withdrawn: {withdrawn_count}")


if __name__ == "__main__":
    main()
