import { localRepository } from "../data/localRepository";
import { supabaseRepository } from "../data/supabaseRepository";

// One-time migration: the very first time a student signs in on a browser
// that already has localStorage progress (from before they had an account),
// copy it into their new Supabase account so nothing is silently lost.
// Guarded by a per-user flag in localStorage so it never re-runs (and never
// re-imports stale data after the student has gone on to make further
// progress in their account).
const MIGRATION_FLAG_PREFIX = "vce-physics.repo.v1.migrated.";

export async function migrateLocalProgressIfNeeded(userId: string): Promise<void> {
  const flagKey = `${MIGRATION_FLAG_PREFIX}${userId}`;
  if (localStorage.getItem(flagKey)) return;

  try {
    const papers = await localRepository.getPapers();
    let migratedAnything = false;

    for (const paper of papers) {
      const attempt = await localRepository.getAttempt(paper.id);
      if (!attempt) continue;

      // Don't clobber progress already made in the Supabase account (e.g. the
      // student signed in on a second device first).
      const existing = await supabaseRepository.getAttempt(paper.id);
      if (!existing) {
        await supabaseRepository.saveAttempt(attempt);
        migratedAnything = true;
      }

      const history = await localRepository.getQuestionHistory(paper.id);
      if (history.length > 0) {
        const existingHistory = await supabaseRepository.getQuestionHistory(paper.id);
        const existingKeys = new Set(existingHistory.map((r) => `${r.interactionId}.${r.checkedAt}`));
        for (const result of history) {
          const key = `${result.interactionId}.${result.checkedAt}`;
          if (!existingKeys.has(key)) {
            await supabaseRepository.recordQuestionResult(result);
            migratedAnything = true;
          }
        }
      }
    }

    if (migratedAnything) {
      // eslint-disable-next-line no-console
      console.info("Migrated local progress into your account.");
    }
  } catch (err) {
    // Never block sign-in on a migration failure -- surface it quietly and
    // let the student keep using their (now-authoritative) Supabase account.
    // eslint-disable-next-line no-console
    console.error("Local progress migration failed:", err);
  } finally {
    localStorage.setItem(flagKey, new Date().toISOString());
  }
}
