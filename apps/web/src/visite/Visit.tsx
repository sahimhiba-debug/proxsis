"use client";

// The visit in five times (brief « à distance », § 4): it works without us, on any device. Each step: one sentence of
// narration, a prepared example, an action proposed but never required, and « Continuer ». The bar of the five times
// shows where one is; one can go back, skip a time, go straight to the conclusion, and come back later to the same
// place (the visit is kept on the device). A permanent general mention; a precise mention only next to a fictional
// person, a calculation or an interpretation; the simap mention where its data shows.
import "@/presentation/direction.css";
import "./visite.css";
import "./identite.css";
import Link from "next/link";
import { AnimatePresence, MotionConfig, motion, useReducedMotion } from "motion/react";
import { ArrowLeft, ArrowRight, ArrowUpRight, CircleHelp, Flag, Volume2, VolumeX } from "lucide-react";
import { useCallback, useEffect, useRef, useState, useSyncExternalStore, type ReactNode } from "react";
import { SEUIL_COPY, SEUIL_EXAMPLE, seuil } from "@/lib/seuil";
import type { FrozenMornings } from "@/lib/types";
import { useStoredString } from "@/lib/useStored";
import { PREF_SON, armerSon } from "@/iris/sons";
import { DateScene, type FirstTest } from "@/presentation/ChooseDate";
import { COPY } from "@/presentation/copy";
import { SimapLine } from "@/presentation/Frame";
import type { MondaysData } from "@/presentation/mondayData";
import { T } from "@/presentation/motion";
import { PREF_MOTION, setPref } from "@/presentation/prefs";
import { PButton } from "@/presentation/ui";
import { CarnetScene, type TenRow } from "./Carnet";
import { MatinFige } from "./MatinFige";
import { CarteScene } from "./Carte";
import { visitPath } from "./paths";
import { EXAMPLE_ENTRY, inAgencyOrder } from "./consultant";
import { exampleCarnet, type NextData } from "./next";
import { ConclusionScene } from "./Conclusion";
import { examplePilot } from "./pilot";
import { PiloteScene } from "./Pilote";
import { SeuilScene } from "./Seuil";
import { summaryRows } from "./summary";
import { SuivantScene } from "./Suivant";
import { VISIT_COPY } from "./copy";
import { DossierScene } from "./DossierScene";
import { GUIDE_COPY } from "./guide";
import { Guide, PREF_GUIDE } from "./GuideMascotte";
import { Lumiere, type PlanLumiere } from "./Lumiere";
import type { VisitDossier } from "./dossier";
import { TEMPS, VISIT_STEPS, type VisitAction, type VisitState } from "./state";
import type { TerritoryData } from "./territory";
import type { Proposer } from "./proposer";
import type { visitMoments } from "./moments";
import { Accelerent } from "./NouveauxMoments";
import { QuatreQuestions } from "./QuatreQuestions";
import { Avenir } from "./Avenir";
import { useResumed, useVisit } from "./useVisit";
import { Logo } from "@/lib/Logo";
import { Fort } from "./Fort";
import { sceneOf, usePassage } from "./passage";
import { HAUT_VALAIS } from "./valais";

export interface VisitData {
  lang: "fr" | "de";
  mondays: MondaysData;
  territory: TerritoryData;
  dossiers: Record<string, VisitDossier>; // every company of the map
  ten: TenRow[]; // the consultant's list of the Monday, in its order
  next: NextData; // the following Monday, same rule
  firstTest: FirstTest; // the scope of the confession (CLAIMS REEL-T0), another test than the measure of the date
  proposer: Record<string, Proposer>; // « Qui proposer ? »: three fictional temps per company of the map, when the app has them
  moments: ReturnType<typeof visitMoments>; // « Cette semaine », the facts of the guided dossiers, « celles qui accélèrent »
  around: Record<string, string[]>; // each agency's week in the application, in its order (B7)
  mornings: FrozenMornings; // « Choisissez une date »: « Chaque matin » of each Monday that can be chosen (suite 10, § 2)
}

