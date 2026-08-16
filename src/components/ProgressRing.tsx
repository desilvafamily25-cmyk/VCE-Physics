/**
 * Small SVG progress ring -- part of the design system's visual-progress
 * commitment (real numbers only; see docs/DATA-ARCHITECTURE.md and the
 * build brief's "never fabricate scores" rule). Used for per-paper and
 * per-Area-of-Study completion on the dashboard and Progress page.
 */
export function ProgressRing({
  value,
  size = 44,
  strokeWidth = 5,
  label
}: {
  value: number; // 0-1
  size?: number;
  strokeWidth?: number;
  label?: string;
}) {
  const clamped = Math.max(0, Math.min(1, value));
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - clamped);
  const complete = clamped >= 1;

  return (
    <div className={`progress-ring${complete ? " ring-complete" : ""}`} style={{ width: size, height: size }}>
      <svg width={size} height={size}>
        <circle className="ring-track" cx={size / 2} cy={size / 2} r={radius} strokeWidth={strokeWidth} />
        <circle
          className="ring-value"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
        />
      </svg>
      <span className="progress-ring-label">{label ?? `${Math.round(clamped * 100)}%`}</span>
    </div>
  );
}
