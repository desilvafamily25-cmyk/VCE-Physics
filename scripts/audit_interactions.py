import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

# Interaction ids individually verified (by rendering the placed rect back
# onto the source PDF page and visually confirming the fit) to be genuinely
# tiny VCAA-provided answer spaces, not a detection error -- e.g. a single
# unit/value box embedded in a diagram, rather than a normal writable text
# field. Excluded from the "tiny Section B fields to review" heuristic below
# so it stays useful for catching real future errors instead of permanently
# flagging known-good geometry.
KNOWN_TINY_FIELDS = {
    # 2024: no text layer, so these three subparts have no ruled working
    # lines to detect at all -- just a bare unit box (Hz, eV) or a pair of
    # them (V, Hz) with no space above for working. Confirmed correct by
    # pixel-precise ink-band scans of the source PDF and a rendered overlay
    # check -- see MANUAL_ENTRIES in scripts/build_2024_section_b.py.
    "2024": {"B10b", "B16cii", "B16ciii"},
    # 2023: B5b is a "show current direction on the small square loop in
    # Figure 5" annotation with no ruled working lines around it; B17e is a
    # fill-in-the-table question whose interactive rect is one table column
    # (narrower than a normal writable field by design). Confirmed correct
    # via a rendered overlay check -- see MANUAL_ENTRIES in
    # scripts/build_2023_section_b.py.
    "2023": {"B5b", "B17e"},
    # 2021: B1a is a small "draw an arrow at point P" annotation area inside
    # a bar-magnet figure; B2b is a small bordered box holding a single
    # multiple-choice-style letter answer, not a normal writable field.
    # Confirmed correct via a rendered overlay check -- see MANUAL_ENTRIES
    # in scripts/build_2021_section_b.py.
    "2021": {"B1a", "B2b"},
    # 2020: B3ci, B5a, B6a and B17a are all small bordered boxes holding a
    # single word/letter/number answer (a point choice, a rotation
    # direction, a trend direction, a spectral-line wavelength read
    # straight off a figure), not normal multi-line writable fields.
    # Confirmed correct via a rendered overlay check -- see MANUAL_ENTRIES
    # in scripts/build_2020_section_b.py.
    "2020": {"B3ci", "B5a", "B6a", "B17a"},
}


def main():
    papers = json.loads((PUBLIC / "papers.json").read_text(encoding="utf-8"))
    issues = []

    for paper in papers:
        path = PUBLIC / paper["interactionsUrl"].lstrip("/")
        items = json.loads(path.read_text(encoding="utf-8-sig"))
        section_a = [item for item in items if item.get("section") == "A"]
        section_b = [item for item in items if item.get("section") == "B"]
        seen = {}
        for item in section_a:
            seen.setdefault(item["id"], []).append(item)

        dupes = [key for key, value in seen.items() if len(value) > 1]
        if dupes:
            issues.append((paper["title"], "duplicate Section A IDs", ", ".join(dupes)))

        expected_total = paper.get("sectionATotal") or 0
        if expected_total:
            expected = {f"A{number}" for number in range(1, expected_total + 1)}
            actual = {item["id"] for item in section_a}
            missing = sorted(expected - actual, key=lambda value: int(value[1:]))
            extra = sorted(actual - expected)
            if missing:
                issues.append((paper["title"], "missing Section A IDs", ", ".join(missing)))
            if extra:
                issues.append((paper["title"], "extra Section A IDs", ", ".join(extra)))
        elif section_a:
            issues.append((paper["title"], "unexpected Section A items on a no-MCQ paper", str(len(section_a))))

        for item in items:
            rect = item.get("rect", {})
            values = [rect.get("x"), rect.get("y"), rect.get("width"), rect.get("height")]
            if any(not isinstance(value, (int, float)) for value in values):
                issues.append((paper["title"], f"{item.get('id')} invalid rect", str(rect)))
                continue
            if rect["x"] < 0 or rect["y"] < 0 or rect["x"] + rect["width"] > 1.02 or rect["y"] + rect["height"] > 1.02:
                issues.append((paper["title"], f"{item.get('id')} rect outside page", str(rect)))

        # Overlap check within the same page (any two rects on the same page
        # whose bounding boxes intersect by a non-trivial area) -- catches a
        # class of geometry error the ID/bounds checks above can't see.
        by_page = {}
        for item in items:
            by_page.setdefault(item["page"], []).append(item)
        for page_items in by_page.values():
            for i in range(len(page_items)):
                for j in range(i + 1, len(page_items)):
                    a, b = page_items[i]["rect"], page_items[j]["rect"]
                    ox = max(0, min(a["x"] + a["width"], b["x"] + b["width"]) - max(a["x"], b["x"]))
                    oy = max(0, min(a["y"] + a["height"], b["y"] + b["height"]) - max(a["y"], b["y"]))
                    overlap_area = ox * oy
                    smaller_area = min(a["width"] * a["height"], b["width"] * b["height"])
                    if smaller_area > 0 and overlap_area / smaller_area > 0.35:
                        issues.append(
                            (
                                paper["title"],
                                "overlapping rects",
                                f"{page_items[i]['id']} / {page_items[j]['id']} on page {page_items[i]['page']}",
                            )
                        )

        known_tiny = KNOWN_TINY_FIELDS.get(paper["id"], set())
        tiny_written = [
            item["id"]
            for item in section_b
            if item["id"] not in known_tiny
            and (item.get("rect", {}).get("height", 0) < 0.045 or item.get("rect", {}).get("width", 0) < 0.18)
        ]
        if tiny_written:
            issues.append((paper["title"], "tiny Section B fields to review", ", ".join(tiny_written[:12])))

    if issues:
        for title, kind, detail in issues:
            print(f"{title}: {kind}: {detail}")
        print(f"\n{len(issues)} issue group(s) found across {len(papers)} papers")
        raise SystemExit(1)

    print(f"Audit passed for {len(papers)} papers")


if __name__ == "__main__":
    main()
