// Data of act 4 (python/src/proxsis/presentation_stories.py → apps/web/src/data/presentation/histoires.json):
// three stories replayed at a past Monday, each in three stops, and the screen of the first examination (CLAIMS
// REEL-T0). The texts that carry facts come from the data, never from the copy.
import type { PLang } from "./copy";

export type Bilingual = Record<PLang, string>;

export interface StoryPiece {
  type: "appel_offres" | "adjudication";
  numero: string;
  date: string;
  titre: string;
  objet: Bilingual | null;
  adjudicateur: string | null;
  montant_chf?: number | null;
  ouvert_a_T?: boolean;
  url: string;
}

export interface StoryInterval {
  code: string;
  nom: Bilingual;
  debut: string;
  fin: string;
  jours: number;
  arret: "connu" | "ensuite";
  prevu?: boolean;
}

export interface Story {
  id: string;
  type: "reussite" | "limite";
  claims: string;
  entreprise: { id: string; nom: string; ville: string };
  region: Bilingual;
  date_T: string;
  arrets: {
    connu: { date: string; pieces: StoryPiece[]; texte: Bilingual; contexte?: { texte: Bilingual } };
    signalement: { texte: Bilingual };
    ensuite: {
      evenements: StoryPiece[];
      texte: Bilingual;
      autres_traces?: { source: Bilingual; publications: { id: string; date: string; commune: string; url: string }[] };
    };
  };
  intervalles: StoryInterval[];
  besoin_personnel: Bilingual;
}

export interface MeasureValue { code: string; nom: Bilingual; pct: number; affiche: Bilingual }

export interface StoriesData {
  validation: string;
  source: { nom: string; mention: string; perimetre: Bilingual };
  regle: Bilingual;
  histoires: Story[];
  mesure: {
    claims: string;
    phrase: Bilingual;
    definition: Bilingual;
    portee: Bilingual;
    perimetre: { texte: Bilingual };
    valeurs: MeasureValue[];
    ecart: { nom: Bilingual; affiche: Bilingual; lecture: Bilingual };
  };
}
