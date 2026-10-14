// Data of act 4, « Choisissez une date » (python/src/proxsis/date_choice.py → apps/web/src/data/presentation/lundis.json):
// every Monday of the measure REEL-SPEC-BAT, the ten companies of the simple rule that day (publications published
// before it only) and what each obtained in the 8 following weeks. The figures come from the file, never from the copy.
import type { PLang } from "./copy";

export interface MondayCompany {
  rang: number;
  id: string;
  nom: string;
  ville: string | null;
  marches_52s: number;
  dernier_marche: string;
  // a second entry of one firm (a branch), counted apart by the measure: the rank of the other entry
  autre_inscription_de: number | null;
  nouveau_marche: { date: string; titre: string | null; url: string; nombre: number } | null;
}

export interface Monday {
  lundi: string;
  choisissable: boolean;
  historique_jours: number;
  entreprises_classees: number;
  entreprises_actives: number;
  obtenu: number;
  dix: MondayCompany[];
}

export interface MondaysData {
  claims: string;
  source: { nom: string; mention: string; debut_des_donnees: string; fin_des_donnees: string };
  regle: { specialite: string; region: string[]; k: number; ordre: string; horizon_jours: number; historique_jours: number };
  choix: { premier: string; dernier: string; nombre: number; exemple: string }; // exemple: the prepared Monday
  mesure: { semaines: number; premiere: string; derniere: string; regle: number; hasard: number;
    affiche: { regle: Record<PLang, string>; hasard: Record<PLang, string> } };
  lundis: Monday[];
}

/** Any date is brought back to the Monday of its week (dates as « AAAA-MM-JJ », computed in UTC: no time zone). */
export function mondayOf(iso: string): string {
  const d = new Date(`${iso}T00:00:00Z`);
  const back = (d.getUTCDay() + 6) % 7;
  return new Date(d.getTime() - back * 86_400_000).toISOString().slice(0, 10);
}

/** The Monday a chosen date leads to, or why it cannot be shown (before the first or after the last Monday offered). */
export function pickMonday(data: MondaysData, iso: string): { monday: Monday } | { outside: "avant" | "apres" } | null {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(iso) || Number.isNaN(Date.parse(`${iso}T00:00:00Z`))) return null;
  const m = mondayOf(iso);
  if (m < data.choix.premier) return { outside: "avant" };
  if (m > data.choix.dernier) return { outside: "apres" };
  const monday = data.lundis.find((x) => x.lundi === m && x.choisissable);
  return monday ? { monday } : null;
}
