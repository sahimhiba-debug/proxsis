// « Votre lundi à Martigny, Sion, Monthey » (brief of 07.10.2026, suite 2, § 3): the three Flexsis agencies of the
// Valais, from their public addresses on flexsis.ch (CLAIMS EXT-FLEXSIS-AGENCES-VS, read on 07.10.2026), placed on the
// map at their commune. No other data about Flexsis, no logo. The prepared example: Martigny, near Saxon and the guided
// dossier. « Around » an agency: the ten companies of the week's list, ordered by the distance between the centres of
// their seat's commune and the agency's commune (an order, never shown as kilometres).
export interface Agence { id: string; nom: string; bfs: string; adresse: string }

export const AGENCES: Agence[] = [
  { id: "martigny", nom: "Martigny", bfs: "6136", adresse: "Avenue de la gare 38, 1920 Martigny" },
  { id: "sion", nom: "Sion", bfs: "6266", adresse: "Avenue de Tourbillon 5, 1950 Sion" },
  { id: "monthey", nom: "Monthey", bfs: "6153", adresse: "Rue de Venise 10, 1870 Monthey" },
];
export const AGENCE_EXEMPLE = "martigny";

/** The centre of a commune's outline (mean of its points, in the map's projected units). */
export function centre(d: string): [number, number] {
  const n = [...d.matchAll(/(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)/g)].map((m) => [Number(m[1]), Number(m[2])] as const);
  const x = n.reduce((a, p) => a + p[0], 0) / n.length, y = n.reduce((a, p) => a + p[1], 0) / n.length;
  return [x, y];
}

/** The companies of the week around an agency: nearest seat commune first, then by name. */
export function autour(ids: string[], seatOf: (id: string) => string | null, centres: Record<string, [number, number]>,
  agence: Agence, name: (id: string) => string): string[] {
  const [ax, ay] = centres[agence.bfs];
  const dist = (id: string) => {
    const c = centres[seatOf(id) ?? ""];
    return c ? Math.hypot(c[0] - ax, c[1] - ay) : Infinity;
  };
  return [...ids].filter((id) => Number.isFinite(dist(id))).sort((a, b) => dist(a) - dist(b) || name(a).localeCompare(name(b)));
}
