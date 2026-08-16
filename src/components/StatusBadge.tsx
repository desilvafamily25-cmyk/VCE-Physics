export type PaperStatus = "not-started" | "in-progress" | "completed";

export function StatusBadge({ status }: { status: PaperStatus }) {
  const label = status === "not-started" ? "Not started" : status === "in-progress" ? "In progress" : "Completed";
  return <span className={`status-badge status-${status}`}>{label}</span>;
}
