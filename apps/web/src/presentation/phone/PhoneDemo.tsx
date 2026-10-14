"use client";

// The real app in a phone, piloted by the presenter's arrows (C2 « démo vivante »). Real pages in a same-origin
// iframe, not a video: each step forward plays one gesture (the finger moves, touches, a copper wave, the page
// changes); anything else jumps straight to the asked state. `still` (or the system's reduced motion): the finger
// jumps, no wave, the page changes at once. Touching the screen hands it to the presenter; the pilot waits until
// « Reprendre la démo ». The arrows keep driving the presentation even when the focus is inside the phone.
import "../direction.css";
import "./phone.css";
import { ArrowRight } from "lucide-react";
import { motion, useMotionValue, useReducedMotionConfig } from "motion/react";
import { useCallback, useEffect, useRef, useState } from "react";
import { PButton } from "../ui";
import { PHONE_COPY } from "./copy";
import { FINGER_REST, Pilot } from "./pilot";
import { PhoneFrame } from "./PhoneFrame";
import { FRAME, fitScale, urlFor, type PLang } from "./script";

/** A gesture of the pilot, as a fraction of the component's box (origin of a soft zoom, for the video). */
export interface GestureEvent {
  phase: "start" | "end";
  x: number;
  y: number;
}

interface PhoneDemoProps {
  lang: PLang;
  step: number; // from outside: the presenter's arrow
  onStepChange?: (step: number) => void; // the presenter, on resuming, left the phone on another step's page
  still?: boolean;
  paused?: boolean; // controlled pause (optional); otherwise the phone pauses itself when touched
  onTakeOver?: () => void;
  onResume?: () => void;
  onGesture?: (g: GestureEvent) => void;
  className?: string;
}

function StatusIcons() {
  return (
    <svg viewBox="0 0 27 13" aria-hidden>
      <rect x="0" y="8" width="3" height="5" rx="0.8" fill="currentColor" />
      <rect x="4.5" y="5.5" width="3" height="7.5" rx="0.8" fill="currentColor" />
      <rect x="9" y="3" width="3" height="10" rx="0.8" fill="currentColor" />
      <rect x="15" y="1.5" width="10" height="10" rx="2.5" fill="none" stroke="currentColor" strokeWidth="1.2" />
      <rect x="16.6" y="3.1" width="6.8" height="6.8" rx="1.4" fill="currentColor" />
      <rect x="25.6" y="4.8" width="1.4" height="3.4" rx="0.7" fill="currentColor" />
    </svg>
  );
}

