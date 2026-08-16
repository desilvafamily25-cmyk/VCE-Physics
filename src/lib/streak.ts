import type { QuestionResult } from "../data/types";

/**
 * Real-data-only streak/activity computation -- never fabricated (per the
 * build brief: "must never fabricate scores or hide real performance").
 * A "study day" is any local calendar date on which at least one question
 * was checked/self-assessed. The current streak counts consecutive study
 * days ending today or yesterday (so it doesn't reset to 0 the instant a
 * student hasn't opened the app yet today).
 */
export function studyDaysFromHistory(history: QuestionResult[]): Set<string> {
  const days = new Set<string>();
  for (const result of history) {
    const date = new Date(result.checkedAt);
    if (Number.isNaN(date.getTime())) continue;
    days.add(localDateKey(date));
  }
  return days;
}

export function localDateKey(date: Date): string {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

export function currentStreak(studyDays: Set<string>, today: Date = new Date()): number {
  if (studyDays.size === 0) return 0;

  const todayKey = localDateKey(today);
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  const yesterdayKey = localDateKey(yesterday);

  let cursor: Date;
  if (studyDays.has(todayKey)) {
    cursor = today;
  } else if (studyDays.has(yesterdayKey)) {
    cursor = yesterday;
  } else {
    return 0;
  }

  let streak = 0;
  while (studyDays.has(localDateKey(cursor))) {
    streak += 1;
    cursor = new Date(cursor);
    cursor.setDate(cursor.getDate() - 1);
  }
  return streak;
}
