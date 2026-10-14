"use client";

import { motion } from "motion/react";
import { EASE, PULSE_REPEAT } from "./motion";

export interface Point { date: string; x: number; recent: boolean; titre: string }

/** One dot per public contract over 52 weeks, oldest left; a contract of less than 14 days carries a copper pulse. */
export function MicroTimeline({ points, label, recentLabel }: { points: Point[]; label: string; recentLabel: string }) {
  return (
    <div className="fx-track" role="img" aria-label={label}>
      {points.map((p, i) => (
        <span key={`${p.date}-${i}`} className="fx-dot" data-recent={p.recent} style={{ left: `${(p.x * 100).toFixed(2)}%` }}
          title={p.recent ? recentLabel : undefined}>
          {p.recent ? ( /* hidden by CSS when motion is reduced */
            <motion.span className="fx-pulse" aria-hidden initial={{ opacity: 0.7, scale: 0.6 }}
              animate={{ opacity: 0, scale: 2.4 }} transition={{ duration: 1.8, ease: EASE, repeat: PULSE_REPEAT, repeatDelay: 0.6 }} />
          ) : null}
        </span>
      ))}
    </div>
  );
}
