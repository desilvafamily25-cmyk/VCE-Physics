import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { Paper } from "../data/types";
import { repository } from "../data";
import { buildTopicQuestions, filterTopicQuestions, type TopicFilter, type TopicQuestion } from "../lib/topicQuery";

export function TopicPracticeRoute() {
  const navigate = useNavigate();
  const [papers, setPapers] = useState<Paper[]>([]);
  const [questions, setQuestions] = useState<TopicQuestion[] | null>(null);
  const [filter, setFilter] = useState<TopicFilter & { paperId?: string }>({});
  const [selected, setSelected] = useState<Set<string>>(new Set());

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const allPapers = await repository.getPapers();
      // Every paper with a curriculum map contributes its questions here.
      // Archive-era papers (2002-2016) never appear -- their elective
      // Detailed Study structure doesn't map onto the current curriculum,
      // see docs/DATA-ARCHITECTURE.md.
      const mappedPapers = allPapers.filter((p) => p.hasCurriculumMap);
      if (mappedPapers.length === 0 || cancelled) {
        setQuestions([]);
        return;
      }
      setPapers(mappedPapers);

      const perPaperQuestions = await Promise.all(
        mappedPapers.map(async (paper) => {
          const [interactions, answers, curriculum] = await Promise.all([
            repository.getInteractions(paper),
            repository.getAnswers(paper),
            repository.getCurriculumMap(paper)
          ]);
          return buildTopicQuestions(paper.id, interactions, answers ?? [], curriculum ?? []);
        })
      );
      if (!cancelled) setQuestions(perPaperQuestions.flat());
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const paperFiltered = useMemo(
    () => (questions ? (filter.paperId ? questions.filter((q) => q.paperId === filter.paperId) : questions) : []),
    [questions, filter.paperId]
  );
  const filtered = useMemo(() => filterTopicQuestions(paperFiltered, filter), [paperFiltered, filter]);

  const areas = useMemo(() => Array.from(new Set(paperFiltered.map((q) => q.areaOfStudy))).sort(), [paperFiltered]);
  const topics = useMemo(
    () =>
      Array.from(
        new Set(paperFiltered.filter((q) => !filter.areaOfStudy || q.areaOfStudy === filter.areaOfStudy).map((q) => q.topic))
      ).sort(),
    [paperFiltered, filter.areaOfStudy]
  );
  const skills = useMemo(() => Array.from(new Set(paperFiltered.flatMap((q) => q.skills))).sort(), [paperFiltered]);
  const difficulties = ["Easy", "Medium", "Hard", "Very Hard", "unknown"];
  const paperTitleById = useMemo(() => new Map(papers.map((p) => [p.id, p.title])), [papers]);

  const toggleSelected = (canonicalId: string) => {
    setSelected((current) => {
      const next = new Set(current);
      if (next.has(canonicalId)) next.delete(canonicalId);
      else next.add(canonicalId);
      return next;
    });
  };

  const startSession = (ids: string[]) => {
    if (ids.length === 0) return;
    // A session is scoped to one paper (it renders that paper's PDF). If a
    // selection spans multiple papers, start with whichever paper has the
    // most selected questions and let the student know the rest were left out.
    const byPaper = new Map<string, string[]>();
    for (const id of ids) {
      const paperId = id.split("-")[0];
      byPaper.set(paperId, [...(byPaper.get(paperId) ?? []), id]);
    }
    const [topPaperId, topIds] = Array.from(byPaper.entries()).sort((a, b) => b[1].length - a[1].length)[0];
    if (byPaper.size > 1) {
      const otherCount = ids.length - topIds.length;
      window.alert(
        `This selection spans ${byPaper.size} papers. Starting a session for ${paperTitleById.get(topPaperId) ?? topPaperId} (${topIds.length} question${topIds.length === 1 ? "" : "s"}) — filter by paper to practise the other ${otherCount} separately.`
      );
    }
    const bareIds = topIds.map((id) => id.replace(`${topPaperId}-`, ""));
    navigate(`/topics/session?paper=${topPaperId}&ids=${bareIds.join(",")}`);
  };

  if (!questions) {
    return <div className="loading">Loading topic bank…</div>;
  }

  if (questions.length === 0) {
    return (
      <div className="page">
        <h2>Practice by Topic</h2>
        <div className="empty-state card">
          <p>No topic-tagged papers are available yet — check back soon, or attempt a paper in Timed/Practice mode.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <h2>Practice by Topic</h2>
      <p className="page-intro">
        Every question here is a real past-paper question, mapped to the VCE Physics Study Design. Filter by paper,
        Area of Study, topic, skill or difficulty, then practise with the official answer alongside — just like
        Practice Mode.
      </p>

      <div className="topic-filters">
        <select value={filter.paperId ?? ""} onChange={(e) => setFilter((f) => ({ ...f, paperId: e.target.value || undefined }))}>
          <option value="">All papers</option>
          {papers.map((p) => (
            <option key={p.id} value={p.id}>
              {p.title}
            </option>
          ))}
        </select>
        <select value={filter.areaOfStudy ?? ""} onChange={(e) => setFilter((f) => ({ ...f, areaOfStudy: e.target.value || undefined, topic: undefined }))}>
          <option value="">All Areas of Study</option>
          {areas.map((area) => (
            <option key={area} value={area}>
              {area}
            </option>
          ))}
        </select>
        <select value={filter.topic ?? ""} onChange={(e) => setFilter((f) => ({ ...f, topic: e.target.value || undefined }))}>
          <option value="">All topics</option>
          {topics.map((topic) => (
            <option key={topic} value={topic}>
              {topic}
            </option>
          ))}
        </select>
        <select value={filter.skill ?? ""} onChange={(e) => setFilter((f) => ({ ...f, skill: e.target.value || undefined }))}>
          <option value="">All skills</option>
          {skills.map((skill) => (
            <option key={skill} value={skill}>
              {skill}
            </option>
          ))}
        </select>
        <select value={filter.difficulty ?? ""} onChange={(e) => setFilter((f) => ({ ...f, difficulty: e.target.value || undefined }))}>
          <option value="">All difficulties</option>
          {difficulties.map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>
      </div>

      <div className="topic-actions">
        <span>{filtered.length} questions match</span>
        <button type="button" className="btn btn-primary btn-sm" disabled={filtered.length === 0} onClick={() => startSession(filtered.map((q) => q.canonicalId))}>
          Practise all {filtered.length}
        </button>
        <button type="button" className="btn btn-secondary btn-sm" disabled={selected.size === 0} onClick={() => startSession(Array.from(selected))}>
          Practise selected ({selected.size})
        </button>
      </div>

      <div className="data-table-wrap">
        <table className="topic-table">
          <thead>
            <tr>
              <th></th>
              <th>Paper</th>
              <th>Q</th>
              <th>Topic</th>
              <th>Skills</th>
              <th>Marks</th>
              <th>Difficulty</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((q) => (
              <tr key={q.canonicalId}>
                <td>
                  <input type="checkbox" checked={selected.has(q.canonicalId)} onChange={() => toggleSelected(q.canonicalId)} />
                </td>
                <td>{paperTitleById.get(q.paperId) ?? q.paperId}</td>
                <td>
                  {q.section}
                  {q.questionLabel}
                </td>
                <td>{q.topic}</td>
                <td>{q.skills.join(", ")}</td>
                <td>{q.marks ?? "—"}</td>
                <td>
                  <span className={`difficulty-pill difficulty-${q.difficulty.replace(/\s+/g, "-").toLowerCase()}`}>{q.difficulty}</span>
                </td>
                <td>
                  <button type="button" className="btn btn-ghost btn-sm" onClick={() => startSession([q.canonicalId])}>
                    Practise
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
