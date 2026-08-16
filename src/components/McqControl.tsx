import type { Interaction, QuestionAnswer } from "../data/types";
import type { PageSize } from "./PdfOverlay";
import { isMcqCorrect } from "../lib/scoring";

const OPTIONS = ["A", "B", "C", "D"];

/**
 * Section A control. In timed/read-only modes it is just the original A-D
 * picker. In practice mode, selecting a letter reveals a small "Check"
 * chip -- the answer is never marked correct/incorrect until the student
 * explicitly checks it. Once checked, the buttons themselves get a
 * correct/incorrect styling hint; the full explanation lives in the docked
 * AnswerPanel, not squeezed into this small on-page control.
 */
export function McqControl({
  interaction,
  answer,
  onAnswer,
  pageSize,
  mode,
  locked,
  checked,
  onCheck,
  questionAnswer
}: {
  interaction: Interaction;
  answer: string;
  onAnswer: (id: string, value: string) => void;
  pageSize: PageSize;
  mode: "timed" | "practice" | "readonly";
  locked: boolean;
  checked: boolean;
  onCheck?: (id: string) => void;
  questionAnswer?: QuestionAnswer;
}) {
  const style = {
    left: `${interaction.rect.x * pageSize.width}px`,
    top: `${interaction.rect.y * pageSize.height}px`,
    width: `${interaction.rect.width * pageSize.width}px`,
    height: `${interaction.rect.height * pageSize.height}px`
  };

  const showCheckChip = mode === "practice" && !checked && !!answer && !!onCheck;
  const revealed = mode === "practice" && checked;

  return (
    <>
      <div className="mcq-control" style={style} aria-label={`Question ${interaction.question}`}>
        {OPTIONS.map((choice) => {
          let stateClass = "";
          if (revealed && questionAnswer && !questionAnswer.withdrawn) {
            const isCorrectOption =
              questionAnswer.allOptionsAccepted ||
              (questionAnswer.acceptedAnswers ?? []).includes(choice) ||
              choice === questionAnswer.correctAnswer;
            if (isCorrectOption) stateClass = "mcq-correct";
            else if (choice === answer) stateClass = "mcq-incorrect";
          }
          return (
            <button
              key={choice}
              type="button"
              disabled={locked}
              className={[answer === choice ? "selected" : "", stateClass].filter(Boolean).join(" ")}
              onClick={() => !locked && onAnswer(interaction.id, choice)}
            >
              {choice}
            </button>
          );
        })}
      </div>
      {showCheckChip && (
        <button
          type="button"
          className="check-chip"
          style={{
            left: `${interaction.rect.x * pageSize.width}px`,
            top: `${(interaction.rect.y + interaction.rect.height) * pageSize.height + 4}px`
          }}
          onClick={() => onCheck?.(interaction.id)}
        >
          Check
        </button>
      )}
      {revealed && questionAnswer?.withdrawn && (
        <span
          className="result-chip result-withdrawn"
          style={{
            left: `${interaction.rect.x * pageSize.width}px`,
            top: `${(interaction.rect.y + interaction.rect.height) * pageSize.height + 4}px`
          }}
        >
          Withdrawn
        </span>
      )}
      {revealed && questionAnswer && !questionAnswer.withdrawn && (
        <span
          className={["result-chip", answer && isMcqCorrect(answer, questionAnswer) ? "result-correct" : "result-incorrect"].join(" ")}
          style={{
            left: `${interaction.rect.x * pageSize.width}px`,
            top: `${(interaction.rect.y + interaction.rect.height) * pageSize.height + 4}px`
          }}
        >
          {answer && isMcqCorrect(answer, questionAnswer) ? "Correct" : "Incorrect"}
        </span>
      )}
    </>
  );
}
