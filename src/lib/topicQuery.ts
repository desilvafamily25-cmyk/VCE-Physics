import type { CurriculumTag, Interaction, QuestionAnswer, SharedStimulusGroup } from "../data/types";

export type TopicQuestion = {
  paperId: string;
  interactionId: string;
  canonicalId: string;
  section: "A" | "B";
  questionLabel: string;
  marks: number | null;
  unit: string;
  areaOfStudy: string;
  topic: string;
  skills: string[];
  difficulty: string;
};

export function buildTopicQuestions(
  paperId: string,
  interactions: Interaction[],
  answers: QuestionAnswer[],
  curriculum: CurriculumTag[]
): TopicQuestion[] {
  const answerById = new Map(answers.map((a) => [a.interactionId, a]));
  const curriculumById = new Map(curriculum.map((c) => [c.interactionId, c]));

  return interactions
    .map((interaction) => {
      const tag = curriculumById.get(interaction.id);
      const answer = answerById.get(interaction.id);
      if (!tag) return null;
      const question: TopicQuestion = {
        paperId,
        interactionId: interaction.id,
        canonicalId: tag.canonicalId,
        section: interaction.section,
        questionLabel: interaction.question,
        marks: answer?.marks ?? interaction.marks ?? null,
        unit: tag.unit,
        areaOfStudy: tag.areaOfStudy,
        topic: tag.topic,
        skills: tag.skills,
        difficulty: answer?.difficulty.level ?? "unknown"
      };
      return question;
    })
    .filter((q): q is TopicQuestion => q !== null);
}

export type TopicFilter = {
  areaOfStudy?: string;
  topic?: string;
  skill?: string;
  difficulty?: string;
};

export function filterTopicQuestions(questions: TopicQuestion[], filter: TopicFilter): TopicQuestion[] {
  return questions.filter((q) => {
    if (filter.areaOfStudy && q.areaOfStudy !== filter.areaOfStudy) return false;
    if (filter.topic && q.topic !== filter.topic) return false;
    if (filter.skill && !q.skills.includes(filter.skill)) return false;
    if (filter.difficulty && q.difficulty !== filter.difficulty) return false;
    return true;
  });
}

/**
 * Section B subparts of the same top-level question (e.g. B4ai, B4bii, B4d)
 * share a stimulus laid out contiguously by VCAA -- grouping by the leading
 * number after "B" is enough to recover the full stimulus range.
 */
function sectionBParentKey(interactionId: string): string | null {
  const match = /^B(\d+)/.exec(interactionId);
  return match ? `B${match[1]}` : null;
}

/**
 * Returns the inclusive page range needed to show a question with its full
 * required stimulus (never show an isolated subquestion without shared
 * context). Falls back to the question's own page(s) when no shared-stimulus
 * grouping applies.
 */
export function pagesForSelection(
  selectedInteractionIds: string[],
  allInteractions: Interaction[],
  sharedGroups: SharedStimulusGroup[]
): number[] {
  const byId = new Map(allInteractions.map((i) => [i.id, i]));
  const pages = new Set<number>();

  for (const id of selectedInteractionIds) {
    const interaction = byId.get(id);
    if (interaction) pages.add(interaction.page);

    const group = sharedGroups.find((g) => g.interactionIds.includes(id));
    if (group) group.pages.forEach((p) => pages.add(p));

    const parentKey = sectionBParentKey(id);
    if (parentKey) {
      for (const other of allInteractions) {
        if (other.section === "B" && sectionBParentKey(other.id) === parentKey) {
          pages.add(other.page);
        }
      }
    }
  }

  if (pages.size === 0) return [];
  const min = Math.min(...pages);
  const max = Math.max(...pages);
  return Array.from({ length: max - min + 1 }, (_, i) => min + i);
}