const onHash = (cb: () => void) => {
  window.addEventListener("hashchange", cb);
  return () => window.removeEventListener("hashchange", cb);
};

function SourceSheet({ url, lang, onClose }: { url: string; lang: "fr" | "de"; onClose: () => void }) {
  const t = VISIT_COPY[lang].source;
  const [online, setOnline] = useState(true);
  useEffect(() => {
    const upd = () => setOnline(navigator.onLine);
    upd();
    window.addEventListener("online", upd);
    window.addEventListener("offline", upd);
    return () => {
      window.removeEventListener("online", upd);
      window.removeEventListener("offline", upd);
    };
  }, []);
  return (
    <motion.div className="v-sheet" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={T.short}
      role="dialog" aria-modal="true" aria-label={t.title}>
      <motion.article className="d-paper w-full max-w-3xl" initial={{ y: 24 }} animate={{ y: 0 }} exit={{ y: 24 }} transition={T.medium}>
        <header className="d-paper-head"><span>{t.title}</span></header>
        <p className="d-paper-meta break-all">{url}</p>
        {online ? (
          <a className="d-paper-link" href={url} target="_blank" rel="noopener noreferrer">{t.open} <ArrowUpRight aria-hidden /></a>
        ) : (
          <p className="d-paper-meta">{t.offline}</p>
        )}
        <p className="d-paper-meta"><SimapLine t={COPY[lang]} lang={lang} /></p>
        <PButton variant="paper" onClick={onClose} autoFocus><ArrowLeft aria-hidden /> {t.close}</PButton>
      </motion.article>
    </motion.div>
  );
}

interface Scene {
  body: ReactNode;
  mention?: ReactNode; // the precise mention of this scene, if any
  simap?: boolean; // the scene shows simap data: its mandatory mention is in the footer
}

