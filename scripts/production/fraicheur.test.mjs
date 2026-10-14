// « Chaque matin, en direct de simap » (suite 10, § 2) : le contrôle quotidien de la production signale une section qui
// n'a pas été renouvelée. Une fois la section publiée, chaque jour ouvrable a sa lecture ; le planificateur de GitHub
// démarre souvent avec des heures de retard, donc le jour même n'est attendu qu'à partir de 16 h (heure de Zurich).
//   node --test scripts/production/fraicheur.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { expectedReading, staleProblem } from "./fraicheur.mjs";

const at = (day, hour) => ({ day, hour }); // the time in Zurich: « AAAA-MM-JJ » and the hour

test("le jour de lecture attendu : le jour ouvrable même à partir de 16 h, sinon le précédent", () => {
  assert.equal(expectedReading(at("2026-10-13", 9)), "2026-10-12"); // Tuesday morning: Monday's reading
  assert.equal(expectedReading(at("2026-10-13", 16)), "2026-10-13");
  assert.equal(expectedReading(at("2026-10-12", 9)), "2026-10-09"); // Monday morning: Friday's reading
  assert.equal(expectedReading(at("2026-10-17", 12)), "2026-10-16"); // Saturday: Friday's
  assert.equal(expectedReading(at("2026-10-18", 20)), "2026-10-16"); // Sunday: Friday's
});

test("une section en attente (jamais publiée) ne déclenche rien", () => {
  assert.equal(staleProblem({ etat: "en_attente", mis_a_jour_le: null }, at("2026-10-14", 18)), null);
});

test("une section renouvelée passe ; une lecture manquée est signalée", () => {
  assert.equal(staleProblem({ etat: "a_jour", mis_a_jour_le: "2026-10-13" }, at("2026-10-14", 10)), null);
  assert.match(staleProblem({ etat: "a_jour", mis_a_jour_le: "2026-10-12" }, at("2026-10-14", 10)),
    /non renouvelée : lecture du 2026-10-12, attendue du 2026-10-13/);
  assert.match(staleProblem({ etat: "a_jour", mis_a_jour_le: "2026-10-13" }, at("2026-10-14", 17)), /attendue du 2026-10-14/);
});
