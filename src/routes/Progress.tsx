import { useEffect, useMemo, useState } from "react";
import type { Attempt, CurriculumTag, Paper, QuestionResult } from "../data/types";
import { repository } from "../data";
import { ProgressRing } from "../components/ProgressRing";
import { currentStreak, studyDaysFromHistory } from "../lib/streak";

const MIN_ATTEMPTS_FOR_TREND = 3;

type TopicStat = {
  areaOfStudy: string;
  topic: string;
  attempted: number;
  correct: number;
  incorrect: number;
};

export function ProgressRoute() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [attempts, setAttempts] = useState<Map<string, Attempt | null>>(new Map());
  const [topicStats, setTopicStats] = useState<TopicStat[] | null>(null);
  const [history, setHistory] = useState<QuestionResult[]>([]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const loadedPapers = await repository.getPapers();
      if (cancelled) return;
      setPapers(loadedPapers);

      const attemptEntries = await Promise.all(
        loadedPapers.map(async (p) => [p.id, await repository.getAttempt(p.id)] as const)
      );
      if (!cancelled) setAttempts(new Map(attemptEntries));

      const loadedHistory = await repository.getQuestionHistory();
      if (cancelled) return;
      setHistory(loadedHistory);

      // Topic stats only cover papers with a curriculum map.
      const curriculumMapped = loadedPapers.filter((p) => p.hasCurriculumMap);
      const curriculumByPaper = new Map<string, CurriculumTag[]>();
      await Promise.all(
        curriculumMapped.map(async (p) => {
          curriculumByPaper.set(p.id, (await repository.getCurriculumMap(p)) ?? []);
        })
      );

      const byTopic = new Map<string, TopicStat>();
      for (const result of loadedHistory) {
        if (result.outcome === "withdrawn") continue;
        const tags = curriculumByPaper.get(result.paperId);
        const tag = tags?.find((t) => t.interactionId === result.interactionId);
        if (!tag) continue;
        const key = `${tag.areaOfStudy}::${tag.topic}`;
        const entry = byTopic.get(key) ?? { areaOfStudy: tag.areaOfStudy, topic: tag.topic, attempted: 0, correct: 0, incorrect: 0 };
        entry.attempted += 1;
        if (result.outcome === "correct") entry.correct += 1;
        else if (result.outcome === "incorrect" || result.outcome === "partially_correct") entry.incorrect += 1;
        byTopic.set(key, entry);
      }
      if (!cancelled) setTopicStats(Array.from(byTopic.values()));
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const paperCounts = useMemo(() => {
    let notStarted = 0;
    let inProgress = 0;
    let completed = 0;
    for (const paper of papers) {
      const attempt = attempts.get(paper.id);
      if (!attempt) notStarted += 1;
      else if (attempt.submittedAt) completed += 1;
      else inProgress += 1;
    }
    return { total: papers.length, notStarted, inProgress, completed };
  }, [papers, attempts]);

  const scored = useMemo(
    () => history.filter((r) => r.outcome === "correct" || r.outcome === "incorrect" || r.outcome === "partially_correct"),
    [history]
  );
  const totalCorrect = scored.filter((r) => r.outcome === "correct").length;
  const accuracy = scored.length > 0 ? totalCorrect / scored.length : 0;
  const streak = useMemo(() => currentStreak(studyDaysFromHistory(history)), [history]);

  const rankedTopics = useMemo(() => {
    if (!topicStats) return [];
    return [...topicStats]
      .filter((t) => t.attempted >= MIN_ATTEMPTS_FOR_TREND)
      .map((t) => ({ ...t, accuracy: t.correct / t.attempted }))
      .sort((a, b) => a.accuracy - b.accuracy);
  }, [topicStats]);

  const belowMinimum = useMemo(() => (topicStats ?? []).filter((t) => t.attempted < MIN_ATTEMPTS_FOR_TREND), [topicStats]);

  return (
    <div className="page">
      <h2>Progress</h2>

      <div className="review-summary-grid">
        <div className="card summary-card" style={{ display: "flex", alignItems: "center", gap: "var(--space-4)" }}>
          <ProgressRing value={paperCounts.total > 0 ? paperCounts.completed / paperCounts.total : 0} size={64} />
          <div>
            <h3>Past Papers</h3>
            <p style={{ margin: 0, fontSize: "var(--text-sm)" }}>
              {paperCounts.completed} completed · {paperCounts.inProgress} in progress · {paperCounts.notStarted} not started
            </p>
          </div>
        </div>
        <div className="card summary-card" style={{ display: "flex", alignItems: "center", gap: "var(--space-4)" }}>
          <ProgressRing value={accuracy} size={64} />
          <div>
            <h3>Accuracy</h3>
            <p style={{ margin: 0, fontSize: "var(--text-sm)" }}>{scored.length} questions checked overall</p>
          </div>
        </div>
        <div className="card summary-card">
          <h3>Study streak</h3>
          <p className="summary-big streak-chip">🔥 {streak} day{streak === 1 ? "" : "s"}</p>
        </div>
      </div>

      {rankedTopics.length > 0 && (
        <section>
          <h3>Areas for Improvement</h3>
          <p className="page-intro">
            Ranked from weakest to strongest, based on topics with at least {MIN_ATTEMPTS_FOR_TREND} checked questions.
          </p>
          <ul className="topic-progress-list">
            {rankedTopics.map((t) => (
              <li key={`${t.areaOfStudy}::${t.topic}`} style={{ display: "flex", alignItems: "center", gap: "var(--space-3)" }}>
                <ProgressRing value={t.accuracy} size={40} />
                <div>
                  <strong>{t.topic}</strong> ({t.areaOfStudy})
                  <br />
                  {t.attempted} attempted · {t.correct} correct · {t.incorrect} incorrect
                </div>
              </li>
            ))}
          </ul>
        </section>
      )}

      {belowMinimum.length > 0 && (
        <section>
          <h3>Not enough data yet</h3>
          <p className="page-intro">
            These topics have fewer than {MIN_ATTEMPTS_FOR_TREND} checked questions — too little to call a trend yet:{" "}
            {belowMinimum.map((t) => t.topic).join(", ")}.
          </p>
        </section>
      )}

      {topicStats && topicStats.length === 0 && (
        <p>No topic-tagged questions have been checked yet — try Practice by Topic or Practice Mode.</p>
      )}
    </div>
  );
}
