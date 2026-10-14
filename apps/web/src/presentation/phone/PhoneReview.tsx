"use client";

// Review page of the piloted phone (/[lang]/presentation/telephone): graphite, the phone in the middle, ← → drive
// the steps, the presenter can take over. The same frame as the presentation (direction.css). With « ?video=1 »
// (recording of the backup video), every gesture gets a soft zoom of the whole page towards the finger.
import "../direction.css";
import "@/visite/visite.css"; // the same order everywhere: direction, visit, identity (see Frame.tsx)
import "@/visite/identite.css";
import "./phone.css";
import Link from "next/link";
import { ArrowLeft, ArrowRight } from "lucide-react";
import { animate, MotionConfig, motion, useMotionValue } from "motion/react";
import { useCallback, useEffect, useRef, useState, useSyncExternalStore } from "react";
import { useStoredString } from "@/lib/useStored";
import { DUR, T } from "../motion";
import { PREF_MOTION, PREF_PROJECTION, setPref } from "../prefs";
import { PButton } from "../ui";
import { COPY } from "../copy";
import { PHONE_COPY } from "./copy";
import { PhoneDemo, type GestureEvent } from "./PhoneDemo";
import { SCRIPT, clampStep, type PLang } from "./script";
import { Logo } from "@/lib/Logo";

const pad = (n: number) => String(n).padStart(2, "0");
const ZOOM = 1.45; // soft: the phone stays in its context
const SUMMARY_ZOOM = 1.3;
const noSubscribe = () => () => {};

