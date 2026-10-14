import Link from "next/link";
import { agencies } from "@/lib/data";

/** The three agencies and « all », as pills; the current one is marked (aria-current). */
export function AgencyNav({ lang, current, allLabel, label }: { lang: string; current: string | null; allLabel: string; label: string }) {
  const items = [...Object.values(agencies).map((a) => ({ id: a.id, name: a.nom.replace(/^Flexsis\s+/, ""), href: `/${lang}/agence/${a.id}/` })),
    { id: null, name: allLabel, href: `/${lang}/agence/` }];
  return (
    <nav aria-label={label} className="mt-6 flex flex-wrap gap-2">
      {items.map((i) => (
        <Link key={i.href} href={i.href} className="fx-pill" aria-current={i.id === current ? "page" : undefined}>{i.name}</Link>
      ))}
    </nav>
  );
}
