import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import type { Attempt, CurriculumTag, Interaction, Paper, QuestionAnswer, QuestionResult } from "../data/types";
import { repository } from "../data";
import { acceptedAnswerLabel, ContentBlocks } from "../components/AnswerPanel";
import { isMcqCorrect, scoreSectionA, summarizeSectionBAnswered } from "../lib/scoring";

type Outcome = "correct" | "incorrect" | "unanswered" | "unassessed" | "withdrawn";

type ReviewRow = {
  interaction: Interaction;
  studentAnswer: string;
  outcome: Outcome;
  tag: CurriculumTag | null;
  answer: QuestionAnswer | null;
};

const FILTERS = [
  { id: "all", label: "All questions" },
  { id: "incorrect", label: "Incorrect only" },
  { id: "unanswered", label: "Unanswered only" }
] as const;

export function ReviewRoute() {
  const { paperId = "" } = useParams();
  const [paper, setPaper] = useState<Paper | null>(null);
  const [attempt, setAttempt] = useState<Attempt | null>(null);
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [answers, setAnswers] = useState<QuestionAnswer[] | null>(null);
  const [curriculum, setCurriculum] = useState<CurriculumTag[] | null>(null);
  const [history, setHistory] = useState<QuestionResult[]>([]);
  const [filter, setFilter] = useState<string>("all");
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const papers = await repository.getPapers();
      const found = papers.find((p) => p.id === paperId) ?? null;
      if (!found || cancelled) return;
      setPaper(found);

      const [loadedAttempt, loadedInteractions, loadedAnswers, loadedCurriculum, loadedHistory] = await Promise.all([
        repository.getAttempt(found.id),
        repository.getInteractions(found),
        repository.getAnswers(found),
        repository.getCurriculumMap(found),
        repository.getQuestionHistory(found.id)
      ]);
      if (cancelled) return;
      setAttempt(loadedAttempt);
      setInteractions(loadedInteractions);
      setAnswers(loadedAnswers);
      setCurriculum(loadedCurriculum);
      setHistory(loadedHistory);
    })();
    return () => {
      cancelled = true;
    };
  }, [paperId]);

  const rows: ReviewRow[] = useMemo(() => {
    if (!attempt) return [];
    const answerMap = new Map((answers ?? []).map((a) => [a.interactionId, a]));
    const tagMap = new Map((curriculum ?? []).map((c) => [c.interactionId, c]));
    const latestResultByInteraction = new Map<string, QuestionResult>();
    for (const result of history) {
      const existing = latestResultByInteraction.get(result.interactionId);
      if (!existing || result.checkedAt > existing.checkedAt) {
        latestResultByInteraction.set(result.interactionId, result);
      }
    }

    return interactions.map((interaction) => {
      const studentAnswer = attempt.answers[interaction.id] ?? "";
      const answer = answerMap.get(interaction.id) ?? null;
      const tag = tagMap.get(interaction.id) ?? null;
      let outcome: Outcome;

      if (answer?.withdrawn) {
        outcome = "withdrawn";
      } else if (interaction.section === "A") {
        if (!studentAnswer.trim()) outcome = "unanswered";
        else if (answer) outcome = isMcqCorrect(studentAnswer, answer) ? "correct" : "incorrect";
        else outcome = "unassessed";
      } else {
        if (!studentAnswer.trim()) {
          outcome = "unanswered";
        } else {
          const result = latestResultByInteraction.get(interaction.id);
          if (!result) outcome = "unassessed";
          else if (result.outcome === "correct") outcome = "correct";
          else if (result.outcome === "incorrect" || result.outcome === "partially_correct") outcome = "incorrect";
          else outcome = "unassessed";
        }
      }

      return { interaction, studentAnswer, outcome, tag, answer };
    });
  }, [attempt, interactions, answers, curriculum, history]);

  const areaBreakdown = useMemo(() => {
    const byArea = new Map<string, { topic: string; correct: number; incorrect: number; total: number }>();
    for (const row of rows) {
      if (!row.tag) continue;
      if (row.outcome !== "correct" && row.outcome !== "incorrect") continue;
      const key = row.tag.areaOfStudy;
      const entry = byArea.get(key) ?? { topic: row.tag.areaOfStudy, correct: 0, incorrect: 0, total: 0 };
      entry.total += 1;
      if (row.outcome === "correct") entry.correct += 1;
      else entry.incorrect += 1;
      byArea.set(key, entry);
    }
    return Array.from(byArea.entries()).sort((a, b) => b[1].incorrect - a[1].incorrect);
  }, [rows]);

  if (!paper || !attempt) {
    return <div className="loading">Loading review…</div>;
  }

  const answerMap = new Map((answers ?? []).map((a) => [a.interactionId, a]));
  const sectionAScore = scoreSectionA(interactions, attempt.answers, answerMap);
  const sectionBSummary = summarizeSectionBAnswered(interactions, attempt.answers);
  const sectionBAssessed = rows.filter((r) => r.interaction.section === "B" && (r.outcome === "correct" || r.outcome === "incorrect")).length;

  const visibleRows = rows.filter((row) => {
    if (filter === "incorrect") return row.outcome === "incorrect";
    if (filter === "unanswered") return row.outcome === "unanswered";
    if (filter !== "all") return row.tag?.areaOfStudy === filter;
    return true;
  });

  const areaOptions = Array.from(new Set(rows.map((r) => r.tag?.areaOfStudy).filter(Boolean))) as string[];

  return (
    <div className="page">
      <h2>Review — {paper.title}</h2>
      <p className="page-intro">
        {attempt.mode === "timed" ? "Timed attempt" : "Practice attempt"} submitted{" "}
        {attempt.submittedAt ? new Date(attempt.submittedAt).toLocaleString() : ""}.
      </p>

      <div className="review-summary-grid">
        {paper.hasMultipleChoice && (
          <div className="card summary-card">
            <h3>Section A</h3>
            <p className="summary-big">
              {sectionAScore.correct} / {sectionAScore.total}
            </p>
            <p>
              {sectionAScore.answered} answered · {sectionAScore.incorrect} incorrect · {sectionAScore.unanswered} unanswered
            </p>
          </div>
        )}
        <div className="card summary-card">
          <h3>Section B</h3>
          <p className="summary-big">
            {sectionBSummary.answered} / {sectionBSummary.total} answered
          </p>
          <p>
            {paper.hasAnswerData
              ? `${sectionBAssessed} self-assessed against the official marking guide`
              : "Official marking guide not yet available for this paper"}
          </p>
        </div>
      </div>

      {areaBreakdown.length > 0 && (
        <section className="area-breakdown">
          <h3>Areas of Study — where errors occurred</h3>
          <ul>
            {areaBreakdown.map(([area, stats]) => (
              <li key={area}>
                <strong>{area}</strong>: {stats.correct} correct, {stats.incorrect} incorrect ({Math.round((stats.correct / stats.total) * 100)}%)
              </li>
            ))}
          </ul>
        </section>
      )}

      <div className="review-filters">
        {FILTERS.map((f) => (
          <button key={f.id} type="button" className={filter === f.id ? "filter-active" : "chip-toggle"} onClick={() => setFilter(f.id)}>
            {f.label}
          </button>
        ))}
        {areaOptions.map((area) => (
          <button key={area} type="button" className={filter === area ? "filter-active" : "chip-toggle"} onClick={() => setFilter(area)}>
            {area}
          </button>
        ))}
      </div>

      <div className="data-table-wrap">
        <table className="review-table">
          <thead>
            <tr>
              <th>Q</th>
              <th>Your answer</th>
              <th>Result</th>
              <th>Topic</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {visibleRows.map((row) => (
              <tr key={row.interaction.id} className={`review-row-${row.outcome}`}>
                <td>{row.interaction.question}</td>
                <td className="review-answer-cell">{row.studentAnswer || <em>—</em>}</td>
                <td>
                  <OutcomeLabel outcome={row.outcome} />
                  {row.interaction.section === "A" && row.answer && row.outcome !== "correct" && row.outcome !== "withdrawn" && (
                    <span className="review-correct-answer"> (correct: {acceptedAnswerLabel(row.answer)})</span>
                  )}
                </td>
                <td>{row.tag ? `${row.tag.topic}` : "—"}</td>
                <td>
                  {row.answer && (
                    <button
                      type="button"
                      className="btn btn-ghost btn-sm"
                      onClick={() => setExpanded(expanded === row.interaction.id ? null : row.interaction.id)}
                    >
                      {expanded === row.interaction.id ? "Hide" : "Details"}
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {visibleRows.map(
        (row) =>
          expanded === row.interaction.id &&
          row.answer && (
            <div className="review-detail card" key={`detail-${row.interaction.id}`}>
              <h4>Question {row.interaction.question}</h4>
              {row.interaction.section === "A" ? (
                row.answer.withdrawn ? (
                  <>
                    <p className="answer-verdict answer-verdict-withdrawn">Question withdrawn</p>
                    <p>
                      VCAA withdrew this question after the exam (e.g. a printing error or ambiguity) — it has no
                      correct answer and does not count toward your score, in either direction.
                    </p>
                    {row.answer.officialExplanation && <p>{row.answer.officialExplanation}</p>}
                  </>
                ) : (
                  <>
                    <p>
                      <strong>Correct answer:</strong> {acceptedAnswerLabel(row.answer)}
                    </p>
                    {row.answer.officialExplanation && <p>{row.answer.officialExplanation}</p>}
                  </>
                )
              ) : (
                <ContentBlocks blocks={row.answer.officialAnswer ?? []} />
              )}
            </div>
          )
      )}

      <p className="review-footer">
        <Link to="/papers">← Back to Past Papers</Link>
      </p>
    </div>
  );
}

function OutcomeLabel({ outcome }: { outcome: Outcome }) {
  const label =
    outcome === "correct"
      ? "Correct"
      : outcome === "incorrect"
        ? "Incorrect"
        : outcome === "unanswered"
          ? "Unanswered"
          : outcome === "withdrawn"
            ? "Withdrawn"
            : "Not self-assessed";
  return <span className={`outcome-pill outcome-${outcome}`}>{label}</span>;
}
