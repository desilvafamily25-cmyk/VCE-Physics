import type { AnswerContentBlock, Interaction, QuestionAnswer, QuestionOutcome } from "../data/types";
import { isMcqCorrect } from "../lib/scoring";

/**
 * Docked panel (not part of the absolutely-positioned PDF layer) showing the
 * official answer/marking guide for whichever question was just checked. Kept
 * separate from the on-page control so arbitrarily long official text never
 * has to be squeezed into a small exam-page rectangle or overlap neighbouring
 * questions.
 */
export function AnswerPanel({
  interaction,
  studentAnswer,
  questionAnswer,
  onSelfAssess,
  onClose
}: {
  interaction: Interaction;
  studentAnswer: string;
  questionAnswer: QuestionAnswer | null;
  onSelfAssess?: (outcome: QuestionOutcome) => void;
  onClose: () => void;
}) {
  return (
    <aside className="answer-panel card" aria-live="polite">
      <div className="answer-panel-header">
        <strong>
          Question {interaction.question} {questionAnswer?.marks != null ? `(${questionAnswer.marks} mark${questionAnswer.marks === 1 ? "" : "s"})` : ""}
        </strong>
        <button type="button" className="btn btn-ghost btn-icon answer-panel-close" onClick={onClose} aria-label="Close answer panel">
          ✕
        </button>
      </div>

      {!questionAnswer && (
        <p className="answer-panel-missing">Official answer not yet available for this paper.</p>
      )}

      {questionAnswer && interaction.section === "A" && (
        <SectionAAnswer studentAnswer={studentAnswer} questionAnswer={questionAnswer} />
      )}

      {questionAnswer && interaction.section === "B" && (
        <SectionBAnswer questionAnswer={questionAnswer} onSelfAssess={onSelfAssess} />
      )}
    </aside>
  );
}

/** Derives the exam year from the answer's own source document name (e.g.
 * "VCE_Physics_2025_Examination_Report.docx" -> "2025") rather than
 * hardcoding a year, since this panel is shared across every paper. */
function cohortLabel(questionAnswer: QuestionAnswer): string {
  const match = questionAnswer.source.document.match(/(\d{4})/);
  return match ? `${match[1]} cohort` : "cohort";
}

/** Renders "B", or "A or D (2 answers accepted after review)", or
 * "A, B, C or D (all accepted)" depending on how many answers the report
 * accepted for this question. */
export function acceptedAnswerLabel(questionAnswer: QuestionAnswer): string {
  const accepted = questionAnswer.acceptedAnswers ?? [];
  if (questionAnswer.allOptionsAccepted) return "A, B, C or D (all accepted)";
  if (accepted.length === 0) return questionAnswer.correctAnswer ?? "unknown";
  if (accepted.length === 1) return accepted[0];
  return `${accepted.join(" or ")} (${accepted.length} answers accepted after review)`;
}

function SectionAAnswer({ studentAnswer, questionAnswer }: { studentAnswer: string; questionAnswer: QuestionAnswer }) {
  if (questionAnswer.withdrawn) {
    return (
      <div>
        <p className="answer-verdict answer-verdict-withdrawn">Question withdrawn</p>
        <p className="answer-panel-note">
          VCAA withdrew this question after the exam (e.g. a printing error or ambiguity) — it has no correct answer
          and does not count toward your score, in either direction.
        </p>
        {questionAnswer.officialExplanation && (
          <div className="answer-explanation">
            {questionAnswer.officialExplanation.split("\n").map((line, index) => (
              <p key={index}>{line}</p>
            ))}
          </div>
        )}
        <SourceNote questionAnswer={questionAnswer} />
      </div>
    );
  }

  const correct = isMcqCorrect(studentAnswer, questionAnswer);
  return (
    <div>
      <p className={correct ? "answer-verdict answer-verdict-correct" : "answer-verdict answer-verdict-incorrect"}>
        {correct ? "Correct" : `Incorrect — your answer: ${studentAnswer || "(none)"}`}
      </p>
      <p>
        <strong>{questionAnswer.acceptedAnswers && questionAnswer.acceptedAnswers.length > 1 ? "Accepted answers:" : "Correct answer:"}</strong>{" "}
        {acceptedAnswerLabel(questionAnswer)}
      </p>
      {questionAnswer.cohortPercentCorrect != null && (
        <p className="answer-cohort-stat">{questionAnswer.cohortPercentCorrect}% of the {cohortLabel(questionAnswer)} answered this correctly.</p>
      )}
      {questionAnswer.officialExplanation && (
        <div className="answer-explanation">
          {questionAnswer.officialExplanation.split("\n").map((line, index) => (
            <p key={index}>{line}</p>
          ))}
        </div>
      )}
      <SourceNote questionAnswer={questionAnswer} />
    </div>
  );
}

