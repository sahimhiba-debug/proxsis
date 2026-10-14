import { ArrowUpRight } from "lucide-react";
import type { ReactNode } from "react";
import type { Dict } from "@/i18n/dictionaries";
import { fmtChfPublished, fmtDate, type Lang } from "@/lib/i18n";
import type { Source } from "@/lib/types";
import { CorrectionNote } from "./CorrectionNote";

/**
 * The published award on its paper (simap.ch, date, title, authority, amount, link): the same sheet in the dossier
 * (« Ce que dit l'annonce ») and in the call guide (« Pourquoi j'appelle »). The title stays in the language it was
 * published in; only the quotation marks follow the page. The amount is the published one, exact; a correction that
 * simap published since is said under the link (AGB API simap ch. 5).
 */
export function AwardPaper({ award, t, lang, children }: { award: Source; t: Dict; lang: Lang; children?: ReactNode }) {
  const title = lang === "fr" ? `« ${award.titre.trim()} »` : `«${award.titre.trim()}»`;
  return (
    <div className="fx-paper p-5 sm:p-6">
      <p className="fx-caps flex justify-between gap-3"><span>simap.ch</span><span>{fmtDate(award.date)}</span></p>
      <p className="fx-paper-title mt-3">{title}{children}</p>
      <p className="mt-3 text-[14px] text-[var(--fx-ink-muted)]">
        {t.company.authority}{t.label.colon} {award.adjudicateur ?? "—"}
        {award.montant_chf ? <span className="fx-num"> · {t.company.amount}{t.label.colon} {fmtChfPublished(award.montant_chf)}</span> : null}
      </p>
      <p className="mt-4 text-[14px]">
        <a href={award.url_simap} target="_blank" rel="noopener noreferrer" className="inline-flex min-h-11 items-center gap-1">
          {t.fx.source} <ArrowUpRight aria-hidden className="size-3.5" strokeWidth={1.75} />
        </a>
      </p>
      <CorrectionNote url={award.url_simap} lang={lang} className="mt-1 text-[var(--fx-ink-muted)]" />
    </div>
  );
}
