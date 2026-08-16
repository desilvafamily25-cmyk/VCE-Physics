import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import type { CurriculumTag, ErrorRecord, Interaction, Paper } from "../data/types";
import { repository } from "../data";
import { buildErrorRecords, unresolvedErrors } from "../lib/errorBank";

type EnrichedError = ErrorRecord & {
  paperTitle: string;
  questionLabel: string;
  areaOfStudy: string | null;
  topic: string | null;
};

export function ErrorBankRoute() {
  const [records, setRecords] = useState<EnrichedError[] | null>(null);
  const [showUnresolvedOnly, setShowUnresolvedOnly] = useState(true);
  const [yearFilter, setYearFilter] = useState<string>("");
  const [areaFilter, setAreaFilter] = useState<string>("");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const [papers, history] = await Promise.all([repository.getPapers(), repository.getQuestionHistory()]);
      const errorRecords = buildErrorRecords(history);
      if (errorRecords.length === 0) {
        if (!cancelled) setRecords([]);
        return;
      }

      const papersById = new Map<string, Paper>(papers.map((p) => [p.id, p]));
      const involvedPaperIds = Array.from(new Set(errorRecords.map((r) => r.paperId)));

      const interactionsByPaper = new Map<string, Interaction[]>();
      const curriculumByPaper = new Map<string, CurriculumTag[]>();
      await Promise.all(
        involvedPaperIds.map(async (paperId) => {
          const paper = papersById.get(paperId);
          if (!paper) return;
          const [interactions, curriculum] = await Promise.all([
            repository.getInteractions(paper),
            repository.getCurriculumMap(paper)
          ]);
          interactionsByPaper.set(paperId, interactions);
          curriculumByPaper.set(paperId, curriculum ?? []);
        })
      );

      const enriched: EnrichedError[] = errorRecords.map((record) => {
        const paper = papersById.get(record.paperId);
        const interaction = interactionsByPaper.get(record.paperId)?.find((i) => i.id === record.interactionId);
        const tag = curriculumByPaper.get(record.paperId)?.find((c) => c.interactionId === record.interactionId);
        return {
          ...record,
          paperTitle: paper?.title ?? record.paperId,
          questionLabel: interaction?.question ?? record.interactionId,
          areaOfStudy: tag?.areaOfStudy ?? null,
          topic: tag?.topic ?? null
        };
      });

      if (!cancelled) setRecords(enriched);
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const years = useMemo(() => Array.from(new Set((records ?? []).map((r) => r.paperId))).sort().reverse(), [records]);
  const areas = useMemo(
    () => Array.from(new Set((records ?? []).map((r) => r.areaOfStudy).filter(Boolean))).sort() as string[],
    [records]
  );

  const filtered = useMemo(() => {
    let list = records ?? [];
    if (showUnresolvedOnly) list = unresolvedErrors(list) as EnrichedError[];
    if (yearFilter) list = list.filter((r) => r.paperId === yearFilter);
    if (areaFilter) list = list.filter((r) => r.areaOfStudy === areaFilter);
    return list;
  }, [records, showUnresolvedOnly, yearFilter, areaFilter]);

  if (!records) {
    return <div className="loading">Loading error bank…</div>;
  }

  return (
    <div className="page">
      <h2>My Errors</h2>
      <p className="page-intro">
        Every question you've gotten wrong in Practice Mode, Timed review, or Topic Practice is tracked here — retry
        it directly from this list. A question drops off "unresolved" once you get it right again.
      </p>

      {records.length === 0 && (
        <div className="empty-state card">
          <p>No errors recorded yet — nice work, or you haven't checked any answers yet.</p>
          <Link className="btn btn-primary btn-sm" to="/papers">
            Start practising
          </Link>
        </div>
      )}

      {records.length > 0 && (
        <>
          <div className="topic-filters">
            <label className="dev-toggle">
              <input type="checkbox" checked={showUnresolvedOnly} onChange={(e) => setShowUnresolvedOnly(e.target.checked)} />
              Unresolved only
            </label>
            <select value={yearFilter} onChange={(e) => setYearFilter(e.target.value)}>
              <option value="">All papers</option>
              {years.map((year) => (
                <option key={year} value={year}>
                  {year}
                </option>
              ))}
            </select>
            <select value={areaFilter} onChange={(e) => setAreaFilter(e.target.value)}>
              <option value="">All Areas of Study</option>
              {areas.map((area) => (
                <option key={area} value={area}>
                  {area}
                </option>
              ))}
            </select>
            <button
              type="button"
              className="btn btn-primary btn-sm"
              disabled={filtered.length === 0}
              onClick={() => {
                const byPaper = new Map<string, string[]>();
                filtered.forEach((r) => byPaper.set(r.paperId, [...(byPaper.get(r.paperId) ?? []), r.interactionId]));
                const [firstPaper, ids] = Array.from(byPaper.entries())[0];
                window.location.assign(`/topics/session?paper=${firstPaper}&ids=${ids.join(",")}`);
              }}
            >
              Practise all unresolved ({filtered.length})
            </button>
          </div>

          <div className="data-table-wrap">
            <table className="review-table">
              <thead>
                <tr>
                  <th>Paper</th>
                  <th>Q</th>
                  <th>Topic</th>
                  <th>Attempts</th>
                  <th>Times wrong</th>
                  <th>Latest answer</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((record) => (
                  <tr key={record.canonicalId} className={record.mastered ? "review-row-correct" : "review-row-incorrect"}>
                    <td>{record.paperTitle}</td>
                    <td>{record.questionLabel}</td>
                    <td>{record.topic ?? "—"}</td>
                    <td>{record.timesAttempted}</td>
                    <td>{record.timesIncorrect}</td>
                    <td>{record.latestStudentAnswer || <em>—</em>}</td>
                    <td>{record.mastered ? "Mastered" : "Unresolved"}</td>
                    <td>
                      <Link className="btn btn-ghost btn-sm" to={`/topics/session?paper=${record.paperId}&ids=${record.interactionId}`}>
                        Retry
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
