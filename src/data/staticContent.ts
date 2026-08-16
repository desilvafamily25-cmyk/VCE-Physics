// Static content (papers, interaction geometry, official answers, curriculum
// mapping) is identical for every storage backend -- it's read-only,
// generated ahead of time by scripts/ into public/, and never scoped to a
// user. Both LocalRepository and SupabaseRepository share this module
// rather than each re-implementing the same fetch/cache logic. See
// docs/DATA-ARCHITECTURE.md.
import type { CurriculumTag, Interaction, Paper, QuestionAnswer, SharedStimulusGroup } from "./types";

async function fetchJsonCached<T>(url: string, cache: Map<string, Promise<unknown>>): Promise<T> {
  let pending = cache.get(url) as Promise<T> | undefined;
  if (!pending) {
    pending = fetch(url).then((response) => {
      if (!response.ok) {
        throw new Error(`Failed to load ${url}: ${response.status}`);
      }
      return response.json() as Promise<T>;
    });
    cache.set(url, pending);
  }
  return pending;
}

// De-duplicates/canonicalises Section A interaction ids -- mirrors the
// original prototype's behaviour so hand-authored *-interactions.json files
// can stay loosely formatted.
function normalizeInteractions(items: Interaction[]): Interaction[] {
  const seenMcqIds = new Set<string>();

  return items.filter((item) => {
    if (item.section !== "A") {
      return true;
    }

    const questionNumber = Number.parseInt(item.question, 10);
    const canonicalId = Number.isFinite(questionNumber) ? `A${questionNumber}` : item.id;
    item.id = canonicalId;
    item.type = "mcq";

    if (seenMcqIds.has(canonicalId)) {
      return false;
    }

    seenMcqIds.add(canonicalId);
    return true;
  });
}

export class StaticContentSource {
  private jsonCache = new Map<string, Promise<unknown>>();

  async getPapers(): Promise<Paper[]> {
    return fetchJsonCached<Paper[]>("/papers.json", this.jsonCache);
  }

  async getInteractions(paper: Paper): Promise<Interaction[]> {
    const items = await fetchJsonCached<Interaction[]>(paper.interactionsUrl, this.jsonCache);
    return normalizeInteractions(items);
  }

  async getAnswers(paper: Paper): Promise<QuestionAnswer[] | null> {
    if (!paper.hasAnswerData) return null;
    try {
      return await fetchJsonCached<QuestionAnswer[]>(`/answers/${paper.id}.json`, this.jsonCache);
    } catch {
      return null;
    }
  }

  async getCurriculumMap(paper: Paper): Promise<CurriculumTag[] | null> {
    if (!paper.hasCurriculumMap) return null;
    try {
      const data = await fetchJsonCached<{ questions: CurriculumTag[] }>(
        `/curriculum/${paper.id}-mapping.json`,
        this.jsonCache
      );
      return data.questions;
    } catch {
      return null;
    }
  }

  async getSharedStimulusGroups(paper: Paper): Promise<SharedStimulusGroup[]> {
    try {
      const data = await fetchJsonCached<{ groups: SharedStimulusGroup[] }>(
        `/curriculum/${paper.id}-shared-stimulus.json`,
        this.jsonCache
      );
      return data.groups;
    } catch {
      return [];
    }
  }
}
