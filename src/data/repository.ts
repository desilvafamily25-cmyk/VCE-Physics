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

/**
 * Every piece of UI in this app reads/writes student data through this
 * interface, never through localStorage or the Supabase client directly.
 * LocalRepository and SupabaseRepository both implement this exact shape --
 * see docs/DATA-ARCHITECTURE.md.
 */
export interface DataRepository {
  getPapers(): Promise<Paper[]>;
  getInteractions(paper: Paper): Promise<Interaction[]>;
  getAnswers(paper: Paper): Promise<QuestionAnswer[] | null>;
  getCurriculumMap(paper: Paper): Promise<CurriculumTag[] | null>;
  getSharedStimulusGroups(paper: Paper): Promise<SharedStimulusGroup[]>;

  getAttempt(paperId: string): Promise<Attempt | null>;
  startAttempt(paper: Paper, mode: AttemptMode): Promise<Attempt>;
  saveAttempt(attempt: Attempt): Promise<void>;
  clearAttempt(paperId: string): Promise<void>;

  recordQuestionResult(result: QuestionResult): Promise<void>;
  getQuestionHistory(paperId?: string): Promise<QuestionResult[]>;
}
