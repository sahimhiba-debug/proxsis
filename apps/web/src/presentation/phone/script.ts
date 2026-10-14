// The piloted phone demo (C2): the real consultant app at mobile size, one gesture per arrow, following the guided
// dossier. Pure data and pure decisions here (tested); the DOM and Motion live in PhoneDemo.tsx.
import { T } from "../motion";

export type PLang = "fr" | "de";
export type StepId = "semaine" | "dossier" | "appel" | "synthese";

/** The guided dossier (dossiers.json) and the fictional consultant whose Monday list ranks it first. */
export const GUIDED = "ent-1ef761b229";
export const CONSULTANT = "M1";

type Gesture =
  | { kind: "tap"; target: string } // touch a [data-demo] element of the page shown
  | { kind: "open" }; // the page opens on its own (the director finds the summary on his phone)

interface PhoneStep {
  id: StepId;
  path: string; // under /{lang}
  gesture: Gesture | null; // the gesture that leads INTO this step, played on the previous step's page
}

export const SCRIPT: PhoneStep[] = [
  { id: "semaine", path: `/semaine/${CONSULTANT}/`, gesture: null },
  { id: "dossier", path: `/entreprise/${GUIDED}/`, gesture: { kind: "tap", target: `ouvrir-${GUIDED}` } },
  { id: "appel", path: `/entreprise/${GUIDED}/appel/`, gesture: { kind: "tap", target: "preparer-appel" } },
  // no call feedback is touched: the demo never records anything (the decision is the director's, on the big screen)
  { id: "synthese", path: "/presentation/synthese/", gesture: { kind: "open" } },
];

export const clampStep = (n: number) => Math.max(0, Math.min(SCRIPT.length - 1, Math.round(n)));

export function urlFor(step: number, lang: PLang): string {
  return `/${lang}${SCRIPT[clampStep(step)].path}`;
}

type Move = { kind: "none" | "gesture" | "jump"; to: number };

/** From what the phone shows to the asked step: one step forward plays its gesture; anything else jumps. */
export function plan(shown: number | null, asked: number): Move {
  const to = clampStep(asked);
  if (shown === to) return { kind: "none", to };
  if (shown !== null && to === shown + 1 && SCRIPT[to].gesture) return { kind: "gesture", to };
  return { kind: "jump", to };
}

const norm = (p: string) => (p.endsWith("/") ? p : `${p}/`);

/** The step whose page is open (the current step first when two steps share a page), or null. */
export function stepOfPath(pathname: string, lang: PLang, current: number): number | null {
  if (!pathname) return null;
  const p = norm(pathname);
  if (urlFor(current, lang) === p) return clampStep(current);
  const i = SCRIPT.findIndex((_, k) => urlFor(k, lang) === p);
  return i < 0 ? null : i;
}

/** « rgb(…) », « oklch(…) » or a hex colour: is it dark? (to write the status bar in ivory). */
export function isDark(color: string): boolean {
  const ok = /oklch\(\s*([\d.]+)(%?)/i.exec(color);
  if (ok) return (ok[2] ? Number(ok[1]) / 100 : Number(ok[1])) < 0.6;
  const rgb = /rgba?\(\s*([\d.]+)[ ,]+([\d.]+)[ ,]+([\d.]+)/i.exec(color);
  const hex = /^#([0-9a-f]{6})$/i.exec(color);
  const [r, g, b] = rgb
    ? [Number(rgb[1]), Number(rgb[2]), Number(rgb[3])]
    : hex
      ? [0, 2, 4].map((i) => parseInt(hex[1].slice(i, i + 2), 16))
      : [255, 255, 255];
  return 0.2126 * r + 0.7152 * g + 0.0722 * b < 128;
}

// ---------------------------------------------------------------- geometry
// Frame of the Magic UI « iphone » mockup (MIT, see NOTICE.md), in its own units (1 unit = 1 CSS px at scale 1).
export const FRAME = { width: 433, height: 882, screenX: 21, screenY: 19, radius: 55.75 } as const;
// The screen: the app keeps its mobile width (390 px); the status bar sits under the Dynamic Island.
export const SCREEN = { width: 390, status: 54, app: 790 } as const;
const MAX_SCALE = 1.25; // never larger than legible: the phone stays a phone

/** Scale that fits the frame in a box, without distortion. */
export function fitScale(boxWidth: number, boxHeight: number): number {
  const k = Math.min(boxWidth / FRAME.width, boxHeight / FRAME.height);
  return Math.max(0.2, Math.min(MAX_SCALE, Number.isFinite(k) ? k : 1));
}

// ---------------------------------------------------------------- motion (one curve, three durations: motion.ts)
export const PHONE_MOTION = {
  fade: T.short, // the finger appears or the screen dims before a jump
  press: T.short, // the finger presses and releases
  ripple: T.medium, // the copper ring grows and fades
  reveal: T.medium, // the new page shows
  travel: T.long, // the finger moves to its target
  scroll: T.long, // the screen scrolls to the target
} as const;