export function PhoneReview({ lang }: { lang: PLang }) {
  const t = PHONE_COPY[lang];
  const other = lang === "fr" ? "de" : "fr";
  const [step, setStep] = useState(0);
  const [paused, setPaused] = useState(false);
  const motionPref = useStoredString(PREF_MOTION, "on");
  const projection = useStoredString(PREF_PROJECTION, "off");
  const video = useSyncExternalStore(noSubscribe, () => new URLSearchParams(window.location.search).has("video"), () => false);
  const still = motionPref === "off";
  const last = SCRIPT.length - 1;
  const id = SCRIPT[step].id;
  const zoom = useMotionValue(1);
  const originX = useMotionValue(0.5);
  const originY = useMotionValue(0.5);
  const demoRef = useRef<HTMLDivElement>(null);

  const move = useCallback((n: number) => {
    setPaused(false);
    setStep(clampStep(n));
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const el = e.target as HTMLElement | null;
      if (el && (el.tagName === "BUTTON" || el.tagName === "A") && (e.key === " " || e.key === "Enter")) return;
      const fwd = e.key === "ArrowRight" || e.key === "PageDown" || e.key === " ";
      const back = e.key === "ArrowLeft" || e.key === "PageUp";
      if (fwd || back) {
        e.preventDefault();
        if (paused) setPaused(false); // first arrow after a take-over: the demo resumes where it was
        else setStep((s) => clampStep(s + (fwd ? 1 : -1)));
      } else if (e.key === "Home") {
        e.preventDefault();
        move(0);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [paused, move]);

  // the camera follows the finger (recording only): one curve, the long duration, then back
  const onGesture = useCallback((g: GestureEvent) => {
    const box = demoRef.current?.getBoundingClientRect();
    if (!box) return;
    if (g.phase === "start") {
      originX.set((box.left + g.x * box.width) / window.innerWidth);
      originY.set((box.top + g.y * box.height) / window.innerHeight);
      animate(zoom, ZOOM, T.long);
    } else {
      animate(zoom, 1, { ...T.long, delay: DUR.long });
    }
  }, [originX, originY, zoom]);

  // the summary is read on the phone itself: the camera comes closer once it is open (recording only)
  useEffect(() => {
    const box = demoRef.current?.getBoundingClientRect();
    if (!video || step !== last || !box) return;
    originX.set((box.left + box.width / 2) / window.innerWidth);
    originY.set((box.top + box.height * 0.45) / window.innerHeight);
    const c = animate(zoom, SUMMARY_ZOOM, { ...T.long, delay: DUR.long });
    return () => {
      c.stop();
      animate(zoom, 1, T.long);
    };
  }, [video, step, last, originX, originY, zoom]);

  const s = t.steps[id];
  const brand = COPY[lang].dir; // the name, its signature and its mention (DESIGN.md § 4 ter)
  return (
    <MotionConfig reducedMotion={still ? "always" : "user"}>
      <motion.div className="dir" lang={lang === "de" ? "de-CH" : "fr-CH"} data-projection={projection}
        data-video={video ? "on" : "off"} style={video ? { scale: zoom, originX, originY } : undefined}>
        <header className="d-head" aria-label={COPY[lang].controls.head}>
          <div className="d-brand-block">
            <p className="d-brand"><Logo title={brand.name} /></p>
            <p className="d-small d-muted">{brand.signature}</p>
            <p className="d-proto">{brand.prototype}</p>
          </div>
          <div className="d-head-right">
            <div className="d-head-title">
              <p className="d-caps">{t.review.title}</p>
            </div>
            <Link className="d-tool" href={`/${other}/presentation/telephone/`} hrefLang={other}>{t.review.language}</Link>
            <PButton variant="tool" aria-pressed={still} onClick={() => setPref(PREF_MOTION, still ? "on" : "off")}>
              {still ? t.review.motion : t.review.still}
            </PButton>
          </div>
        </header>

        <main className="d-main" aria-label={t.review.title}>
          <div className="ph-review">
            <div className="ph-review-text" data-testid="review-caption" aria-live="polite">
              <p className="d-label">{pad(step + 1)} — {t.review.kicker}</p>
              <h1 className="d-statement">{s.label}</h1>
              <p className="d-lead">{s.caption}</p>
              <p className="ph-mentions">{s.mention.map((m) => <span key={m}>{m}</span>)}</p>
            </div>
            <div className="ph-review-phone" ref={demoRef}>
              <PhoneDemo lang={lang} step={step} onStepChange={move} still={still} paused={paused}
                onTakeOver={() => setPaused(true)} onResume={() => setPaused(false)} onGesture={video ? onGesture : undefined} />
            </div>
            <ol className="ph-steps" aria-label={t.review.route}>
              {SCRIPT.map((x, i) => (
                <li key={x.id}>
                  <PButton variant="option" aria-current={i === step ? "step" : undefined} onClick={() => move(i)}>
                    <span>{t.steps[x.id].label}</span>
                    <small className="d-num" aria-hidden>{pad(i + 1)}</small>
                  </PButton>
                </li>
              ))}
            </ol>
          </div>
        </main>

        <footer className="d-foot" aria-label={COPY[lang].controls.foot}>
          <nav className="d-nav" aria-label={t.review.route}>
            <div className="flex items-center gap-[clamp(14px,1.6vw,32px)]">
              <PButton variant="nav" onClick={() => move(step - 1)} disabled={step === 0}>
                <ArrowLeft className="back" aria-hidden /> {t.review.prev}
              </PButton>
              <p className="d-count d-num" data-testid="review-step">
                {pad(step + 1)} <span className="of">/ {pad(SCRIPT.length)}</span>
                <span className="sr-only"> · {t.review.step.replace("{n}", String(step + 1)).replace("{total}", String(SCRIPT.length))}</span>
              </p>
            </div>
            <span />
            <PButton variant="nav" className="justify-self-end" onClick={() => move(step + 1)} disabled={step === last}>
              {t.review.next} <ArrowRight className="fwd" aria-hidden />
            </PButton>
          </nav>
          <div className="d-mentions">
            <p className="ph-hint">{t.review.keys}</p>
          </div>
        </footer>
      </motion.div>
    </MotionConfig>
  );
}
