import type { Attempt, Interaction, QuestionAnswer, QuestionOutcome } from "../data/types";

export function canonicalId(paperId: string, interactionId: string): string {
  return `${paperId}-${interactionId}`;
}

export function isMcqCorrect(studentAnswer: string, qa: QuestionAnswer): boolean {
  if (!studentAnswer) return false;
  // A withdrawn question has no correct answer -- never mark a real response
  // to it right or wrong (see types.ts QuestionAnswer.withdrawn and the
  // "withdrawn" QuestionOutcome).
  if (qa.withdrawn) return false;
  if (qa.allOptionsAccepted) return true;
  // acceptedAnswers is the source of truth (it covers the single-answer case
  // too) -- some questions have more than one accepted answer without every
  // option being accepted. Checking correctAnswer alone would mark that case
  // wrong.
  if (qa.acceptedAnswers && qa.acceptedAnswers.length > 0) {
    return qa.acceptedAnswers.includes(studentAnswer);
  }
  return studentAnswer === qa.correctAnswer;
}

export type SectionSummary = {
  total: number;
  answered: number;
  correct: number;
  incorrect: number;
  unanswered: number;
};

/**
 * Section A is always machine-gradeable, in both Timed and Practice modes.
 * Withdrawn questions (see QuestionAnswer.withdrawn) are excluded from the
 * total entirely -- matching how VCAA itself handles them, they don't count
 * for or against a student, so they must not appear as an unanswered/wrong
 * question dragging the score down.
 */
export function scoreSectionA(
  interactions: Interaction[],
  answers: Record<string, string>,
  answerMap: Map<string, QuestionAnswer>
): SectionSummary {
  const items = interactions.filter((item) => item.section === "A" && !answerMap.get(item.id)?.withdrawn);
  let correct = 0;
  let incorrect = 0;
  let answered = 0;

  for (const item of items) {
    const studentAnswer = (answers[item.id] ?? "").trim();
    if (!studentAnswer) continue;
    answered += 1;
    const qa = answerMap.get(item.id);
    if (qa) {
      if (isMcqCorrect(studentAnswer, qa)) correct += 1;
      else incorrect += 1;
    }
  }

  return {
    total: items.length,
    answered,
    correct,
    incorrect,
    unanswered: items.length - answered
  };
}

/**
 * Section B has no reliable autograder. "correct" / "incorrect" here reflect
 * the student's own self-assessment recorded via QuestionResult after
 * viewing the official answer -- never a fabricated automatic mark.
 */
export function summarizeSectionBAnswered(
  interactions: Interaction[],
  answers: Record<string, string>
): SectionSummary {
  const items = interactions.filter((item) => item.section === "B");
  const answered = items.filter((item) => (answers[item.id] ?? "").trim()).length;
  return { total: items.length, answered, correct: 0, incorrect: 0, unanswered: items.length - answered };
}

export function outcomeLabel(outcome: QuestionOutcome): string {
  switch (outcome) {
    case "correct":
      return "Correct";
    case "incorrect":
      return "Incorrect";
    case "partially_correct":
      return "Partially correct";
    case "withdrawn":
      return "Withdrawn";
    default:
      return "Unmarked";
  }
}

export function attemptAnsweredCount(interactions: Interaction[], attempt: Attempt): number {
  return interactions.filter((item) => (attempt.answers[item.id] ?? "").trim()).length;
}
