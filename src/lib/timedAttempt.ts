import type { Attempt } from "../data/types";

export type TimedPhase = "writing" | "expired";

export type TimedStatus = {
  phase: TimedPhase;
  msRemaining: number;
};

/**
 * Recomputes the current phase/remaining time from the attempt's absolute
 * wall-clock writing deadline rather than an in-memory counter, so a page
 * refresh mid-exam still shows the correct remaining time.
 *
 * There is no separate Reading Time lock -- answers are enterable from the
 * moment a Timed attempt starts. (VCAA's real papers include reading time --
 * 15 minutes for every era covered here -- but this practice tool
 * intentionally skips it; see docs/DATA-ARCHITECTURE.md.)
 */
export function getTimedStatus(attempt: Attempt, now: Date = new Date()): TimedStatus {
  if (!attempt.writingEndsAt) {
    return { phase: "expired", msRemaining: 0 };
  }

  const nowMs = now.getTime();
  const writingEndsMs = new Date(attempt.writingEndsAt).getTime();

  if (nowMs < writingEndsMs) {
    return { phase: "writing", msRemaining: writingEndsMs - nowMs };
  }
  return { phase: "expired", msRemaining: 0 };
}

export function formatDuration(ms: number): string {
  const totalSeconds = Math.max(0, Math.floor(ms / 1000));
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  const pad = (value: number) => value.toString().padStart(2, "0");
  return hours > 0 ? `${hours}:${pad(minutes)}:${pad(seconds)}` : `${minutes}:${pad(seconds)}`;
}
