import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import * as pdfjsLib from "pdfjs-dist";
import type { Attempt as AttemptT, AttemptMode, Interaction, Paper, QuestionAnswer, QuestionOutcome, Rect } from "../data/types";
import { repository } from "../data";
import { PdfOverlay, type DragState } from "../components/PdfOverlay";
import { McqControl } from "../components/McqControl";
import { WrittenControl } from "../components/WrittenControl";
import { AnswerPanel } from "../components/AnswerPanel";
import { Timer } from "../components/Timer";
import { FormulaSheetPanel } from "../components/FormulaSheetPanel";
import { canonicalId, isMcqCorrect } from "../lib/scoring";
import { getTimedStatus } from "../lib/timedAttempt";

export function AttemptRoute() {
  const { paperId = "", mode: modeParam = "practice" } = useParams();
  const mode = (modeParam === "timed" ? "timed" : "practice") as AttemptMode;
  const navigate = useNavigate();

  const [paper, setPaper] = useState<Paper | null>(null);
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [answers, setAnswers] = useState<QuestionAnswer[] | null>(null);
  const [pdf, setPdf] = useState<pdfjsLib.PDFDocumentProxy | null>(null);
  const [attempt, setAttempt] = useState<AttemptT | null>(null);
  const [activeAnswerId, setActiveAnswerId] = useState<string | null>(null);
  const [developerMode, setDeveloperMode] = useState(false);
  const [selectedRect, setSelectedRect] = useState<Rect | null>(null);
  const [drag, setDrag] = useState<DragState | null>(null);
  const [savedFlash, setSavedFlash] = useState(false);
  const [showFormulaSheet, setShowFormulaSheet] = useState(false);
  // Set when the student asks for one mode (e.g. Practice) but an
  // unsubmitted attempt already exists in the other mode (e.g. Timed) --
  // an explicit choice instead of a silent redirect back to the in-progress
  // mode (which would look like the requested mode's controls "did nothing").
  const [modeConflict, setModeConflict] = useState<AttemptT | null>(null);

  const loadForMode = useCallback(
    async (found: Paper, requestedMode: AttemptMode, force: "keep-existing" | "discard-existing" | "ask" = "ask") => {
      const existing = await repository.getAttempt(found.id);

      if (existing && !existing.submittedAt && existing.mode !== requestedMode) {
        if (force === "discard-existing") {
          await repository.clearAttempt(found.id);
          setModeConflict(null);
          setAttempt(await repository.startAttempt(found, requestedMode));
          return;
        }
        if (force !== "keep-existing") {
          setModeConflict(existing);
          return;
        }
      }

      setModeConflict(null);
      if (existing && !existing.submittedAt && existing.mode === requestedMode) {
        setAttempt(existing);
      } else {
        setAttempt(await repository.startAttempt(found, requestedMode));
      }
    },
    []
  );

  useEffect(() => {
    let cancelled = false;

    (async () => {
      const papers = await repository.getPapers();
      const found = papers.find((p) => p.id === paperId) ?? null;
      if (!found || cancelled) return;
      setPaper(found);

      const [loadedInteractions, loadedAnswers, loadedPdf] = await Promise.all([
        repository.getInteractions(found),
        repository.getAnswers(found),
        pdfjsLib.getDocument({ url: found.pdfUrl }).promise
      ]);
      if (cancelled) return;

      setInteractions(loadedInteractions);
      setAnswers(loadedAnswers);
      setPdf(loadedPdf);
      await loadForMode(found, mode);
    })();

    return () => {
      cancelled = true;
    };
  }, [paperId, mode, loadForMode]);

  const answerByInteractionId = useMemo(() => {
    const map = new Map<string, QuestionAnswer>();
    (answers ?? []).forEach((a) => map.set(a.interactionId, a));
    return map;
  }, [answers]);

  const interactionsByPage = useMemo(() => {
    return interactions.reduce<Record<number, Interaction[]>>((byPage, item) => {
      byPage[item.page] = byPage[item.page] ?? [];
      byPage[item.page].push(item);
      return byPage;
    }, {});
  }, [interactions]);

  const persist = useCallback((next: AttemptT) => {
    setAttempt(next);
    repository.saveAttempt(next);
    setSavedFlash(true);
    window.setTimeout(() => setSavedFlash(false), 800);
  }, []);

  const updateAnswer = useCallback((id: string, value: string) => {
    setAttempt((current) => {
      if (!current) return current;
      const next: AttemptT = { ...current, answers: { ...current.answers, [id]: value } };
      repository.saveAttempt(next);
      return next;
    });
  }, []);

  const finishAttempt = useCallback(
    (auto: boolean) => {
      if (!attempt || !paper) return;
      if (!auto && !window.confirm(`Submit this ${mode === "timed" ? "timed" : "practice"} attempt for ${paper.title}?`)) {
        return;
      }
      const next: AttemptT = { ...attempt, submittedAt: new Date().toISOString() };
      persist(next);
      navigate(`/review/${paper.id}`);
    },
    [attempt, paper, mode, persist, navigate]
  );

  const resetAttempt = useCallback(async () => {
    if (!paper) return;
    if (!window.confirm(`Reset this attempt for ${paper.title}? All saved answers for this paper will be cleared.`)) {
      return;
    }
    await repository.clearAttempt(paper.id);
    setActiveAnswerId(null);
    setAttempt(await repository.startAttempt(paper, mode));
  }, [paper, mode]);

  const recordCheck = useCallback(
    (interaction: Interaction, outcome: QuestionOutcome, selfAssessed: boolean, studentAnswer: string) => {
      if (!paper) return;
      repository.recordQuestionResult({
        id: `${paper.id}-${interaction.id}-${Date.now()}`,
        canonicalId: canonicalId(paper.id, interaction.id),
        paperId: paper.id,
        interactionId: interaction.id,
        section: interaction.section,
        mode,
        studentAnswer,
        outcome,
        selfAssessed,
        checkedAt: new Date().toISOString()
      });
    },
    [paper, mode]
  );

  const onCheck = useCallback(
    (interaction: Interaction) => {
      setAttempt((current) => {
        if (!current) return current;
        const next: AttemptT = { ...current, checked: { ...current.checked, [interaction.id]: true } };
        repository.saveAttempt(next);
        return next;
      });
      setActiveAnswerId(interaction.id);

      const qa = answerByInteractionId.get(interaction.id);
      const studentAnswer = attempt?.answers[interaction.id] ?? "";

      if (qa?.withdrawn) {
        // A withdrawn question is recorded so it still shows up in history,
        // but as its own outcome -- never as "incorrect" and never asking
        // the student to self-assess something VCAA itself discarded.
        recordCheck(interaction, "withdrawn", false, studentAnswer);
        return;
      }

      if (interaction.section === "A" && qa) {
        recordCheck(interaction, isMcqCorrect(studentAnswer, qa) ? "correct" : "incorrect", false, studentAnswer);
      }
      // Section B (non-withdrawn) outcome is recorded when the student
      // self-assesses in AnswerPanel.
    },
    [answerByInteractionId, attempt, recordCheck]
  );

  const onSelfAssess = useCallback(
    (interaction: Interaction, outcome: QuestionOutcome) => {
      const studentAnswer = attempt?.answers[interaction.id] ?? "";
      recordCheck(interaction, outcome, true, studentAnswer);
      setActiveAnswerId(null);
    },
    [attempt, recordCheck]
  );

  if (paper && modeConflict) {
    const requestedLabel = mode === "timed" ? "Timed Mode" : "Practice Mode";
    const existingLabel = modeConflict.mode === "timed" ? "Timed" : "Practice";
    return (
      <div className="page mode-conflict">
        <h2>You already have a {existingLabel.toLowerCase()} attempt in progress</h2>
        <p className="page-intro">
          You started a {existingLabel} attempt on {paper.title} at{" "}
          {new Date(modeConflict.startedAt).toLocaleTimeString()} and haven't submitted it yet. You can resume that
          attempt, or discard it and start a fresh {requestedLabel} attempt instead — but discarding will permanently
          delete its saved answers.
        </p>
        <div className="mode-conflict-actions">
          <button type="button" className="btn btn-primary" onClick={() => navigate(`/attempt/${paperId}/${modeConflict.mode}`, { replace: true })}>
            Resume {existingLabel} attempt
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => paper && loadForMode(paper, mode, "discard-existing")}
          >
            Discard it and start {requestedLabel}
          </button>
        </div>
        <p className="review-footer">
          <Link to="/papers">← Back to Past Papers</Link>
        </p>
      </div>
    );
  }

  if (!paper || !attempt) {
    return <div className="loading">Loading {paperId}...</div>;
  }

  const timedStatus = mode === "timed" ? getTimedStatus(attempt) : null;
  // Timed mode has no Reading Time lock -- only "expired" (auto-submitted)
  // or an already-submitted attempt locks further editing.
  const locked = mode === "timed" ? timedStatus?.phase === "expired" : Boolean(attempt.submittedAt);
  const activeInteraction = interactions.find((i) => i.id === activeAnswerId) ?? null;

  const sectionAItems = interactions.filter((i) => i.section === "A");
  const answeredTotal = interactions.filter((i) => (attempt.answers[i.id] ?? "").trim()).length;
  const sectionAAnswered = sectionAItems.filter((i) => Boolean(attempt.answers[i.id])).length;

  return (
    <div className="app">
      <header className="topbar">
        <div className="title-block">
          <h1>{paper.title}</h1>
          <p>
            {mode === "timed" ? "Timed Mode" : "Practice Mode"} — {answeredTotal} of {interactions.length} answered
          </p>
        </div>
        <div className="toolbar" aria-label="Exam controls">
          {sectionAItems.length > 0 && (
            <span className="progress">
              Section A {sectionAAnswered} / {sectionAItems.length}
            </span>
          )}
          <span className={savedFlash ? "saved saved-on" : "saved"}>{savedFlash ? "Saved" : "All changes saved"}</span>
          {mode === "timed" && !attempt.submittedAt && <Timer attempt={attempt} onExpire={() => finishAttempt(true)} />}
          {!paper.hasAnswerData && (
            <span className="data-missing-note">Official answers not yet available for this paper.</span>
          )}
          {paper.formulaSheetUrl && (
            <button type="button" className="formula-toggle" onClick={() => setShowFormulaSheet(true)}>
              📐 Formula sheet
            </button>
          )}
          <label className="dev-toggle">
            <input
              type="checkbox"
              checked={developerMode}
              onChange={(event) => {
                setDeveloperMode(event.target.checked);
                setSelectedRect(null);
                setDrag(null);
              }}
            />
            Dev coordinates
          </label>
          <button type="button" className="btn btn-danger-ghost btn-sm" onClick={resetAttempt}>
            Reset attempt
          </button>
          {!attempt.submittedAt && (
            <button type="button" className="btn btn-primary btn-sm" onClick={() => finishAttempt(false)}>
              {mode === "timed" ? "Submit Exam" : "Finish & Review"}
            </button>
          )}
          {attempt.submittedAt && <Link to={`/review/${paper.id}`}>View review →</Link>}
        </div>
      </header>

      {selectedRect && (
        <div className="coord-panel">
          <code>{JSON.stringify({ rect: selectedRect }, null, 2)}</code>
          <button type="button" className="btn btn-secondary btn-sm" onClick={() => navigator.clipboard.writeText(JSON.stringify(selectedRect, null, 2))}>
            Copy rect
          </button>
        </div>
      )}

      <div className="attempt-layout">
        <main className="paper">
          {!pdf && <div className="loading">Loading original PDF for {paper.title}...</div>}
          {pdf && (
            <PdfOverlay
              pdf={pdf}
              pages={Array.from({ length: pdf.numPages }, (_, i) => i + 1)}
              interactionsByPage={interactionsByPage}
              developerMode={developerMode}
              drag={drag}
              setDrag={setDrag}
              setSelectedRect={setSelectedRect}
              renderControl={(interaction, pageSize) => {
                const answer = attempt.answers[interaction.id] ?? "";
                const checked = Boolean(attempt.checked?.[interaction.id]);
                if (interaction.type === "mcq") {
                  return (
                    <McqControl
                      interaction={interaction}
                      answer={answer}
                      onAnswer={updateAnswer}
                      pageSize={pageSize}
                      mode={mode === "timed" ? "timed" : "practice"}
                      locked={locked}
                      checked={checked}
                      onCheck={paper.hasAnswerData ? () => onCheck(interaction) : undefined}
                      questionAnswer={answerByInteractionId.get(interaction.id)}
                    />
                  );
                }
                return (
                  <WrittenControl
                    interaction={interaction}
                    answer={answer}
                    onAnswer={updateAnswer}
                    pageSize={pageSize}
                    mode={mode === "timed" ? "timed" : "practice"}
                    locked={locked}
                    checked={checked}
                    onCheck={paper.hasAnswerData ? () => onCheck(interaction) : undefined}
                  />
                );
              }}
            />
          )}
        </main>

        {mode === "practice" && activeInteraction && (
          <AnswerPanel
            interaction={activeInteraction}
            studentAnswer={attempt.answers[activeInteraction.id] ?? ""}
            questionAnswer={answerByInteractionId.get(activeInteraction.id) ?? null}
            onSelfAssess={
              activeInteraction.section === "B" && !answerByInteractionId.get(activeInteraction.id)?.withdrawn
                ? (outcome) => onSelfAssess(activeInteraction, outcome)
                : undefined
            }
            onClose={() => setActiveAnswerId(null)}
          />
        )}
      </div>

      {showFormulaSheet && paper.formulaSheetUrl && (
        <FormulaSheetPanel url={paper.formulaSheetUrl} onClose={() => setShowFormulaSheet(false)} />
      )}
    </div>
  );
}
