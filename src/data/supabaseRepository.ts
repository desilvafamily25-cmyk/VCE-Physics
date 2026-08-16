import { supabase } from "../lib/supabaseClient";
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

type AttemptRow = {
  paper_id: string;
  mode: AttemptMode;
  answers: Record<string, string>;
  checked: Record<string, boolean>;
  started_at: string;
  last_saved_at: string;
  submitted_at: string | null;
  writing_ends_at: string | null;
};

function rowToAttempt(row: AttemptRow): Attempt {
  return {
    paperId: row.paper_id,
    mode: row.mode,
    answers: row.answers ?? {},
    checked: row.checked ?? {},
    startedAt: row.started_at,
    lastSavedAt: row.last_saved_at,
    submittedAt: row.submitted_at ?? undefined,
    writingEndsAt: row.writing_ends_at ?? undefined
  };
}

async function currentUserId(): Promise<string> {
  const { data, error } = await supabase.auth.getUser();
  if (error || !data.user) {
    throw new Error("Not signed in -- SupabaseRepository requires an authenticated session.");
  }
  return data.user.id;
}

/**
 * Supabase-backed DataRepository -- one attempt row and an append-only
 * question_results history per (student, paper), scoped by Row Level
 * Security to auth.uid() (see supabase/schema.sql). Static content is
 * shared with LocalRepository via StaticContentSource; only the
 * per-student read/write methods differ. See docs/DATA-ARCHITECTURE.md.
 */
export class SupabaseRepository implements DataRepository {
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
    const userId = await currentUserId();
    const { data, error } = await supabase
      .from("attempts")
      .select("*")
      .eq("user_id", userId)
      .eq("paper_id", paperId)
      .maybeSingle();
    if (error) throw error;
    return data ? rowToAttempt(data as AttemptRow) : null;
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
    const userId = await currentUserId();
    const lastSavedAt = new Date().toISOString();
    const { error } = await supabase.from("attempts").upsert(
      {
        user_id: userId,
        paper_id: attempt.paperId,
        mode: attempt.mode,
        answers: attempt.answers,
        checked: attempt.checked ?? {},
        started_at: attempt.startedAt,
        last_saved_at: lastSavedAt,
        submitted_at: attempt.submittedAt ?? null,
        writing_ends_at: attempt.writingEndsAt ?? null
      },
      { onConflict: "user_id,paper_id" }
    );
    if (error) throw error;
  }

  async clearAttempt(paperId: string): Promise<void> {
    const userId = await currentUserId();
    const { error } = await supabase.from("attempts").delete().eq("user_id", userId).eq("paper_id", paperId);
    if (error) throw error;
  }

  async recordQuestionResult(result: QuestionResult): Promise<void> {
    const userId = await currentUserId();
    const { error } = await supabase.from("question_results").insert({
      user_id: userId,
      canonical_id: result.canonicalId,
      paper_id: result.paperId,
      interaction_id: result.interactionId,
      section: result.section,
      mode: result.mode,
      student_answer: result.studentAnswer,
      outcome: result.outcome,
      self_assessed: result.selfAssessed,
      checked_at: result.checkedAt
    });
    if (error) throw error;
  }

  async getQuestionHistory(paperId?: string): Promise<QuestionResult[]> {
    const userId = await currentUserId();
    let query = supabase.from("question_results").select("*").eq("user_id", userId);
    if (paperId) {
      query = query.eq("paper_id", paperId);
    }
    const { data, error } = await query;
    if (error) throw error;
    return (data ?? []).map((row) => ({
      id: row.id,
      canonicalId: row.canonical_id,
      paperId: row.paper_id,
      interactionId: row.interaction_id,
      section: row.section,
      mode: row.mode,
      studentAnswer: row.student_answer,
      outcome: row.outcome,
      selfAssessed: row.self_assessed,
      checkedAt: row.checked_at
    }));
  }
}

export const supabaseRepository = new SupabaseRepository();
