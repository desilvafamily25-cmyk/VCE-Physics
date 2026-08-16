# VCE Physics 50 — Past Paper Practice

A VCE Physics past-exam practice platform: real VCAA past papers rendered from the original PDF with an interactive overlay (multiple-choice selectors, written-response fields), Timed and Practice modes, official examination-report answers, topic-tagged practice by Area of Study, an Error Bank, and a toggle-able formula-sheet reference panel.

Architecturally mirrors a VCE Chemistry sibling project: React + TypeScript + Vite SPA, PDF.js for exam rendering, a `DataRepository` interface (`src/data/repository.ts`) as the only thing UI components touch for data, backed by Supabase (Postgres + Auth + RLS). See [docs/DATA-ARCHITECTURE.md](docs/DATA-ARCHITECTURE.md) for the full data model.

## Getting started

```bash
npm install
npm run dev
```

### Data pipeline (Python)

Source PDFs (exam papers, examination reports, official study designs) live in the four gitignored top-level folders (`archive-2002-2016/`, `previous-design-2017-2023/`, `current-design-2024-2027/`, `reference/`) — never committed in bulk, per `INDEX.md`. The extraction pipeline turns them into the JSON this app actually serves:

```bash
pip install pymupdf python-docx
python scripts/generate_paper_assets.py       # papers.json, interaction geometry, formula sheets, for every discovered exam
python scripts/extract_2025_report.py         # data/answers/2025.json from the 2025 examination report
python scripts/build_2025_section_b.py        # hand-verifiable Section B geometry, labelled to match the report's subpart ids
python scripts/build_2025_curriculum_map.py   # data/curriculum/2025-mapping.json against the official study design
python scripts/audit_interactions.py          # structural checks: no ID gaps/dupes/overlaps, no out-of-bounds rects
```

## Deploying

`netlify.toml` has the build command, publish dir and SPA redirect. Supabase URL/anon key are baked into `src/lib/supabaseClient.ts` as a public fallback (RLS is the real security boundary — see that file's comment) with `VITE_SUPABASE_URL`/`VITE_SUPABASE_ANON_KEY` as an optional override.