function scene(data: VisitData, s: VisitState, dispatch: (a: VisitAction) => void): Scene {
  const lang = data.lang;
  const id = VISIT_STEPS[s.step].id;
  if (id === "carte") {
    return {
      simap: true,
      mention: VISIT_COPY[lang].carte.swisstopo,
      body: <CarteScene territory={data.territory} lang={lang} commune={s.commune} agence={s.agence}
        week={data.ten.map((x) => x.id)} around={data.around} thisWeek={data.moments.week} dispatch={dispatch} />,
    };
  }
  if (id === "dossier") {
    const company = s.company && data.dossiers[s.company] ? s.company : data.territory.exemple.entreprise;
    // the mandatory mention is on the paper itself (a paper without it could pass for an official publication, AGB API
    // simap ch. 5), so the foot does not repeat it: once per screen (brief « à distance », § 4)
    return {
      simap: false,
      body: <DossierScene d={data.dossiers[company]} lang={lang} example={company === data.territory.exemple.entreprise && !s.company}
        reveal={s.reveal} dispatch={dispatch}
        hautValais={company !== HAUT_VALAIS.entreprise ? data.dossiers[HAUT_VALAIS.entreprise] ?? null : null}
        who={data.proposer[company] ?? null}
        facts={data.moments.facts.dossiers[company] ?? null} factSources={data.moments.facts.sources} />,
    };
  }
  if (id === "carnet") {
    const company = s.company && data.dossiers[s.company] ? s.company : data.territory.exemple.entreprise;
    return {
      simap: true,
      // the consultant's Monday in the order of « Ma semaine » for the agency (Q17: one list, the same three first calls)
      body: <CarnetScene d={data.dossiers[company]} ten={inAgencyOrder(data.ten, data.around, s.agence)} monday={data.territory.lundi} lang={lang} own={s.carnet[company]}
        reveal={s.reveal} dispatch={dispatch} who={data.proposer[company] ?? null} />,
    };
  }
  if (id === "suivant") {
    // his decisions, else the prepared examples (the lead of time 1 handed over, one set aside, one to look at again)
    const opened = s.company && data.dossiers[s.company] ? s.company : data.territory.exemple.entreprise;
    const base = { ...exampleCarnet(data.next.lundi), [opened]: EXAMPLE_ENTRY };
    const names = Object.fromEntries([...data.ten.map((r) => [r.id, r.nom]), ...Object.values(data.dossiers).map((d) => [d.id, d.nom])]);
    return {
      simap: true,
      body: <SuivantScene data={data.next} rows={inAgencyOrder(data.ten, data.around, s.agence)} names={names} carnet={{ ...base, ...s.carnet }}
        examples={new Set(Object.keys(base).filter((k) => !s.carnet[k]))} lang={lang} reveal={s.reveal} dispatch={dispatch} />,
    };
  }
  if (id === "seuil") {
    return {
      mention: SEUIL_COPY[lang].mention,
      body: <SeuilScene lang={lang} value={s.seuil} half={s.half} dispatch={dispatch} />,
    };
  }
  if (id === "pilote") {
    const days = seuil(s.seuil ?? SEUIL_EXAMPLE, s.half).breakEvenDays;
    return {
      body: (
        <>
          <PiloteScene lang={lang} value={s.pilot} example={examplePilot(days)} dispatch={dispatch} />
          <Avenir lang={lang} id="v-avenir-decision" />
        </>
      ),
    };
  }
  if (id === "conclusion") {
    const rows = summaryRows({ lang, s, dossiers: data.dossiers, exampleCompany: data.territory.exemple.entreprise, mondays: data.mondays });
    return { simap: true, body: <ConclusionScene rows={rows} lang={lang} /> };
  }
  if (id === "date") {
    return {
      simap: true,
      body: <DateScene data={data.mondays} lang={lang} monday={s.monday} reveal={s.reveal} firstTest={data.firstTest} titleAs="h2"
        head={<p className="d-lead v-preuve" data-testid="preuve">{VISIT_COPY[lang].preuve}</p>}
        onMonday={(value) => dispatch({ type: "monday", value })} onReveal={(n) => dispatch({ type: "reveal", n })}
        onSource={(url) => dispatch({ type: "openSource", url })}
        afterResult={<Accelerent a={data.moments.accelerating} lang={lang} />}
        morning={(m) => <MatinFige data={data.mornings} monday={m.lundi} ten={m.dix.map((c) => c.id)} lang={lang}
          onSource={(url) => dispatch({ type: "openSource", url })} />} />,
    };
  }
  return { body: <p className="d-lead d-muted" data-testid="visit-pending">{VISIT_COPY[lang].pending}</p> };
}

/** Where the guide's light rests at each step (the prototype of reference: the target, then the next one, no line). */
function planLumiere(id: string, reveal: number): PlanLumiere {
  switch (id) {
    case "carte": return { visee: { cible: "repere", theme: "c", tag: "spotted" } };
    case "dossier": return reveal >= 1
      ? { visee: { cible: "question", theme: "c" } } // le fait publié, puis la question
      : { visee: { cible: "papier", theme: "p", tag: "spotted" } };
    case "suivant": return reveal >= 1
      ? { visee: { cible: "rappel", theme: "c", tag: "recall" } } // « Revoir le… », puis aujourd'hui
      : { visee: { cible: "revoir", theme: "c" } };
    default: return {};
  }
}

