// The first test the confession of « Choisissez une date » is about (CLAIMS REEL-T0, histoires.json): another scope
// than the measure of the date (Valais, ten companies per Monday), shown under the confession with its own figures.
import histoires from "@/data/presentation/histoires.json";
import type { FirstTest } from "@/presentation/ChooseDate";

/** Its weeks, the simple rule and the more complicated selection, as displayed (never written by hand). */
export function firstTest(): FirstTest {
  const value = (code: string) => {
    const v = histoires.mesure.valeurs.find((x) => x.code === code);
    if (!v) throw new Error(`histoires.json : valeur ${code} absente`);
    return v.affiche;
  };
  return { semaines: histoires.mesure.perimetre.semaines, regle: value("frequence_52s"), m0: value("m0_marches") };
}
