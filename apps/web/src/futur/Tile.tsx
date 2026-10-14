import Link from "next/link";
import type { Dict } from "@/i18n/dictionaries";
import { Counter } from "./Counter";
import { KindTag, type DataKind } from "./KindTag";

/** A figure on a tile: it builds up, says what it is (real, fictional…) and links to the measure that justifies it. */
export function Tile({ label, value, decimals = 0, suffix = "", kind, claim, note, lang, t }: {
  label: string; value: number; decimals?: number; suffix?: string; kind: DataKind; claim: string; note?: string;
  lang: string; t: Dict;
}) {
  return (
    <div className="fx-card flex flex-col p-5" data-testid="kpi">
      <p className="flex flex-wrap items-start justify-between gap-x-3 gap-y-2">
        <span className="fx-muted min-w-0 text-[14px] leading-snug [hyphens:auto]">{label}</span>
        <KindTag kind={kind} t={t} />
      </p>
      <p className="mt-4"><Counter value={value} decimals={decimals} lang={lang} suffix={suffix} className="fx-display text-[44px] leading-none" /></p>
      {note ? <p className="fx-muted mt-2 text-[13px] leading-snug">{note}</p> : null}
      <p className="mt-auto pt-3 text-[13px]">
        <Link className="fx-link inline-flex min-h-11 items-center" href={`/${lang}/mesures/#${claim}`}>{t.fx.howMeasure}</Link>
      </p>
    </div>
  );
}
