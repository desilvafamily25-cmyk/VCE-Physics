import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import type { Attempt, Paper, QuestionResult } from "../data/types";
import { repository } from "../data";
import { currentStreak, studyDaysFromHistory } from "../lib/streak";
import { ProgressRing } from "../components/ProgressRing";

type PaperWithAttempt = { paper: Paper; attempt: Attempt | null };

export function DashboardRoute() {
  const [papers, setPapers] = useState<PaperWithAttempt[] | null>(null);
  const [history, setHistory] = useState<QuestionResult[]>([]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const loadedPapers = await repository.getPapers();
      const withAttempts = await Promise.all(
        loadedPapers.map(async (paper) => ({ paper, attempt: await repository.getAttempt(paper.id) }))
      );
      const loadedHistory = await repository.getQuestionHistory();
      if (!cancelled) {
        setPapers(withAttempts);
        setHistory(loadedHistory);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const stats = useMemo(() => {
    const checked = history.length;
    const correct = history.filter((r) => r.outcome === "correct").length;
    const scored = history.filter((r) => r.outcome === "correct" || r.outcome === "incorrect" || r.outcome === "partially_correct");
    const accuracy = scored.length > 0 ? Math.round((correct / scored.length) * 100) : null;
    const studyDays = studyDaysFromHistory(history);
    const streak = currentStreak(studyDays);
    return { checked, accuracy, streak };
  }, [history]);

  const inProgress = useMemo(
    () => (papers ?? []).filter((p) => p.attempt && !p.attempt.submittedAt).sort((a, b) => (b.attempt!.lastSavedAt).localeCompare(a.attempt!.lastSavedAt)),
    [papers]
  );

  const completedCount = useMemo(() => (papers ?? []).filter((p) => p.attempt?.submittedAt).length, [papers]);
  const totalPapers = papers?.length ?? 0;
  const hasAnyActivity = history.length > 0 || (papers ?? []).some((p) => p.attempt);

  const recentActivity = useMemo(
    () => [...history].sort((a, b) => b.checkedAt.localeCompare(a.checkedAt)).slice(0, 6),
    [history]
  );

  const paperTitleByPaperId = useMemo(() => new Map((papers ?? []).map((p) => [p.paper.id, p.paper.title])), [papers]);

  if (!papers) {
    return <div className="loading">Loading your dashboard…</div>;
  }

  const recommendedPaper = papers.find((p) => p.paper.hasAnswerData)?.paper ?? papers[0]?.paper;

  return (
    <div className="page">
      {!hasAnyActivity ? (
        <div className="welcome-hero">
          <h1>Welcome to VCE Physics 50 👋</h1>
          <p>
            You're set up and ready to go. Attempt real VCAA past papers under exam-like conditions, get instant
            feedback with official examination-report answers, and track exactly which Areas of Study need more
            work.
          </p>
          <div className="welcome-hero-actions">
            {recommendedPaper && (
              <Link className="btn btn-accent" to={`/attempt/${recommendedPaper.id}/practice`}>
                Start with {recommendedPaper.title} — Practice Mode
              </Link>
            )}
            <Link className="btn btn-secondary" to="/papers">
              Browse all past papers
            </Link>
          </div>
        </div>
      ) : (
        <div className="welcome-hero">
          <h1>Welcome back 👋</h1>
          <p>Keep the momentum going — here's where you left off and how you're tracking overall.</p>
          <div className="welcome-hero-actions">
            <Link className="btn btn-accent" to="/papers">
              Browse past papers
            </Link>
            <Link className="btn btn-secondary" to="/progress">
              View full progress
            </Link>
          </div>
        </div>
      )}

      <div className="stat-strip">
        <div className="card stat-tile">
          <span className="stat-tile-value">
            {completedCount} / {totalPapers}
          </span>
          <span className="stat-tile-label">Papers completed</span>
        </div>
        <div className="card stat-tile">
          <span className="stat-tile-value">{stats.checked}</span>
          <span className="stat-tile-label">Questions checked</span>
        </div>
        <div className="card stat-tile">
          <span className="stat-tile-value">{stats.accuracy != null ? `${stats.accuracy}%` : "—"}</span>
          <span className="stat-tile-label">Accuracy so far</span>
        </div>
        <div className="card stat-tile">
          <span className="stat-tile-value streak-chip">🔥 {stats.streak} day{stats.streak === 1 ? "" : "s"}</span>
          <span className="stat-tile-label">Current streak</span>
        </div>
      </div>

      {inProgress.length > 0 && (
        <>
          <div className="section-heading">
            <h2>Continue where you left off</h2>
          </div>
          <div className="papers-grid">
            {inProgress.slice(0, 3).map(({ paper, attempt }) => (
              <div key={paper.id} className="card card-interactive paper-card">
                <div className="paper-card-top">
                  <div>
                    <p className="paper-card-title">{paper.title}</p>
                    <p className="paper-card-meta">
                      <span>{attempt!.mode === "timed" ? "Timed" : "Practice"} attempt</span>
                      <span>· started {new Date(attempt!.startedAt).toLocaleDateString()}</span>
                    </p>
                  </div>
                  <ProgressRing value={0.5} size={40} label="" />
                </div>
                <div className="paper-card-actions">
                  <Link className="btn btn-primary btn-sm" to={`/attempt/${paper.id}/${attempt!.mode}`}>
                    Resume
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {recentActivity.length > 0 && (
        <>
          <div className="section-heading">
            <h2>Recent activity</h2>
          </div>
          <div className="card" style={{ padding: "var(--space-2)" }}>
            <ul className="topic-progress-list" style={{ gridTemplateColumns: "1fr", gap: 0 }}>
              {recentActivity.map((result) => (
                <li key={result.id} style={{ border: "none", borderBottom: "1px solid var(--border)", borderRadius: 0, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span>
                    {paperTitleByPaperId.get(result.paperId) ?? result.paperId} · Q{result.interactionId}
                  </span>
                  <span className={`outcome-pill outcome-${result.outcome}`}>{result.outcome.replace("_", " ")}</span>
                </li>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  );
}
