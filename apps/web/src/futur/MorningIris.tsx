"use client";

// Iris beside « Chaque matin, en direct de simap » (suite 10, § 2): a single toc when the section shows something new —
// the head strikes once when the section comes into view, and the sound plays only if it is on (it arms at the
// visitor's first gesture, like in the visit, and the same choice « Son : oui / coupé » holds on this device) —, once per
// reading on this device. Then she keeps watch one turn (her eyes blink) and stops, since there is text to read
// (suite 8, complement, § 8). Reduced motion: she does not move at all. Nothing here sends anything anywhere.
import { useReducedMotion } from "motion/react";
import { Volume2, VolumeX } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { IrisPetite } from "@/iris/IrisPetite";
import { PREF_SON, armerSon, jouerToc } from "@/iris/sons";
import { readStored, useStoredString, writeStored } from "@/lib/useStored";

const TOC_DONE = "proxsis.matin.toc"; // the reading whose toc was already played on this device
const ONE_TURN_MS = 5_000; // « elle veille » : one loop of five seconds, then she stops

export function MorningIris({ nouveau, lecture, label }: { nouveau: boolean; lecture: string | null; label: string }) {
  const ref = useRef<HTMLSpanElement>(null);
  const reduced = Boolean(useReducedMotion());
  const [toc, setToc] = useState(0);
  const [resting, setResting] = useState(false);

  // the sound never starts by itself: it arms at the visitor's first gesture on the page
  useEffect(() => {
    const arm = () => { armerSon(); window.removeEventListener("pointerdown", arm); window.removeEventListener("keydown", arm); };
    window.addEventListener("pointerdown", arm);
    window.addEventListener("keydown", arm);
    return () => { window.removeEventListener("pointerdown", arm); window.removeEventListener("keydown", arm); };
  }, []);

  // when the section comes into view: the toc if there is something new (once per reading), then one turn of watch
  useEffect(() => {
    const el = ref.current;
    if (!el || typeof IntersectionObserver === "undefined") return;
    let rest = 0;
    const seen = new IntersectionObserver(([entry]) => {
      if (!entry?.isIntersecting) return;
      seen.disconnect();
      if (nouveau && lecture && readStored(TOC_DONE) !== lecture) {
        writeStored(TOC_DONE, lecture);
        if (!reduced) setToc(1);
        jouerToc(); // plays only if the sound is armed and not cut
      }
      rest = window.setTimeout(() => setResting(true), ONE_TURN_MS);
    }, { threshold: 0.6 });
    seen.observe(el);
    return () => { seen.disconnect(); window.clearTimeout(rest); };
  }, [nouveau, lecture, reduced]);

  return (
    <span className="fx-matin-iris" ref={ref} data-testid="matin-iris" data-toc={toc || undefined} data-veille={!(reduced || resting) || undefined}>
      <IrisPetite hauteur={52} regard={[2, -1]} toc={toc} immobile={reduced || resting} label={label} />
    </span>
  );
}

/** « Son : oui / coupé », the same choice as in the visit, kept on this device. */
export function MorningSound({ nouveau, labels }: { nouveau: boolean; labels: { on: string; off: string; sound: string } }) {
  const sonOn = useStoredString(PREF_SON, "on") !== "off";
  return (
    <button type="button" className="fx-tool" aria-pressed={sonOn} aria-label={labels.sound} data-testid="matin-son"
      onClick={() => {
        armerSon();
        writeStored(PREF_SON, sonOn ? "off" : "on");
        if (!sonOn && nouveau) jouerToc(); // turned on while there is something new: the toc, once, as an answer
      }}>
      {sonOn ? <Volume2 aria-hidden className="size-4" strokeWidth={1.5} /> : <VolumeX aria-hidden className="size-4" strokeWidth={1.5} />}
      <span aria-hidden>{sonOn ? labels.on : labels.off}</span>
    </button>
  );
}
