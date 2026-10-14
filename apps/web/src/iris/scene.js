// Iris, le marteau du bisse, en calques (docs/identite/mascotte/MASCOTTE.md, choisie par Hiba le 12.10.2026) :
// la géométrie commune des calques, sur une scène de 1024 × 1024 (découpés dans portrait.jpg par
// scripts/mascotte/calques.py), lue par l'animation du logo (logo.js). La grande scène animée (la roue, les frappes, les
// moments) a servi au film ; elle n'est plus dans l'application, son code reste dans l'historique Git.

export const PIVOT = { x: 907, y: 432 }; // le boulon du chevalet : le manche tourne autour
export const EYES = [
  { name: "oeil-g", x: 334, y: 307, w: 68, h: 98, cx: 367.5, cy: 355.5, ew: 32, eh: 62 },
  { name: "oeil-d", x: 425, y: 320, w: 66, h: 95, cx: 457.5, cy: 367.0, ew: 30, eh: 59 },
];
