// Le point du « i » de Proxsis (suite 8, § 4) : les lettres montent depuis la ligne de base, l'une après l'autre, le
// « i » sans son point ; Iris entre, petite, et frappe juste à l'endroit du point : toc, une petite onde orange ; quand
// elle se relève, la diagonale orange est posée, avec un léger rebond ; elle s'efface, et plus rien ne bouge.
// Environ 2,2 s. Deux façons de poser le point : « tampon » (il apparaît sous la tête, révélé quand elle se relève) et
// « chute » (il tombe de la tête sur le « i »). Sans mouvement : le logo complet, le point posé, pas d'Iris.
// Tout est dans le repère du logo (VIEWBOX) : la même animation sert au premier écran, au film et au diaporama.
import { DOT, DOT_BOX, LETTERS, VIEWBOX } from "./logo-paths.js";
import { EYES, PIVOT } from "./scene.js";

const NS = "http://www.w3.org/2000/svg";
const ORANGE = "#E6530F";
const GLOW = "#FFF4D8";
const HEAD_BOTTOM = { x: 345, y: 497 }; // le milieu du dessous de la tête, au repos (repère de la scène, 1024 px)
const HEAD_WIDTH = 410; // largeur de la tête dans la scène
const DOT_W = DOT_BOX.x1 - DOT_BOX.x0;
const DOT_CX = (DOT_BOX.x0 + DOT_BOX.x1) / 2, DOT_CY = (DOT_BOX.y0 + DOT_BOX.y1) / 2;

function n(tag, attrs = {}, parent) {
  const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, String(v));
  if (parent) parent.appendChild(e);
  return e;
}

/**
 * Construit le logo animé dans `container` (un SVG à la largeur du conteneur).
 * Options : base (dossier des calques d'Iris), ext, variant (« tampon » | « chute »), color (couleur des lettres),
 * reduced (sans mouvement : logo complet tout de suite), title (nom lu par les lecteurs d'écran), attente (secondes
 * entre les lettres posées et l'entrée d'Iris : 0 sur le site ; le film l'allonge pour que le toc tombe sur la voix).
 * Renvoie { svg, tl, tocs, duration } ; le fil est en pause (l'appelant le lance une seule fois).
 */
