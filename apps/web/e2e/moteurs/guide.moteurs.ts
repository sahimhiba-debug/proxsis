import { test } from "@playwright/test";
import { MIN_IPAD, MIN_TELEPHONE, TAILLES_IPAD, TAILLES_TELEPHONE, verifierIris } from "../iris-taille";

// Suite 9, § 10, on the real engines: the guide's Iris measures at least 56 px on a phone (390 × 844, 375 × 667) and
// 72 px on an iPad (820 × 1180, 1180 × 820, 1024 × 1366), her two eyes well visible: the phone sizes on each engine's
// phone, the iPad sizes on its tablet.
test("la petite Iris du guide est assez grande pour être reconnue", async ({ page }, info) => {
  test.skip(info.project.name.endsWith("ordinateur"), "téléphone et tablette");
  const phone = info.project.name.endsWith("telephone");
  for (const size of phone ? TAILLES_TELEPHONE : TAILLES_IPAD) await verifierIris(page, size, phone ? MIN_TELEPHONE : MIN_IPAD);
});
