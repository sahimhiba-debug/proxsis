"use client";

import { motion } from "motion/react";
import { EASE, PULSE_REPEAT } from "./motion";

/** The dot of a dated signal on the vertical timeline; a signal of less than 14 days breathes in copper. */
export function PulseDot({ recent, label }: { recent: boolean; label?: string }) {
  return (
    <span className="fx-tl-dot" data-recent={recent} aria-label={recent ? label : undefined} role={recent ? "img" : undefined}>
      {recent ? ( /* hidden by CSS when motion is reduced */
        <motion.span className="fx-pulse" aria-hidden initial={{ opacity: 0.7, scale: 0.6 }} animate={{ opacity: 0, scale: 2.4 }}
          transition={{ duration: 1.8, ease: EASE, repeat: PULSE_REPEAT, repeatDelay: 0.6 }} />
      ) : null}
    </span>
  );
}