export function Visit({ data }: { data: VisitData }) {
  const lang = data.lang;
  const other = lang === "fr" ? "de" : "fr";
  const t = VISIT_COPY[lang];
  const brand = COPY[lang].dir; // the product's name, its signature and the prototype mention, as everywhere
  const [s, dispatch] = useVisit();
  const motionPref = useStoredString(PREF_MOTION, "on");
  const guideOn = useStoredString(PREF_GUIDE, "on") !== "off";
  const sonOn = useStoredString(PREF_SON, "on") !== "off";
  // le son ne part jamais tout seul : il s'arme au premier geste du visiteur (suite 8, § 5)
  useEffect(() => {
    const arme = () => { armerSon(); window.removeEventListener("pointerdown", arme); window.removeEventListener("keydown", arme); };
    window.addEventListener("pointerdown", arme);
    window.addEventListener("keydown", arme);
    return () => { window.removeEventListener("pointerdown", arme); window.removeEventListener("keydown", arme); };
  }, []);
  const reduced = useReducedMotion();
  const still = motionPref === "off" || Boolean(reduced);
  const step = VISIT_STEPS[s.step];
  const last = s.step === VISIT_STEPS.length - 1;
  const [options, setOptions] = useState(false);
  const resumed = useResumed(s.step); // « Vous reprenez là où vous vous étiez arrêté »
  const { go, bande } = usePassage(s, dispatch, motionPref !== "off"); // the orange band into the three dark moments
  // the director's mode (suite 2, § 5): four questions over the visit; the first screen opens it with #questions
  const [asked, setQuestions] = useState(false);
  const fromLink = useSyncExternalStore(onHash, () => window.location.hash === "#questions", () => false);
  const questions = asked || fromLink;
  const questionsBtn = useRef<HTMLButtonElement>(null);
  const closeQuestions = useCallback(() => {
    setQuestions(false);
    if (window.location.hash === "#questions") {
      window.history.replaceState(null, "", window.location.pathname + window.location.search);
      window.dispatchEvent(new HashChangeEvent("hashchange"));
    }
    questionsBtn.current?.focus({ preventScroll: true });
  }, []);

  // a new step opens at its top, its narration first (the sentence carries the visit for someone who only reads): the page
  // and the scene go back up, the focus moves to the narration (screen readers read it), and the bar of the five times
  // shows the current one (on a phone it scrolls sideways). Then what a gesture reveals is brought into view (on a small
  // screen the scene scrolls), without motion when asked.
  const mainRef = useRef<HTMLElement>(null);
  const shownStep = useRef(s.step);
  const focusNarration = useRef(false);
  useEffect(() => {
    if (shownStep.current !== s.step) {
      shownStep.current = s.step;
      window.scrollTo({ top: 0, behavior: "auto" });
      mainRef.current?.scrollTo({ top: 0, behavior: "auto" });
      focusNarration.current = true;
      const bar = document.querySelector<HTMLElement>(".v-progress");
      const current = bar?.querySelector<HTMLElement>("[aria-current=step]");
      if (bar && current && bar.scrollWidth > bar.clientWidth) {
        bar.scrollTo({ left: current.offsetLeft - (bar.clientWidth - current.offsetWidth) / 2, behavior: "auto" });
      }
      return;
    }
    if (s.reveal === 0) return;
    const last = [...document.querySelectorAll<HTMLElement>("main [data-revealed]")].at(-1);
    if (!last) return;
    // only when its beginning is out of sight: a scene whose new part already starts on screen does not move
    const top = last.getBoundingClientRect().top;
    if (top > 0 && top < window.innerHeight * 0.8) return;
    last.scrollIntoView({ block: "start", behavior: motionPref === "off" ? "auto" : "smooth" });
  }, [s.step, s.reveal, motionPref]);

  // on a computer the scene scrolls inside the frame: when it goes on below, the bottom fades (« there is more »)
  useEffect(() => {
    const main = mainRef.current;
    if (!main) return;
    const update = () => main.toggleAttribute("data-more", main.scrollHeight - main.clientHeight - main.scrollTop > 8);
    update();
    const ro = new ResizeObserver(update);
    ro.observe(main);
    for (const child of main.children) ro.observe(child);
    main.addEventListener("scroll", update, { passive: true });
    return () => { ro.disconnect(); main.removeEventListener("scroll", update); };
  }, [s.step, s.reveal]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const el = e.target as HTMLElement | null;
      if (el && (el.tagName === "INPUT" || el.tagName === "TEXTAREA" || el.tagName === "SELECT")) return;
      if (el && (el.tagName === "BUTTON" || el.tagName === "A") && (e.key === " " || e.key === "Enter")) return;
      if (questions) {
        if (e.key === "Escape") closeQuestions();
        return;
      }
      if (s.source) {
        if (e.key === "Escape") dispatch({ type: "closeSource" });
        return;
      }
      if (e.key === "ArrowRight" || e.key === "PageDown") { e.preventDefault(); go({ type: "next" }); }
      else if (e.key === "ArrowLeft" || e.key === "PageUp") { e.preventDefault(); go({ type: "prev" }); }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [dispatch, go, s.source, questions, closeQuestions]);

  const sc = scene(data, s, dispatch);
  return (
    <MotionConfig reducedMotion={motionPref === "off" ? "always" : "user"}>
      <div className="dir v-visit" data-motion={motionPref} data-scene={sceneOf(s.step)} data-guide={guideOn ? "on" : undefined}
        lang={lang === "de" ? "de-CH" : "fr-CH"}>
        {bande ? <div key={bande} className="px-bande" aria-hidden data-testid="bande" /> : null}
        <header className="d-head relative" aria-label={t.nav.head}>
          <div className="d-brand-block">
            <p className="d-brand"><Logo title={brand.name} /></p>
            <p className="d-small d-muted">{brand.signature}</p>
            <p className="d-proto">{brand.prototype}</p>
          </div>
          <div className="d-head-right">
            <button type="button" className="d-tool v-son" aria-pressed={sonOn} data-testid="son"
              aria-label={t.nav.sound}
              onClick={() => { armerSon(); setPref(PREF_SON, sonOn ? "off" : "on"); }}>
              {sonOn ? <Volume2 aria-hidden /> : <VolumeX aria-hidden />}<span className="v-son-texte" aria-hidden>{sonOn ? t.nav.soundOn : t.nav.soundOff}</span>
            </button>
            <Link className="d-tool" href={visitPath(other)} hrefLang={other}>{t.nav.language}</Link>
            <PButton variant="tool" onClick={() => setOptions((v) => !v)} aria-expanded={options} aria-controls="v-options">
              {t.nav.options} ⋯
            </PButton>
          </div>
          {options ? (
            <div id="v-options" className="d-menu">
              <button onClick={() => window.open(visitPath(lang, "notes"), "proxsis-notes", "width=900,height=700")}>{t.nav.presenter}</button>
              <button aria-pressed={motionPref === "off"} onClick={() => setPref(PREF_MOTION, motionPref === "off" ? "on" : "off")}>{t.nav.motion}</button>
              <button onClick={() => setPref(PREF_GUIDE, guideOn ? "off" : "on")} data-testid="guide-toggle">
                {guideOn ? GUIDE_COPY[lang].hide : GUIDE_COPY[lang].show}
              </button>
              <button onClick={() => { if (window.confirm(t.nav.resetConfirm)) { dispatch({ type: "reset" }); setOptions(false); } }}>{t.nav.reset}</button>
              <div className="mt-3 border-t border-[var(--trait)] pt-3 d-small d-muted" data-testid="privacy">
                <p>{t.privacy.sent}</p>
                <p className="mt-1">{t.privacy.kept}</p>
                <p className="mt-1">{t.privacy.share}</p>
              </div>
            </div>
          ) : null}
        </header>

        <nav className="v-progress" aria-label={t.nav.progress}>
          <ol>
            {TEMPS.map((tp) => (
              <li key={tp}>
                <button aria-current={tp === step.temps ? "step" : undefined} data-done={tp < step.temps || undefined}
                  onClick={() => go({ type: "temps", temps: tp })}>
                  {tp < 6 ? <span className="d-num">{tp}</span> : <Flag className="v-step-icon" aria-hidden />}
                  <span className="v-step-label">{t.temps[tp]}</span>
                </button>
              </li>
            ))}
            <li>
              <button ref={questionsBtn} onClick={() => setQuestions(true)} aria-haspopup="dialog" data-testid="open-questions"
                className="v-questions-btn">
                <CircleHelp className="v-step-icon" aria-hidden />
                <span className="v-step-label">{t.questions.open}</span>
              </button>
            </li>
          </ol>
          {/* au téléphone, la barre ne montre que les numéros : le nom du temps courant, entier, sur sa propre ligne */}
          <p className="v-progress-courant" aria-hidden="true">{step.temps < 6 ? `${step.temps} · ` : ""}{t.temps[step.temps]}</p>
        </nav>

        <main className="d-main v-main" aria-label={t.temps[step.temps]} ref={mainRef}>
          {resumed ? <p className="d-small d-muted" role="status">{t.nav.resumed}</p> : null}
          {guideOn ? (
            <Guide lang={lang} temps={step.temps as 1 | 2 | 3 | 4 | 5 | 6} mondays={data.mondays} immobile={still}
              decisions={Object.keys(s.carnet).length}
              repere={planLumiere(step.id, s.reveal).visee?.tag === "spotted" ? `${step.id}-${s.reveal}` : ""} />
          ) : null}
          <AnimatePresence mode="wait">
            <motion.div key={step.id} className="v-scene" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={T.short}>
              {step.id === "carte" ? (
                <p className="v-moment" data-testid="moment">
                  <span>{t.moment.market} <span className="d-muted">({t.moment.source})</span></span>
                  <span className="block">{t.moment.trade}</span>
                </p>
              ) : null}
              <h1 className="v-narration v-miroir" data-testid="narration" tabIndex={-1} ref={(el) => {
                if (el && focusNarration.current) { focusNarration.current = false; el.focus({ preventScroll: true }); }
              }}><Fort text={t.narration[step.id]} strong={t.strong[step.id]} /></h1>
              {sc.body}
            </motion.div>
          </AnimatePresence>
          {guideOn ? <Lumiere plan={planLumiere(step.id, s.reveal)} lang={lang} immobile={still} cle={step.id} /> : null}
          <AnimatePresence>{s.source ? <SourceSheet url={s.source} lang={lang} onClose={() => dispatch({ type: "closeSource" })} /> : null}</AnimatePresence>
        </main>

        <footer className="d-foot" aria-label={t.nav.foot}>
          <div className="d-mentions">
            <p data-testid="general-mention">
              {t.mentions.general}{sc.mention ? <> · {sc.mention}</> : null}{sc.simap ? <> · <SimapLine t={COPY[lang]} lang={lang} /></> : null}
              {t.mentions.review ? <> · <span data-testid="review-mention">{t.mentions.review}</span></> : null}
            </p>
          </div>
          <nav className="d-nav" aria-label={t.nav.move}>
            <div className="flex items-center gap-[clamp(14px,1.6vw,32px)]">
              <PButton variant="nav" onClick={() => go({ type: "prev" })} disabled={s.step === 0 && s.reveal === 0}>
                <ArrowLeft className="back" aria-hidden /> {t.nav.prev}
              </PButton>
              <p className="d-count d-num" data-testid="visit-step">
                {step.temps < 6 ? t.nav.of.replace("{n}", String(step.temps)) : t.temps[6]}
              </p>
            </div>
            {last ? <span /> : (
              <PButton variant="quiet" className="justify-self-center" onClick={() => go({ type: "temps", temps: 6 })}>{t.nav.conclusion}</PButton>
            )}
            <PButton variant="nav" className="justify-self-end" onClick={() => go({ type: "next" })} disabled={last}>
              {t.nav.next} <ArrowRight className="fwd" aria-hidden />
            </PButton>
          </nav>
        </footer>
        {/* over the whole window, outside the scene's frame (which would clip it) */}
        <AnimatePresence>
          {questions ? (
            <QuatreQuestions lang={lang} onClose={closeQuestions}
              onGo={(to) => { closeQuestions(); go({ type: "goto", step: VISIT_STEPS.findIndex((x) => x.id === to) }); }} />
          ) : null}
        </AnimatePresence>
      </div>
    </MotionConfig>
  );
}