export function createLogoIris(container, { gsap, base, ext = "png", variant = "tampon", color = "currentColor", reduced = false, title = "Proxsis", attente = 0 }) {
  const svg = n("svg", { viewBox: VIEWBOX, role: "img", "aria-label": title, class: "px-logo-iris", overflow: "visible", style: "display:block;width:100%;height:auto;overflow:visible" }, container);
  const defs = n("defs", {}, svg);
  const clip = n("clipPath", { id: `px-rise-${Math.random().toString(36).slice(2, 8)}` }, defs);
  n("rect", { x: -200, y: -2400, width: 7000, height: 2440 }, clip); // tout ce qui est au-dessus de la ligne de base (+40)
  const glowId = `px-glow-${Math.random().toString(36).slice(2, 8)}`;
  const f = n("filter", { id: glowId, x: "-80%", y: "-80%", width: "260%", height: "260%" }, defs);
  n("feGaussianBlur", { stdDeviation: "3.2", result: "b" }, f);
  const mg = n("feMerge", {}, f); n("feMergeNode", { in: "b" }, mg); n("feMergeNode", { in: "SourceGraphic" }, mg);

  const letters = n("g", { fill: color, "clip-path": `url(#${clip.id})` }, svg);
  const paths = LETTERS.map((d) => n("path", { d }, letters));
  const rings = [0, 1].map(() => n("circle", { cx: DOT_CX, cy: DOT_CY, r: 0, fill: "none", stroke: ORANGE, "stroke-width": 26, opacity: 0 }, svg));
  const dot = n("path", { d: DOT, fill: ORANGE }, svg);

  // Iris, petite : la tête et son manche, ses yeux ; mise à l'échelle pour que sa tête fasse 1,75 fois le point
  const s = (DOT_W * 2.1) / HEAD_WIDTH;
  const tx = DOT_CX - HEAD_BOTTOM.x * s, ty = DOT_BOX.y0 - HEAD_BOTTOM.y * s; // au contact (angle 0), la tête touche le point
  const px = tx + PIVOT.x * s, py = ty + PIVOT.y * s; // le pivot (le bout du manche), dans le repère du logo
  const outer = n("g", { opacity: 0 }, svg);
  const swing = n("g", {}, outer);
  const body = n("g", { transform: `translate(${tx} ${ty}) scale(${s})` }, swing);
  n("image", { href: `${base}tete.${ext}`, x: 0, y: 0, width: 1024, height: 1024 }, body);
  const eyes = EYES.map((e) => n("image", { href: `${base}${e.name}.${ext}`, x: e.x, y: e.y, width: e.w, height: e.h }, body));
  const happy = EYES.map((e) => n("path", { d: "M -15 7 Q 0 -17 15 7", fill: "none", stroke: GLOW, "stroke-width": 8.5, "stroke-linecap": "round",
    filter: `url(#${glowId})`, opacity: 0, transform: `translate(${e.cx} ${e.cy - 4})` }, body));

  const S = { rise: 0, iris: 0, angle: 34, dx: 820, dy: -620, blink: 0, happy: 0, r1: -1, r2: -1, dotOn: 0, dotPop: 1, dotY: 0 };
  const render = () => {
    paths.forEach((p, i) => {
      const t = Math.max(0, Math.min(1, (S.rise * 0.63 - i * 0.035) / 0.42));
      const e = 1 - Math.pow(1 - t, 3);
      p.setAttribute("transform", `translate(0 ${(1 - e) * 620})`);
      p.setAttribute("opacity", String(Math.min(1, t * 1.6)));
    });
    outer.setAttribute("opacity", String(S.iris));
    outer.setAttribute("transform", `translate(${S.dx} ${S.dy})`);
    swing.setAttribute("transform", `rotate(${S.angle} ${px} ${py})`);
    eyes.forEach((e, i) => {
      const { cx, cy } = EYES[i], k = Math.max(0.06, 1 - S.blink);
      e.setAttribute("transform", `translate(${cx} ${cy}) scale(1 ${k}) translate(${-cx} ${-cy})`);
      e.setAttribute("opacity", String(1 - S.happy));
    });
    happy.forEach((h) => h.setAttribute("opacity", String(S.happy)));
    rings.forEach((r, i) => {
      const p = i === 0 ? S.r1 : S.r2;
      if (p < 0 || p > 1) { r.setAttribute("opacity", "0"); return; }
      r.setAttribute("r", String(170 + p * 620));
      r.setAttribute("stroke-width", String(30 - 22 * p));
      r.setAttribute("opacity", String(0.9 * Math.pow(1 - p, 1.3)));
    });
    dot.setAttribute("opacity", String(S.dotOn));
    dot.setAttribute("transform", `translate(${DOT_CX} ${DOT_BOX.y1 + S.dotY}) scale(${1 + (S.dotPop - 1) * 0.6} ${S.dotPop}) translate(${-DOT_CX} ${-DOT_BOX.y1})`);
  };

  if (reduced) {
    Object.assign(S, { rise: 1, iris: 0, dotOn: 1, dotPop: 1, dotY: 0 });
    render();
    return { svg, tl: gsap.timeline({ paused: true }), tocs: [], duration: 0, render };
  }

  const T_HIT = 1.1 + attente;
  const tl = gsap.timeline({ paused: true, onUpdate: render });
  tl.set(S, { rise: 0, iris: 0, angle: 34, dx: 820, dy: -620, happy: 0, r1: -1, r2: -1, dotOn: 0, dotPop: 1, dotY: 0 }, 0);
  tl.to(S, { rise: 1, duration: 0.66, ease: "none" }, 0); // les lettres montent (35 ms d'écart, 0,42 s chacune)
  // Iris entre, petite, et vise le point
  tl.to(S, { iris: 1, duration: 0.25, ease: "power1.out" }, 0.42 + attente);
  tl.to(S, { dx: 0, dy: 0, angle: 24, duration: 0.5, ease: "power2.out" }, 0.42 + attente);
  tl.to(S, { blink: 1, duration: 0.06 }, 0.8 + attente).to(S, { blink: 0, duration: 0.08 }, 0.86 + attente);
  // toc
  tl.to(S, { angle: 0, duration: 0.15, ease: "power3.in" }, T_HIT - 0.15);
  tl.to(S, { angle: 2.4, duration: 0.07, ease: "power2.out" }, T_HIT).to(S, { angle: 0, duration: 0.08, ease: "power2.in" }, T_HIT + 0.07);
  tl.to(S, { happy: 1, duration: 0.07 }, T_HIT);
  tl.fromTo(S, { r1: 0 }, { r1: 1, duration: 0.6, ease: "power1.out", immediateRender: false }, T_HIT);
  tl.fromTo(S, { r2: 0 }, { r2: 1, duration: 0.6, ease: "power1.out", immediateRender: false }, T_HIT + 0.12);
  // elle se relève et s'efface
  tl.to(S, { angle: 30, dx: 260, dy: -380, duration: 0.42, ease: "power2.inOut" }, T_HIT + 0.22);
  tl.to(S, { iris: 0, duration: 0.3, ease: "power1.in" }, T_HIT + 0.42);
  if (variant === "chute") {
    // le point tombe de la tête et se pose avec un léger rebond
    tl.set(S, { dotOn: 1, dotY: -520, dotPop: 1 }, T_HIT + 0.26);
    tl.to(S, { dotY: 0, duration: 0.26, ease: "power2.in" }, T_HIT + 0.26);
    tl.to(S, { dotPop: 0.82, duration: 0.07, ease: "power2.out" }, T_HIT + 0.52).to(S, { dotPop: 1.06, duration: 0.09, ease: "power1.inOut" }, T_HIT + 0.59)
      .to(S, { dotPop: 1, duration: 0.1, ease: "power1.out" }, T_HIT + 0.68);
  } else {
    // tamponné : le point est là, sous la tête, dès le contact ; il rebondit quand elle se relève
    tl.set(S, { dotOn: 1, dotPop: 0.86 }, T_HIT);
    tl.to(S, { dotPop: 1.08, duration: 0.12, ease: "power2.out" }, T_HIT + 0.24).to(S, { dotPop: 1, duration: 0.14, ease: "power1.inOut" }, T_HIT + 0.36);
  }
  const duration = 2.2 + attente;
  tl.set(S, {}, duration);
  render();
  return { svg, tl, tocs: [T_HIT], duration, render };
}

