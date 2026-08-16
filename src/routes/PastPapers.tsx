import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import type { Attempt, Paper } from "../data/types";
import { repository } from "../data";
import { StatusBadge, type PaperStatus } from "../components/StatusBadge";
import { scoreSectionA } from "../lib/scoring";

type Row = {
  paper: Paper;
  attempt: Attempt | null;
  status: PaperStatus;
  sectionAScore: string | null;
};

const ERA_LABELS: Record<Paper["era"], string> = {
  current: "Current design (2024–2027)",
  previous: "Previous design (2017–2023)",
  archive: "Archive (2002–2016)"
};

function statusFor(attempt: Attempt | null): PaperStatus {
  if (!attempt) return "not-started";
  return attempt.submittedAt ? "completed" : "in-progress";
}

export function PastPapersRoute() {
  const [rows, setRows] = useState<Row[] | null>(null);
  const [era, setEra] = useState<"all" | Paper["era"]>("all");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const papers = await repository.getPapers();
      const built = await Promise.all(
        papers.map(async (paper) => {
          const attempt = await repository.getAttempt(paper.id);
          const status = statusFor(attempt);
          let sectionAScore: string | null = null;

          if (status === "completed" && paper.hasAnswerData && attempt) {
            const [interactions, answers] = await Promise.all([
              repository.getInteractions(paper),
              repository.getAnswers(paper)
            ]);
            if (answers) {
              const answerMap = new Map(answers.map((a) => [a.interactionId, a]));
              const score = scoreSectionA(interactions, attempt.answers, answerMap);
              sectionAScore = paper.hasMultipleChoice ? `${score.correct} / ${score.total}` : null;
            }
          }

          return { paper, attempt, status, sectionAScore };
        })
      );
      if (!cancelled) setRows(built);
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const filteredRows = useMemo(() => (rows ?? []).filter((r) => era === "all" || r.paper.era === era), [rows, era]);

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h2>Past Papers</h2>
          <p className="page-intro">
            Choose a paper, then attempt it in Timed Mode (real exam conditions) or Practice Mode (instant feedback
            as you go). Papers without official answer data yet can still be timed — Practice feedback and topic
            tagging roll out progressively.
          </p>
        </div>
      </div>

      <div className="era-filter-bar">
        {(["all", "current", "previous", "archive"] as const).map((value) => (
          <button
            key={value}
            type="button"
            className={era === value ? "chip-toggle chip-active" : "chip-toggle"}
            onClick={() => setEra(value)}
          >
            {value === "all" ? "All years" : ERA_LABELS[value]}
          </button>
        ))}
      </div>

      {!rows && <div className="loading">Loading papers…</div>}

      {rows && (
        <div className="papers-grid">
          {filteredRows.map(({ paper, status, sectionAScore }) => (
            <div key={paper.id} className="card card-interactive paper-card">
              <div className="paper-card-top">
                <div>
                  <p className="paper-card-title">{paper.title}</p>
                  <p className="paper-card-meta">
                    <span className="badge badge-neutral">{ERA_LABELS[paper.era]}</span>
                    {!paper.hasMultipleChoice && <span className="badge badge-info">No MCQ (elective study)</span>}
                  </p>
                </div>
                <StatusBadge status={status} />
              </div>

              <p className="paper-card-meta">
                {paper.readingMinutes} min reading · {paper.writingMinutes} min writing · {paper.totalMarks} marks
              </p>

              {sectionAScore && (
                <p className="paper-card-score">
                  Section A score: <strong>{sectionAScore}</strong>
                </p>
              )}

              {!paper.hasAnswerData && (
                <p className="badge badge-warning" style={{ alignSelf: "flex-start" }}>
                  Answers not yet available — Timed Mode only
                </p>
              )}

              <div className="paper-card-actions">
                <Link className="btn btn-primary btn-sm" to={`/attempt/${paper.id}/timed`}>
                  Timed
                </Link>
                <Link className="btn btn-secondary btn-sm" to={`/attempt/${paper.id}/practice`}>
                  Practice
                </Link>
                {status === "completed" && (
                  <Link className="btn btn-ghost btn-sm" to={`/review/${paper.id}`}>
                    Review
                  </Link>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
