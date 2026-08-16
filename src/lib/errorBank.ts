import type { ErrorRecord, QuestionResult } from "../data/types";

/**
 * Derives Error Bank records from the full QuestionResult history. There is
 * deliberately no separate "errors" store -- whether a question is still an
 * error is always recomputed from its most recent result, so a later correct
 * attempt automatically resolves/masters it without a second write path.
 *
 * A "withdrawn" result never counts toward timesIncorrect and is never
 * treated as unresolved -- VCAA withdrawing a question is not the student
 * getting it wrong.
 */
export function buildErrorRecords(history: QuestionResult[]): ErrorRecord[] {
  const byQuestion = new Map<string, QuestionResult[]>();
  for (const result of history) {
    if (result.outcome === "withdrawn") continue;
    const list = byQuestion.get(result.canonicalId) ?? [];
    list.push(result);
    byQuestion.set(result.canonicalId, list);
  }

  const records: ErrorRecord[] = [];
  for (const [canonicalId, results] of byQuestion) {
    const sorted = [...results].sort((a, b) => a.checkedAt.localeCompare(b.checkedAt));
    const latest = sorted[sorted.length - 1];
    const timesIncorrect = sorted.filter(
      (r) => r.outcome === "incorrect" || r.outcome === "partially_correct"
    ).length;

    if (timesIncorrect === 0) continue; // never got this wrong -- not an error record

    records.push({
      canonicalId,
      paperId: latest.paperId,
      interactionId: latest.interactionId,
      section: latest.section,
      timesAttempted: sorted.length,
      timesIncorrect,
      latestOutcome: latest.outcome,
      latestStudentAnswer: latest.studentAnswer,
      latestCheckedAt: latest.checkedAt,
      mastered: latest.outcome === "correct"
    });
  }

  return records.sort((a, b) => b.latestCheckedAt.localeCompare(a.latestCheckedAt));
}

export function unresolvedErrors(records: ErrorRecord[]): ErrorRecord[] {
  return records.filter((record) => !record.mastered);
}
