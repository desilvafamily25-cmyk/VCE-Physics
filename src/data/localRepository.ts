import type { DataRepository } from "./repository";
import { StaticContentSource } from "./staticContent";
import type {
  Attempt,
  AttemptMode,
  CurriculumTag,
  Interaction,
  Paper,
  QuestionAnswer,
  QuestionResult,
  SharedStimulusGroup
} from "./types";

const VERSION = "v1";
const attemptKey = (paperId: string) => `vce-physics.repo.${VERSION}.attempt.${paperId}`;
const resultsKey = (paperId: string) => `vce-physics.repo.${VERSION}.results.${paperId}`;
const RESULTS_INDEX_KEY = `vce-physics.repo.${VERSION}.results-index`;

/**
 * localStorage-backed DataRepository -- used when no student is signed in
 * (or as the source of "local progress" that gets migrated into Supabase on
 * first sign-in, see src/lib/migrateLocalProgress.ts). Static content
 * (papers/interactions/answers/curriculum) is shared with SupabaseRepository
 * via StaticContentSource; only the per-student read/write methods differ.
 * See docs/DATA-ARCHITECTURE.md.
 */
export class LocalRepository implements DataRepository {
  private static_ = new StaticContentSource();

  async getPapers(): Promise<Paper[]> {
    return this.static_.getPapers();
  }

  async getInteractions(paper: Paper): Promise<Interaction[]> {
    return this.static_.getInteractions(paper);
  }

  async getAnswers(paper: Paper): Promise<QuestionAnswer[] | null> {
    return this.static_.getAnswers(paper);
  }

  async getCurriculumMap(paper: Paper): Promise<CurriculumTag[] | null> {
    return this.static_.getCurriculumMap(paper);
  }

  async getSharedStimulusGroups(paper: Paper): Promise<SharedStimulusGroup[]> {
    return this.static_.getSharedStimulusGroups(paper);
  }

  async getAttempt(paperId: string): Promise<Attempt | null> {
    const raw = localStorage.getItem(attemptKey(paperId));
    if (raw) {
      try {
        return JSON.parse(raw) as Attempt;
      } catch {
        return null;
      }
    }
    return null;
  }

  async startAttempt(paper: Paper, mode: AttemptMode): Promise<Attempt> {
    const now = new Date();
    const nowIso = now.toISOString();
    const attempt: Attempt = {
      paperId: paper.id,
      mode,
      answers: {},
      startedAt: nowIso,
      lastSavedAt: nowIso,
      checked: {}
    };

    if (mode === "timed") {
      // No Reading Time lock -- writing time (and the countdown) starts
      // immediately when the attempt is created.
      const writingEnds = new Date(now.getTime() + paper.writingMinutes * 60_000);
      attempt.writingEndsAt = writingEnds.toISOString();
    }

    await this.saveAttempt(attempt);
    return attempt;
  }

  async saveAttempt(attempt: Attempt): Promise<void> {
    const withTimestamp: Attempt = { ...attempt, lastSavedAt: new Date().toISOString() };
    localStorage.setItem(attemptKey(attempt.paperId), JSON.stringify(withTimestamp));
  }

  async clearAttempt(paperId: string): Promise<void> {
    localStorage.removeItem(attemptKey(paperId));
  }

  async recordQuestionResult(result: QuestionResult): Promise<void> {
    const key = resultsKey(result.paperId);
    const existingRaw = localStorage.getItem(key);
    const existing: QuestionResult[] = existingRaw ? JSON.parse(existingRaw) : [];
    existing.push(result);
    localStorage.setItem(key, JSON.stringify(existing));

    const indexRaw = localStorage.getItem(RESULTS_INDEX_KEY);
    const index: string[] = indexRaw ? JSON.parse(indexRaw) : [];
    if (!index.includes(result.paperId)) {
      index.push(result.paperId);
      localStorage.setItem(RESULTS_INDEX_KEY, JSON.stringify(index));
    }
  }

  async getQuestionHistory(paperId?: string): Promise<QuestionResult[]> {
    if (paperId) {
      const raw = localStorage.getItem(resultsKey(paperId));
      return raw ? (JSON.parse(raw) as QuestionResult[]) : [];
    }

    const indexRaw = localStorage.getItem(RESULTS_INDEX_KEY);
    const index: string[] = indexRaw ? JSON.parse(indexRaw) : [];
    const all: QuestionResult[] = [];
    for (const id of index) {
      const raw = localStorage.getItem(resultsKey(id));
      if (raw) all.push(...(JSON.parse(raw) as QuestionResult[]));
    }
    return all;
  }
}

export const localRepository = new LocalRepository();
