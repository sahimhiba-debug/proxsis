// The region of a week list, for the mini-map of « Ma semaine » (wide screens). Server side only: it reads the
// swisstopo commune boundaries (embedded, offline) and keeps the communes in view. Places come from the export (the
// commune of each company, the agency's public address); nothing is placed by guess.
import contours from "@/data/presentation/communes_vs.json";

const P = contours.meta.projection;
const COS = Math.cos((P.cos_lat * Math.PI) / 180);

/** Same projection as the boundaries (and as the presentation's map). */
export function project(lat: number, lon: number): { x: number; y: number } {
  return { x: (lon - P.lon0) * COS * P.k, y: (P.lat1 - lat) * P.k };
}

interface View { x: number; y: number; w: number; h: number }

/** A view around the points, with a margin, never smaller than `minW`, in the given width/height ratio. */
export function regionView(pts: { x: number; y: number }[], ratio = 4 / 3, pad = 30, minW = 250): View {
  const xs = pts.map((p) => p.x);
  const ys = pts.map((p) => p.y);
  const [x0, x1, y0, y1] = [Math.min(...xs) - pad, Math.max(...xs) + pad, Math.min(...ys) - pad, Math.max(...ys) + pad];
  const w = Math.max(minW, x1 - x0, (y1 - y0) * ratio);
  const h = w / ratio;
  return { x: (x0 + x1) / 2 - w / 2, y: (y0 + y1) / 2 - h / 2, w, h };
}

const BOXES = contours.communes.map((c) => {
  const n = c.d.match(/-?\d+(?:\.\d+)?/g)?.map(Number) ?? [];
  const xs = n.filter((_, i) => i % 2 === 0);
  const ys = n.filter((_, i) => i % 2 === 1);
  return { bfs: c.bfs, d: c.d, x0: Math.min(...xs), x1: Math.max(...xs), y0: Math.min(...ys), y1: Math.max(...ys) };
});

/** The communes that cross the view (the others are not sent to the page). */
export function communesIn(v: View): { bfs: number; d: string }[] {
  return BOXES.filter((b) => b.x1 >= v.x && b.x0 <= v.x + v.w && b.y1 >= v.y && b.y0 <= v.y + v.h).map(({ bfs, d }) => ({ bfs, d }));
}

export const CANTON = contours.canton;

const [BX0, BY0, BX1, BY1] = contours.meta.bbox;
/** The whole canton, with a small margin (the « Carte » page). */
export const VALAIS_VIEW: View = { x: BX0 - 8, y: BY0 - 8, w: BX1 - BX0 + 16, h: BY1 - BY0 + 16 };

export interface Place { ville: string; x: number; y: number; n: number; recent: number }

/** The companies of the week, one place per commune: how many, and how many with a contract of less than 14 days. */
export function places(items: { ville: string; lat: number; lon: number; recent: boolean }[]): Place[] {
  const by = new Map<string, Place>();
  for (const it of items) {
    const p = by.get(it.ville) ?? { ville: it.ville, ...project(it.lat, it.lon), n: 0, recent: 0 };
    p.n += 1;
    if (it.recent) p.recent += 1;
    by.set(it.ville, p);
  }
  // the places with a recent signal are drawn last, above the others
  return [...by.values()].sort((a, b) => Number(a.recent > 0) - Number(b.recent > 0) || a.ville.localeCompare(b.ville));
}

type LabelSide = "right" | "left" | "above" | "below";

/**
 * The side where a label has room in its frame and covers no other dot (positions in px of a reference frame W × H;
 * a label is about 8 px per letter). Shared by the region of the week and the map of the Valais.
 */
export function labelSide(a: { x: number; y: number }, text: string, others: { x: number; y: number }[], W: number, H: number): LabelSide {
  const w = text.length * 8 + 24;
  const box: Record<LabelSide, [number, number, number, number]> = { // x0, x1, y0, y1 of the label, around the dot
    right: [a.x + 4, a.x + w, a.y - 9, a.y + 9], left: [a.x - w, a.x - 4, a.y - 9, a.y + 9],
    above: [a.x - w / 2, a.x + w / 2, a.y - 24, a.y - 4], below: [a.x - w / 2, a.x + w / 2, a.y + 4, a.y + 24],
  };
  const fits = ([x0, x1, y0, y1]: number[]) => x0 > 6 && x1 < W - 6 && y0 > 4 && y1 < H - 4;
  const covered = ([x0, x1, y0, y1]: number[]) => others.filter((b) => b.x > x0 && b.x < x1 && b.y > y0 && b.y < y1).length;
  const order: LabelSide[] = ["right", "left", "above", "below"];
  const room = order.filter((k) => fits(box[k]));
  return room.find((k) => covered(box[k]) === 0) ?? room.sort((x, y) => covered(box[x]) - covered(box[y]))[0] ?? "right";
}
