"use client";

// Le guide de la visite : Iris, le marteau du bisse (suite 8, § 3), petite dans un coin, debout sur son manche et tournée
// vers l'information, une phrase par temps, et « Une question ? » avec six réponses préparées par l'équipe (guide.ts).
// Ses gestes : ses yeux se tournent vers la scène ; quand le point se pose sur une carte (« Repéré »), un petit coup de
// tête ; quand le visiteur choisit, ses yeux deviennent contents. Rien à saisir, rien d'envoyé. Masquable (« Options »,
// et la fenêtre des notes du présentateur) ; immobile quand le mouvement est réduit. L'ancienne Iris (la sphère) est
// dans les notes de travail (non publiées).
import { useEffect, useRef, useState } from "react";
import { IrisPetite, type Humeur } from "@/iris/IrisPetite";
import type { MondaysData } from "@/presentation/mondayData";
import { GUIDE_COPY, QUESTIONS, reponse, sourcesAnswer, type QuestionGuide } from "./guide";

export const PREF_GUIDE = "proxsis.visite.guide"; // « off » : le guide est masqué (sur cet appareil)

export function Guide({ lang, temps, mondays, decisions, repere, immobile }: {
  lang: "fr" | "de"; temps: 1 | 2 | 3 | 4 | 5 | 6; mondays: MondaysData;
  decisions: number; // le nombre de choix du visiteur dans le carnet : à chaque nouveau choix, des yeux contents
  repere: string; // la cible où le point vient de se poser (« Repéré ») : un petit coup de tête
  immobile: boolean;
}) {
  const g = GUIDE_COPY[lang];
  const [ouvert, setOuvert] = useState(false);
  const [question, setQuestion] = useState<QuestionGuide | null>(null);
  const reponseRef = useRef<HTMLHeadingElement>(null);
  const premiereRef = useRef<HTMLButtonElement>(null);
  const phrase = g.phrases[temps];
  const [humeur, setHumeur] = useState<Humeur>("calme");
  const [toc, setToc] = useState(0);
  const avant = useRef(decisions);

  // un nouveau choix : ses yeux deviennent contents, deux secondes
  useEffect(() => {
    if (decisions <= avant.current) { avant.current = decisions; return; }
    avant.current = decisions;
    setHumeur("contente");
    const t = window.setTimeout(() => setHumeur("calme"), 2000);
    return () => window.clearTimeout(t);
  }, [decisions]);
  // le point se pose sur une carte (Lumiere, après 0,42 s) : elle frappe en même temps
  useEffect(() => {
    if (!repere) return;
    const t = window.setTimeout(() => setToc((n) => n + 1), immobile ? 0 : 420);
    return () => window.clearTimeout(t);
  }, [repere, immobile]);

  useEffect(() => { if (question) reponseRef.current?.focus(); else if (ouvert) premiereRef.current?.focus(); }, [question, ouvert]);
  useEffect(() => {
    if (!ouvert) return;
    const echap = (e: KeyboardEvent) => { if (e.key === "Escape") { setOuvert(false); setQuestion(null); } };
    window.addEventListener("keydown", echap);
    return () => window.removeEventListener("keydown", echap);
  }, [ouvert]);

  return (
    <aside className="v-guide" aria-label={g.label} data-testid="guide">
      <IrisPetite hauteur={96} humeur={question === "sources" ? "inquiete" : humeur} toc={toc} immobile={immobile} label={g.still} />
      <div className="v-guide-body">
        <p className="v-guide-phrase" data-testid="guide-phrase">{phrase}</p>
        <button type="button" className="v-guide-ask" aria-expanded={ouvert} aria-controls="v-guide-panel" data-testid="guide-ask"
          onClick={() => { setOuvert((o) => !o); setQuestion(null); }}>{g.ask}</button>
      </div>
      {ouvert ? (
        <section id="v-guide-panel" className="v-guide-panel" aria-label={g.ask} data-testid="guide-panel">
          {question ? (
            <div className="v-guide-answer" data-testid="guide-answer">
              <h3 className="d-small" tabIndex={-1} ref={reponseRef}>{g.questions[question].q}</h3>
              <p>{reponse(question, lang, mondays)}</p>
              {question === "sources" ? <p className="d-small" data-testid="guide-sources-carte">{sourcesAnswer(lang)}</p> : null}
              <button type="button" className="v-link d-small" onClick={() => setQuestion(null)}>{g.others}</button>
            </div>
          ) : (
            <ul className="v-guide-questions">
              {QUESTIONS.map((k, i) => (
                <li key={k}>
                  <button type="button" className="v-guide-q" ref={i === 0 ? premiereRef : undefined} data-testid={`guide-q-${k}`}
                    onClick={() => setQuestion(k)}>{g.questions[k].q}</button>
                </li>
              ))}
            </ul>
          )}
          <div className="v-guide-foot">
            <p className="d-small d-muted" data-testid="guide-prepared">{g.prepared}</p>
            <button type="button" className="v-link d-small" onClick={() => { setOuvert(false); setQuestion(null); }}>{g.close}</button>
          </div>
        </section>
      ) : null}
    </aside>
  );
}
