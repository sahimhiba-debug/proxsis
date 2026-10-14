import { afterEach, describe, expect, it } from "vitest";
import { readStored, writeStored } from "./useStored";

// a browser whose storage is refused (site data blocked), or that works: the choices are kept either way for the visit
function browser(refused: boolean) {
  const saved = new Map<string, string>();
  const localStorage = {
    getItem: (k: string) => { if (refused) throw new Error("SecurityError"); return saved.get(k) ?? null; },
    setItem: (k: string, v: string) => { if (refused) throw new Error("SecurityError"); saved.set(k, v); },
  };
  (globalThis as unknown as { window: unknown }).window = { localStorage };
  return saved;
}

afterEach(() => { delete (globalThis as unknown as { window?: unknown }).window; });

describe("conservation sur l'appareil, et en mémoire si elle est refusée (brief à distance, § 8)", () => {
  it("stockage refusé : le choix reste lu pendant la visite (« Sans mouvement », mode essai, carnet)", () => {
    browser(true);
    expect(readStored("k.refuse")).toBeNull();
    writeStored("k.refuse", "on");
    expect(readStored("k.refuse")).toBe("on");
  });

  it("stockage disponible : le choix y est écrit, et une écriture réussie remplace la mémoire", () => {
    browser(true);
    writeStored("k.mixte", "memoire");
    const saved = browser(false);
    writeStored("k.mixte", "appareil");
    expect(saved.get("k.mixte")).toBe("appareil");
    expect(readStored("k.mixte")).toBe("appareil");
  });
});
