import { expect, test } from "@playwright/test";

// The served site sends its security headers (next.config.ts) and no page breaks them: the demo path already fails on
// any console error, a refused script or style included.
test("en-têtes de sécurité du site servi", async ({ request }, info) => {
  test.skip(info.project.name !== "en-ligne", "le site servi seulement (la copie hors ligne n'a pas d'en-têtes)");
  for (const path of ["/fr/semaine/M1/", "/fr/presentation/", "/de/entreprise/ent-1ef761b229/appel/"]) {
    const res = await request.get(path);
    const h = res.headers();
    expect(h["content-security-policy"], path).toContain("default-src 'self'");
    expect(h["content-security-policy"], path).toContain("frame-ancestors 'self'");
    expect(h["x-content-type-options"], path).toBe("nosniff");
    expect(h["referrer-policy"], path).toBe("strict-origin-when-cross-origin");
    expect(h["x-frame-options"], path).toBe("SAMEORIGIN");
    expect(h["permissions-policy"], path).toContain("camera=()");
    expect(h["x-powered-by"], path).toBeUndefined();
  }
});
