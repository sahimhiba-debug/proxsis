"use client";

// The director's mode (brief of 07.10.2026, suite 2, § 5): « Quatre questions, quatre réponses ». Each answer is one
// sentence, then a way to the time of the visit that shows it. Opened from the bar of the five times, or from the first
// screen (its link ends with #questions). A dialog over the visit: Escape or « Fermer » closes it, the focus goes back.
import { motion } from "motion/react";
import { ArrowRight, X } from "lucide-react";
import { T } from "@/presentation/motion";
import { PButton } from "@/presentation/ui";
import { VISIT_COPY } from "./copy";
import type { StepId } from "./state";

export function QuatreQuestions({ lang, onGo, onClose }: { lang: "fr" | "de"; onGo: (to: StepId) => void; onClose: () => void }) {
  const t = VISIT_COPY[lang].questions;
  return (
    <motion.div className="v-sheet" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={T.short}
      role="dialog" aria-modal="true" aria-labelledby="v-questions-titre" data-testid="questions"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <motion.article className="d-paper v-questions" initial={{ y: 24 }} animate={{ y: 0 }} exit={{ y: 24 }} transition={T.medium}>
        <header className="v-questions-head">
          <h2 id="v-questions-titre">{t.title}</h2>
          <button className="v-questions-close" onClick={onClose} aria-label={t.close} autoFocus><X aria-hidden /></button>
        </header>
        <ol>
          {t.items.map((x, i) => (
            <li key={x.to} data-testid="question-item">
              <span className="v-questions-num d-num" aria-hidden>{i + 1}</span>
              <div>
                <h3>{x.q}</h3>
                <p>{x.a}</p>
                <PButton variant="paper" onClick={() => onGo(x.to)}>{t.go.replace("{where}", x.where)} <ArrowRight aria-hidden /></PButton>
              </div>
            </li>
          ))}
        </ol>
      </motion.article>
    </motion.div>
  );
}
