import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import * as pdfjsLib from "pdfjs-dist";
import type { Attempt, Interaction, Paper, QuestionAnswer, QuestionOutcome, SharedStimulusGroup } from "../data/types";
import { repository } from "../data";
import { PdfOverlay } from "../components/PdfOverlay";
import { McqControl } from "../components/McqControl";
import { WrittenControl } from "../components/WrittenControl";
import { AnswerPanel } from "../components/AnswerPanel";
import { FormulaSheetPanel } from "../components/FormulaSheetPanel";
import { canonicalId, isMcqCorrect } from "../lib/scoring";
import { pagesForSelection } from "../lib/topicQuery";

export function TopicSessionRoute() {
  const [searchParams] = useSearchParams();
  const paperId = searchParams.get("paper") ?? "";
  const requestedIds = useMemo(() => (searchParams.get("ids") ?? "").split(",").filter(Boolean), [searchParams]);

  const [paper, setPaper] = useState<Paper | null>(null);
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [answers, setAnswers] = useState<QuestionAnswer[]>([]);
  const [sharedGroups, setSharedGroups] = useState<SharedStimulusGroup[]>([]);
  const [pdf, setPdf] = useState<pdfjsLib.PDFDocumentProxy | null>(null);
  const [attempt, setAttempt] = useState<Attempt | null>(null);
  const [activeAnswerId, setActiveAnswerId] = useState<string | null>(null);
  const [showFormulaSheet, setShowFormulaSheet] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const papers = await repository.getPapers();
      const found = papers.find((p) => p.id === paperId) ?? null;
      if (!found || cancelled) return;
      setPaper(found);

      const [loadedInteractions, loadedAnswers, groups, loadedPdf, existingAttempt] = await Promise.all([
        repository.getInteractions(found),
        repository.getAnswers(found),
        repository.getSharedStimulusGroups(found),
        pdfjsLib.getDocument({ url: found.pdfUrl }).promise,
        repository.getAttempt(found.id)
      ]);
      if (cancelled) return;

      setInteractions(loadedInteractions);
      setAnswers(loadedAnswers ?? []);
      setSharedGroups(groups);
      setPdf(loadedPdf);
      // Topic Practice shares the same underlying paper attempt as Practice
      // Mode, so progress made here also counts toward that paper's record.
      setAttempt(existingAttempt && !existingAttempt.submittedAt ? existingAttempt : await repository.startAttempt(found, "practice"));
    })();
    return () => {
      cancelled = true;
    };
  }, [paperId]);

  const answerByInteractionId = useMemo(() => new Map(answers.map((a) => [a.interactionId, a])), [answers]);

  const pages = useMemo(
    () => pagesForSelection(requestedIds, interactions, sharedGroups),
    [requestedIds, interactions, sharedGroups]
  );

  const interactionsByPage = useMemo(() => {
    return interactions.reduce<Record<number, Interaction[]>>((byPage, item) => {
      if (!pages.includes(item.page)) return byPage;
      byPage[item.page] = byPage[item.page] ?? [];
      byPage[item.page].push(item);
      return byPage;
    }, {});
  }, [interactions, pages]);

  const updateAnswer = useCallback((id: string, value: string) => {
    setAttempt((current) => {
      if (!current) return current;
      const next: Attempt = { ...current, answers: { ...current.answers, [id]: value } };
      repository.saveAttempt(next);
      return next;
    });
  }, []);

  const recordCheck = useCallback(
    (interaction: Interaction, outcome: QuestionOutcome, selfAssessed: boolean, studentAnswer: string) => {
      if (!paper) return;
      repository.recordQuestionResult({
        id: `${paper.id}-${interaction.id}-${Date.now()}`,
        canonicalId: canonicalId(paper.id, interaction.id),
        paperId: paper.id,
        interactionId: interaction.id,
        section: interaction.section,
        mode: "practice",
        studentAnswer,
        outcome,
        selfAssessed,
        checkedAt: new Date().toISOString()
      });
    },
    [paper]
  );

  const onCheck = useCallback(
    (interaction: Interaction) => {
      setAttempt((current) => {
        if (!current) return current;
        const next: Attempt = { ...current, checked: { ...current.checked, [interaction.id]: true } };
        repository.saveAttempt(next);
        return next;
      });
      setActiveAnswerId(interaction.id);

      const qa = answerByInteractionId.get(interaction.id);
      const studentAnswer = attempt?.answers[interaction.id] ?? "";

      if (qa?.withdrawn) {
        recordCheck(interaction, "withdrawn", false, studentAnswer);
        return;
      }

      if (interaction.section === "A" && qa) {
        recordCheck(interaction, isMcqCorrect(studentAnswer, qa) ? "correct" : "incorrect", false, studentAnswer);
      }
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

  if (!paper || !attempt || !pdf) {
    return <div className="loading">Loading topic practice session…</div>;
  }

  const activeInteraction = interactions.find((i) => i.id === activeAnswerId) ?? null;

  return (
    <div className="app">
      <header className="topbar">
        <div className="title-block">
          <h1>Topic Practice — {paper.title}</h1>
          <p>
            {requestedIds.length} question{requestedIds.length === 1 ? "" : "s"} selected · showing page{pages.length === 1 ? "" : "s"}{" "}
            {pages.join(", ")}
          </p>
        </div>
        <div className="toolbar">
          {paper.formulaSheetUrl && (
            <button type="button" className="formula-toggle" onClick={() => setShowFormulaSheet(true)}>
              📐 Formula sheet
            </button>
          )}
          <Link to="/topics">← Back to topic picker</Link>
        </div>
      </header>

      <div className="attempt-layout">
        <main className="paper">
          <PdfOverlay
            pdf={pdf}
            pages={pages}
            interactionsByPage={interactionsByPage}
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
                    mode="practice"
                    locked={false}
                    checked={checked}
                    onCheck={() => onCheck(interaction)}
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
                  mode="practice"
                  locked={false}
                  checked={checked}
                  onCheck={() => onCheck(interaction)}
                />
              );
            }}
          />
        </main>

        {activeInteraction && (
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