export function PhoneDemo({ lang, step, onStepChange, still = false, paused, onTakeOver, onResume, onGesture, className }: PhoneDemoProps) {
  const t = PHONE_COPY[lang];
  const reduced = useReducedMotionConfig();
  const isStill = still || Boolean(reduced);
  const [innerPaused, setInnerPaused] = useState(false);
  const isPaused = paused ?? innerPaused;
  const fx = useMotionValue(FINGER_REST.x);
  const fy = useMotionValue(FINGER_REST.y);
  const fo = useMotionValue(0);
  const fs = useMotionValue(1);
  const rx = useMotionValue(0);
  const ry = useMotionValue(0);
  const rs = useMotionValue(0.6);
  const ro = useMotionValue(0);
  const screen = useMotionValue(1);
  const [pilot] = useState(() => new Pilot({ fx, fy, fo, fs, rx, ry, rs, ro, screen }));
  const attach = useCallback((el: HTMLIFrameElement | null) => pilot.attach(el), [pilot]);
  const [src] = useState(() => urlFor(step, lang)); // never re-rendered: the pilot navigates
  const [shown, setShown] = useState<number | null>(null);
  const [finger, setFinger] = useState(false);
  const [ripple, setRipple] = useState(0);
  const [status, setStatus] = useState({ bg: "#ffffff", dark: false });
  const [size, setSize] = useState<{ w: number; h: number } | null>(null);
  const rootRef = useRef<HTMLDivElement>(null);
  const boxRef = useRef<HTMLDivElement>(null);
  const afterRef = useRef<HTMLDivElement>(null); // where « Passer le téléphone » sends the focus

  // the latest callbacks of the parent, without restarting the pilot
  const parent = useRef({ onTakeOver, onStepChange, onGesture });
  useEffect(() => {
    parent.current = { onTakeOver, onStepChange, onGesture };
  });

  useEffect(() => {
    pilot.on({
      shown: setShown,
      finger: setFinger,
      ripple: () => setRipple((n) => n + 1),
      status: (bg, dark) => setStatus({ bg, dark }),
      takeOver: () => {
        setInnerPaused(true);
        parent.current.onTakeOver?.();
      },
      adopt: (n) => parent.current.onStepChange?.(n),
      gesture: (phase, p) => {
        const root = rootRef.current;
        const box = boxRef.current;
        const onGesture = parent.current.onGesture;
        if (!onGesture || !root || !box) return;
        const k = fitScale(box.clientWidth, box.clientHeight);
        const left = box.offsetLeft + (box.clientWidth - FRAME.width * k) / 2;
        const top = box.offsetTop + (box.clientHeight - FRAME.height * k) / 2;
        onGesture({
          phase,
          x: (left + (FRAME.screenX + p.x) * k) / root.clientWidth,
          y: (top + (FRAME.screenY + p.y) * k) / root.clientHeight,
        });
      },
    });
  }, [pilot]);

  useEffect(() => {
    pilot.sync(step, lang, isStill, isPaused);
  }, [pilot, step, lang, isStill, isPaused]);

  useEffect(() => () => pilot.dispose(), [pilot]);

  useEffect(() => {
    const el = boxRef.current;
    if (!el) return;
    const ro = new ResizeObserver(([e]) => setSize({ w: e.contentRect.width, h: e.contentRect.height }));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const k = size ? fitScale(size.w, size.h) : 1;
  const resume = () => {
    setInnerPaused(false);
    onResume?.();
  };

  return (
    <div ref={rootRef} className={`ph-root ${className ?? ""}`} data-testid="phone-demo" data-shown={shown ?? ""}
      data-paused={isPaused}>
      {/* the phone is the real app, reachable with the keyboard; this link (visible on focus) jumps past it */}
      <button type="button" className="ph-skip" onClick={() => afterRef.current?.focus()}>{t.phone.skip}</button>
      <div ref={boxRef} className="ph-box">
        <div className="ph-sizer" style={{ width: FRAME.width * k, height: FRAME.height * k }}>
          <div className="ph-stage" data-measured={size ? "true" : "false"} style={{ transform: `scale(${k})` }}>
            <PhoneFrame label={t.phone.label} screen={status.bg}>
              <div className="ph-status" style={{ background: status.bg, color: status.dark ? "var(--texte)" : "#141414" }} aria-hidden>
                <span>{t.phone.clock}</span>
                <StatusIcons />
              </div>
              <motion.div style={{ opacity: screen }}>
                <iframe ref={attach} className="ph-app" src={src} title={t.phone.frameTitle} data-testid="phone-app" />
              </motion.div>
              {ripple ? (
                <motion.div className="ph-ripple" data-testid="ripple" aria-hidden
                  style={{ x: rx, y: ry, scale: rs, opacity: ro }} />
              ) : null}
              {finger ? (
                <motion.div className="ph-finger" data-testid="finger" aria-hidden
                  style={{ x: fx, y: fy, scale: fs, opacity: fo }} />
              ) : null}
            </PhoneFrame>
          </div>
        </div>
      </div>
      {/* fixed height: a touch never moves the phone between press and release */}
      <div className="ph-line" ref={afterRef} tabIndex={-1}>
        <p className="ph-legend">{t.phone.legend}</p>
        <div className="ph-pilot">
          <span className="sr-only" role="status">{isPaused ? t.pilot.paused : ""}</span>
          {isPaused ? (
            <PButton className="ph-resume" onClick={resume}>
              {t.pilot.resume} <ArrowRight aria-hidden />
            </PButton>
          ) : (
            <span className="ph-hint">{t.pilot.hint}</span>
          )}
        </div>
      </div>
    </div>
  );
}
