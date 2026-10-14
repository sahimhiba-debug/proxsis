import { CORRECTION_COPY, correctionSentence, correctionsFor } from "@/lib/corrections";

/** Next to a notice of the frozen data: the corrections simap published since (none: nothing is shown). */
export function CorrectionNote({ url, lang, className = "" }: { url: string | null | undefined; lang: "fr" | "de"; className?: string }) {
  const found = correctionsFor(url);
  if (!found.length) return null;
  return (
    <p className={`text-[13px] ${className}`} data-testid="correction-note" role="note">
      {found.map((n) => (
        <span key={`${n.date}-${n.type}`} className="block">
          {correctionSentence(n.type, n.date, lang)}{" "}
          <a className="underline underline-offset-4" href={n.url} target="_blank" rel="noopener noreferrer">{CORRECTION_COPY[lang].open}</a>
        </span>
      ))}
    </p>
  );
}
