import { useEffect, useRef, useState } from "react";
import type { Attempt } from "../data/types";
import { formatDuration, getTimedStatus } from "../lib/timedAttempt";

/**
 * Writing-time countdown for Timed Mode (no Reading Time lock -- see
 * lib/timedAttempt.ts). Recomputes from the attempt's stored absolute
 * deadline every second, so it's always correct even immediately after a
 * refresh (no reliance on an in-memory counter that a reload would reset).
 */
export function Timer({ attempt, onExpire }: { attempt: Attempt; onExpire: () => void }) {
  const [status, setStatus] = useState(() => getTimedStatus(attempt));
  const expiredRef = useRef(false);

  useEffect(() => {
    const tick = () => {
      const next = getTimedStatus(attempt);
      setStatus(next);
      if (next.phase === "expired" && !expiredRef.current) {
        expiredRef.current = true;
        onExpire();
      }
    };
    tick();
    const interval = window.setInterval(tick, 1000);
    return () => window.clearInterval(interval);
  }, [attempt, onExpire]);

  const label = status.phase === "writing" ? "Writing time" : "Time's up";

  return (
    <div className={`timer timer-${status.phase}`} role="timer" aria-live="polite">
      <span className="timer-label">{label}</span>
      <span className="timer-clock">{formatDuration(status.msRemaining)}</span>
    </div>
  );
}
