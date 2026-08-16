import type { Interaction } from "../data/types";
import type { PageSize } from "./PdfOverlay";

/**
 * Section B control. A "Check / Show Answer" chip appears in practice mode
 * once the student has typed something and hasn't checked yet -- clicking it
 * opens the docked AnswerPanel with the official answer/marking guide,
 * rather than pretending the free-text response has been auto-marked.
 */
export function WrittenControl({
  interaction,
  answer,
  onAnswer,
  pageSize,
  mode,
  locked,
  checked,
  onCheck
}: {
  interaction: Interaction;
  answer: string;
  onAnswer: (id: string, value: string) => void;
  pageSize: PageSize;
  mode: "timed" | "practice" | "readonly";
  locked: boolean;
  checked: boolean;
  onCheck?: (id: string) => void;
}) {
  const style = {
    left: `${interaction.rect.x * pageSize.width}px`,
    top: `${interaction.rect.y * pageSize.height}px`,
    width: `${interaction.rect.width * pageSize.width}px`,
    height: `${interaction.rect.height * pageSize.height}px`
  };

  const showCheckChip = mode === "practice" && !!answer.trim() && !!onCheck;

  return (
    <>
      <textarea
        className={interaction.type === "drawing" ? "response-field drawing-field" : "response-field"}
        style={style}
        value={answer}
        disabled={locked}
        aria-label={`Question ${interaction.question} response`}
        placeholder={interaction.type === "drawing" ? "Drawing response placeholder" : ""}
        onChange={(event) => !locked && onAnswer(interaction.id, event.target.value)}
      />
      {showCheckChip && (
        <button
          type="button"
          className={checked ? "check-chip check-chip-done" : "check-chip"}
          style={{
            left: `${(interaction.rect.x + interaction.rect.width) * pageSize.width - 118}px`,
            top: `${(interaction.rect.y + interaction.rect.height) * pageSize.height + 4}px`
          }}
          onClick={() => onCheck?.(interaction.id)}
        >
          {checked ? "View answer" : "Check / Show answer"}
        </button>
      )}
    </>
  );
}