function SectionBAnswer({
  questionAnswer,
  onSelfAssess
}: {
  questionAnswer: QuestionAnswer;
  onSelfAssess?: (outcome: QuestionOutcome) => void;
}) {
  if (questionAnswer.withdrawn) {
    return (
      <div>
        <p className="answer-verdict answer-verdict-withdrawn">Question withdrawn</p>
        <p className="answer-panel-note">
          VCAA withdrew this question after the exam — it has no official marking guide and does not count toward
          your score, in either direction.
        </p>
        <SourceNote questionAnswer={questionAnswer} />
      </div>
    );
  }

  return (
    <div>
      <p className="answer-panel-note">
        Written responses can't be auto-marked reliably. Compare your answer with the official marking guide below,
        then record how you think you went.
      </p>
      {questionAnswer.marksDistributionPct && Object.keys(questionAnswer.marksDistributionPct).length > 0 && (
        <p className="answer-cohort-stat">
          {cohortLabel(questionAnswer)} average: {questionAnswer.averageMark ?? "?"} / {questionAnswer.marks}
        </p>
      )}

      <h4>Official answer / marking guide</h4>
      <ContentBlocks blocks={questionAnswer.officialAnswer ?? []} />

      {questionAnswer.examinerComments.length > 0 && (
        <>
          <h4>Examiner comments</h4>
          <ContentBlocks blocks={questionAnswer.examinerComments} />
        </>
      )}

      <SourceNote questionAnswer={questionAnswer} />

      {onSelfAssess && (
        <div className="self-assess">
          <p>How did you go?</p>
          <div className="self-assess-buttons">
            <button type="button" onClick={() => onSelfAssess("correct")}>
              Correct
            </button>
            <button type="button" onClick={() => onSelfAssess("partially_correct")}>
              Partially correct
            </button>
            <button type="button" onClick={() => onSelfAssess("incorrect")}>
              Incorrect
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export function ContentBlocks({ blocks }: { blocks: AnswerContentBlock[] }) {
  return (
    <div className="answer-blocks">
      {blocks.map((block, index) => {
        if (block.type === "table") {
          return (
            <table key={index} className="answer-table">
              <tbody>
                {block.rows.map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    {row.map((cell, cellIndex) => (
                      <td key={cellIndex}>{cell}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          );
        }
        const className = ["answer-block", `answer-block-${block.type}`, block.level > 0 ? `answer-block-indent-${block.level}` : ""]
          .filter(Boolean)
          .join(" ");
        return (
          <p key={index} className={className}>
            {block.level > 0 ? "• " : ""}
            {block.text}
          </p>
        );
      })}
    </div>
  );
}

function SourceNote({ questionAnswer }: { questionAnswer: QuestionAnswer }) {
  return (
    <p className="answer-source">
      Source: {questionAnswer.source.document} — {questionAnswer.source.location}
      {questionAnswer.uncertain ? ` (flagged for review: ${questionAnswer.uncertainReason})` : ""}
    </p>
  );
}
