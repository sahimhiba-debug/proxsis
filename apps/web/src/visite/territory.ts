// Data of the visit's first time, « Le premier lundi » (python/src/proxsis/territory.py → apps/web/src/data/
// presentation/territoire.json): per commune of the map (official number), the companies whose seat is there and the
// contracts published there, only for companies whose dossier passes every check; the others with their reasons.

export interface TerritoryContract { id: string; date: string; titre: string; url: string }

export interface TerritoryCompany {
  nom: string;
  ville: string | null; // the published seat locality
  commune_siege: number; // official number of the seat's commune
  guide: boolean; // one of the three guided dossiers (« à valider »)
  consortium: boolean;
}

export interface TerritoryData {
  schema: 1;
  lundi: string;
  source: { nom: string; mention: string };
  controles: Record<string, string>;
  exemple: { commune: string; entreprise: string };
  communes: Record<string, { siege: string[]; marches: TerritoryContract[] }>;
  entreprises: Record<string, TerritoryCompany>;
  exclues: { id: string; nom: string; controles_echoues: string[] }[];
}
