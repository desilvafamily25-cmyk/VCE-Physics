// Core data model. See docs/DATA-ARCHITECTURE.md for the entity overview and
// the Supabase-backed storage plan. Every UI module should import types from
// here rather than redeclaring shapes locally.
//
// Deliberate difference from the VCE Chemistry app this was modelled on:
// "withdrawn" is a first-class QuestionOutcome from day one (see
// QuestionOutcome below and QuestionAnswer.withdrawn), not retrofitted later.

export type Rect = {
  x: number;
  y: number;
  width: number;
  height: number;
};

export type InteractionType = "mcq" | "text" | "drawing";

export type Interaction = {
  id: string;
  section: "A" | "B";
  question: string;
  page: number;
  type: InteractionType;
  marks?: number;
  rect: Rect;
  note?: string;
};

export type Paper = {
  id: string;
  title: string;
  era: "current" | "previous" | "archive";
  pdfUrl: string;
  interactionsUrl: string;
  formulaSheetUrl?: string;
  storageKey: string;
  sectionATotal: number;
  totalMarks: number;
  source: string;
  pageCount: number;
  interactionCount: number;
  readingMinutes: number;
  writingMinutes: number;
  durationSource: string;
  hasAnswerData: boolean;
  hasCurriculumMap: boolean;
  // Archive-era papers (2002-2016) have no Section A/MCQ at all and use an
  // elective Detailed Study structure that doesn't map cleanly onto the
  // current curriculum -- see docs/DATA-ARCHITECTURE.md. Timed/Practice
  // still work; Topic Practice and curriculum tagging never apply to them.
  hasMultipleChoice: boolean;
};

// ---- Answer / solution dataset (data/answers/<paperId>.json) ----

export type AnswerContentBlock =
  | { type: "markingPoint" | "examinerComment" | "note"; level: number; text: string }
  | { type: "table"; rows: string[][] };

export type QuestionAnswer = {
  interactionId: string;
  canonicalId: string;
  section: "A" | "B";
  questionLabel: string;
  marks: number | null;

  // Section A only
  correctAnswer?: string | null;
  acceptedAnswers?: string[];
  allOptionsAccepted?: boolean;
  // VCAA occasionally withdraws a question after the exam (printing error,
  // ambiguity, etc.) -- when true, this question has no correct answer and
  // must never be scored against a student, in either direction. See
  // QuestionOutcome's "withdrawn" value and report_extraction_lib.py's
  // WITHDRAWN_RE for how this is detected.
  withdrawn?: boolean;
  cohortPercentCorrect?: number | null;
  optionPercents?: Record<string, number>;
  officialExplanation?: string;

  // Section B only
  marksDistributionPct?: Record<string, number>;
  averageMark?: number | null;
  officialAnswer?: AnswerContentBlock[];

  examinerComments: AnswerContentBlock[];
  source: { document: string; location: string };
  uncertain: boolean;
  uncertainReason: string;
  difficulty: {
    level: "Easy" | "Medium" | "Hard" | "Very Hard" | "unknown";
    ratio: number | null;
    source: string;
    rule: string;
  };
};

// ---- Curriculum mapping (data/curriculum/<paperId>-mapping.json) ----

export type CurriculumTag = {
  canonicalId: string;
  interactionId: string;
  unit: string;
  areaOfStudy: string;
  topic: string;
  skills: string[];
  confidence: "high" | "medium" | "low";
  uncertain: boolean;
  note?: string;
};

export type SharedStimulusGroup = {
  interactionIds: string[];
  pages: number[];
  stimulus: string;
};

// ---- Attempts ----

export type AttemptMode = "timed" | "practice";

export type Attempt = {
  paperId: string;
  mode: AttemptMode;
  answers: Record<string, string>;
  startedAt: string;
  lastSavedAt: string;
  submittedAt?: string;
  // Timed mode only -- an absolute wall-clock deadline, so a page refresh
  // recomputes remaining time instead of relying on an in-memory counter.
  // No separate Reading Time lock -- writing time starts immediately.
  writingEndsAt?: string;
  // Practice mode only -- which questions the student has explicitly
  // "checked" (revealing correctness/official answer).
  checked?: Record<string, boolean>;
};

// ---- Question-level results (feeds Error Bank + Progress) ----

// "withdrawn" is a first-class outcome (not folded into "unknown" or
// "incorrect"): a VCAA-withdrawn question is recorded so it still shows up
// in review history with its own distinct treatment, but is excluded from
// every score/accuracy calculation in both directions -- see
// src/lib/scoring.ts and docs/DATA-ARCHITECTURE.md.
export type QuestionOutcome = "correct" | "incorrect" | "partially_correct" | "withdrawn" | "unknown";

export type QuestionResult = {
  id: string; // unique per check event
  canonicalId: string;
  paperId: string;
  interactionId: string;
  section: "A" | "B";
  mode: AttemptMode;
  studentAnswer: string;
  outcome: QuestionOutcome;
  selfAssessed: boolean; // true for Section B (no reliable autograder)
  checkedAt: string;
};

export type ErrorRecord = {
  canonicalId: string;
  paperId: string;
  interactionId: string;
  section: "A" | "B";
  timesAttempted: number;
  timesIncorrect: number;
  latestOutcome: QuestionOutcome;
  latestStudentAnswer: string;
  latestCheckedAt: string;
  mastered: boolean; // most recent result is correct after at least one prior miss
};
