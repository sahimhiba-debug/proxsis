// The status of a post at a glance: a copper arc for the working days of restriction still to run (full at five,
// empty when publication is free), a quiet closed ring once it is over, a thin ring for a post not subject, a dashed
// ring when the match is not checked. Drawn only: the words next to it say the same.
const R = 13;
const C = 2 * Math.PI * R;

type RingStatus = "subject" | "free" | "not-subject" | "unknown";

export function StatusRing({ status, left = 0, of = 5 }: { status: RingStatus; left?: number; of?: number }) {
  const arc = status === "subject" ? Math.max(0, Math.min(1, left / of)) : 0;
  return (
    <svg className="fx-ring" data-status={status} viewBox="0 0 32 32" width="32" height="32" aria-hidden focusable="false">
      <circle cx="16" cy="16" r={R} className="fx-ring-base" />
      {status === "subject" ? (
        <circle cx="16" cy="16" r={R} className="fx-ring-arc" strokeDasharray={`${(arc * C).toFixed(2)} ${C.toFixed(2)}`}
          transform="rotate(-90 16 16)" />
      ) : null}
      {status === "subject" ? <text x="16" y="16" className="fx-ring-n" textAnchor="middle" dominantBaseline="central">{left}</text> : null}
    </svg>
  );
}
