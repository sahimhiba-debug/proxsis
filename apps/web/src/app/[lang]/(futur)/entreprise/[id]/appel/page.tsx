import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, ArrowUpRight } from "lucide-react";
import type { ReactNode } from "react";
import { CopyButton } from "@/components/CopyButton";
import { CarnetPanel } from "@/futur/CarnetPanel";
import { calls, companies, meta } from "@/lib/data";
import { fmt, getDict, LANGS, type Lang } from "@/lib/i18n";
import type { Fact, FactType, GuideSection, Phrase } from "@/lib/types";
import { AwardPaper } from "@/futur/AwardPaper";
import { callLine, frenchSpaces, reasonAward, usageName } from "@/futur/display";
import { CorrectionNote } from "@/futur/CorrectionNote";

export const dynamicParams = false;

export function generateStaticParams() {
  return LANGS.flatMap((lang) => Object.keys(calls).map((id) => ({ lang, id })));
}

export async function generateMetadata({ params }: PageProps<"/[lang]/entreprise/[id]/appel">) {
  const { lang, id } = await params;
  return { title: `${getDict(lang).call.title} · ${companies[id]?.nom ?? ""}` };
}

// « app:/mesures#PHAS-1 » → « /fr/mesures/#PHAS-1 »: the fragment comes AFTER the trailing slash (audit M3)
function factHref(f: Fact, lang: string): string {
  if (!f.url.startsWith("app:")) return f.url;
  const [path, fragment] = f.url.slice(4).split("#");
  return `/${lang}${path}/`.replace("//", "/") + (fragment ? `#${fragment}` : "");
}

/**
 * « [votre nom] » and « [votre agence] » are slots the consultant fills in: they look like slots, not like words. A
 * slot and the sign right after it stay on one line (the final point never starts a line alone).
 */
function Slots({ text }: { text: string }) {
  return text.split(/(\[[^\]]+\][.,;:!?]?)/).map((part, i) => {
    const slot = part.match(/^\[([^\]]+)\](.?)$/);
    return slot ? <span key={i} className="whitespace-nowrap"><span className="fx-slot">{slot[1]}</span>{slot[2]}</span> : part;
  });
}

/** The numbers of the sources a sentence rests on, each a link to the source below. */
function Cite({ ids, label }: { ids: number[]; label: string }) {
  if (!ids.length) return null;
  return (
    <sup className="fx-cite">
      {ids.map((i) => <a key={i} href={`#fait-${i}`} aria-label={label.replace("{n}", String(i))}>{i}</a>)}
    </sup>
  );
}

/** A sentence and its source numbers; the last word and the numbers stay on one line (a number never starts a line). */
function Said({ p, label, lang }: { p: Phrase; label: string; lang: Lang }) {
  const text = frenchSpaces(p.texte, lang);
  if (!p.sources.length) return <>{text}</>;
  const cut = text.lastIndexOf(" ");
  return <>{text.slice(0, cut + 1)}<span className="whitespace-nowrap">{text.slice(cut + 1)}<Cite ids={p.sources} label={label} /></span></>;
}

/** The e-mail as the consultant will paste it: one blank line between paragraphs; the closing formula and the
 * signature lines to fill in ([votre nom], Flexsis [votre agence]) form one paragraph. */
function emailText(subject: string, phrases: Phrase[]): string {
  const slots = (x: Phrase) => /^(Flexsis )?\[[^\]]+\]$/.test(x.texte);
  return `${subject}\n\n${phrases.map((x, i) => (i === 0 ? "" : slots(x) ? "\n" : "\n\n") + x.texte).join("")}`;
}

function Block({ title, id, tag, children }: { title: string; id: string; tag?: ReactNode; children: ReactNode }) {
  return (
    <section aria-labelledby={id} className="mt-12">
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <h2 id={id} className="fx-caps fx-muted">{title}</h2>{tag}
      </div>
      {children}
    </section>
  );
}

// « Préparer l'appel », futurisme suisse: one clear card with what to say first and what to ask, then the guide in the
// order of the call. Every sentence keeps its source number; the estimate is set apart as a hypothesis to confirm,
// never as a fact; the company's answer is recorded where the consultant comes back after calling.
export default async function CallPage({ params }: PageProps<"/[lang]/entreprise/[id]/appel">) {
  const { lang: l, id } = await params;
  const lang = l as Lang;
  const t = getDict(lang);
  const prep = calls[id];
  const c = companies[id];
  if (!prep || !c) notFound();
  const doc = prep[lang];
  const types = new Map(prep.faits.map((f) => [f.id, f.type]));
  const typeOf = (sec: GuideSection): FactType | null => types.get(sec.phrases.flatMap((p) => p.sources)[0]) ?? null;
  const part = (code: GuideSection["code"]) => doc.guide.find((s) => s.code === code);
  const opening = part("ouverture")?.phrases[0];
  const question = part("questions")?.phrases[0];
  const phone = callLine(c, lang);
  const award = reasonAward(c);
  const awardFact = prep.faits.find((f) => f.code === "adjudication")?.id;
  const provider = prep.redaction.type === "apertus" ? prep.redaction.fournisseur : t.fx.callTemplate;
  const cite = t.fx.callSource;
  const tag = (type: FactType | null) => (type === "maison" || type === "fictif"
    ? <span className="fx-tag" data-kind={type}>{t.call.type[type]}</span> : null);

  return (
    <article className="fx-col fx-dossier pt-2">
      <div className="fx-dossier-head">
        <Link href={`/${lang}/entreprise/${id}/`} className="fx-quiet -ml-1">
          <ArrowLeft aria-hidden className="size-4" strokeWidth={1.5} /> {usageName(c.nom)}
        </Link>
        <header className="mt-3">
          <p className="fx-caps fx-copper">{c.ville} · {c.canton}</p>
          <h1 className="fx-display mt-2 text-[36px] sm:text-[44px]">{t.call.title}</h1>
          <p className="fx-muted mt-2 text-[14px]">{c.nom}</p>
        </header>

        {/* the card the consultant holds while dialling: how to open, what to say, what to ask */}
        <section className="fx-raised mt-6 p-6 sm:p-7" aria-labelledby="fx-call-card" data-testid="call-card">
          <h2 id="fx-call-card" className="sr-only">{t.fx.callCard}</h2>
          {opening ? (
            <>
              <p className="fx-caps fx-muted">{t.fx.callOpen}</p>
              <p className="mt-3 text-[19px] leading-snug sm:text-[21px]"><Slots text={frenchSpaces(opening.texte, lang)} /></p>
            </>
          ) : null}
          {phone ? (
            <>
              <hr className="fx-rule my-6" />
              <p className="fx-caps fx-muted">{phone.review ? t.fx.phoneFact : t.fx.phone}</p>
              <p className="mt-3 text-[17px] leading-snug" data-testid="phone-line">
                <Said p={{ texte: phone.lead ?? phone.text, sources: awardFact ? [awardFact] : [] }} label={cite} lang={lang} />
                {phone.lead && phone.title ? <q className="fx-citation" data-testid="phone-title">{phone.title}</q> : null}
              </p>
              {phone.review ? <p className="fx-muted mt-1 text-[13px]">{t.fx.phoneReview}</p> : null}
            </>
          ) : null}
          {question ? (
            <>
              <hr className="fx-rule my-6" />
              <p className="fx-caps fx-copper">{t.fx.callQuestion}</p>
              <p className="fx-display mt-3 text-balance text-[26px] sm:text-[30px]">{frenchSpaces(question.texte, lang)}</p>
            </>
          ) : null}
        </section>
        <p className="fx-muted mt-3 text-[13px]">{t.call.placeholderNote}</p>
      </div>

      <div className="fx-dossier-body">
        {/* German: the guide's wording is not presented as ready until a German speaker has read it (§ 9) */}
        {t.fx.guideReview ? <p className="fx-muted mt-10 text-[14px]" data-testid="guide-review">{t.fx.guideReview}</p> : null}
        {doc.guide.filter((s) => s.code !== "ouverture").map((sec) => {
          const key = `fx-call-${sec.code}`;
          if (sec.code === "pourquoi") {
            // the published award on its paper (as in the dossier), then what else simap says
            const rest = sec.phrases.filter((p) => !(awardFact && p.sources.length === 1 && p.sources[0] === awardFact));
            return (
              <Block key={key} id={key} title={sec.titre}>
                {award ? <AwardPaper award={award} t={t} lang={lang}>{awardFact ? <Cite ids={[awardFact]} label={cite} /> : null}</AwardPaper> : null}
                {rest.length ? (
                  <ul className="mt-4 border-t border-[var(--fx-line)]">
                    {rest.map((p, i) => <li key={i} className="border-b border-[var(--fx-line)] py-3 text-[15px] leading-relaxed"><Said p={p} label={cite} lang={lang} /></li>)}
                  </ul>
                ) : null}
              </Block>
            );
          }
          if (sec.code === "estimation") {
            return (
              <Block key={key} id={key} title={sec.titre}>
                <div className="fx-hypo p-5" data-testid="call-hypothesis">
                  <p className="fx-muted text-[14px]">{t.fx.callHypothesis}</p>
                  {sec.phrases.map((p, i) => <p key={i} className="mt-3 text-[15px] leading-relaxed"><Said p={p} label={cite} lang={lang} /></p>)}
                  <p className="mt-3 text-[14px]"><Link className="fx-link inline-flex min-h-11 items-center" href={`/${lang}/mesures/#BESOIN-1`}>{t.fx.howMeasure}</Link></p>
                </div>
              </Block>
            );
          }
          if (sec.code === "questions") {
            // the first question is on the card already: the others follow it, numbered after it
            const others = sec.phrases.slice(1);
            if (!others.length) return null;
            return (
              <Block key={key} id={key} title={sec.titre}>
                <ol className="border-t border-[var(--fx-line)]">
                  {others.map((p, i) => (
                    <li key={i} className="flex gap-4 border-b border-[var(--fx-line)] py-3 text-[16px]">
                      <span className="fx-mono fx-muted text-[13px] leading-6" aria-hidden>{String(i + 2).padStart(2, "0")}</span>
                      <span>{frenchSpaces(p.texte, lang)}</span>
                    </li>
                  ))}
                </ol>
              </Block>
            );
          }
          return (
            <Block key={key} id={key} title={sec.titre} tag={tag(typeOf(sec))}>
              <ul className="border-t border-[var(--fx-line)]">
                {sec.phrases.map((p, i) => (
                  <li key={i} className={`border-b border-[var(--fx-line)] py-3 leading-relaxed ${sec.code === "suite" ? "text-[18px]" : "text-[15px]"}`}>
                    <Said p={p} label={cite} lang={lang} />
                  </li>
                ))}
              </ul>
              {sec.code === "apport" ? <p className="fx-muted mt-3 text-[13px]">{t.call.houseNote}</p> : null}
            </Block>
          );
        })}

        {/* the call's outcome, right after the guide: where the consultant comes back once he has called */}
        <div className="mt-12">
          <CarnetPanel entreprise={id} monday={meta.semaine} lang={lang} />
        </div>

        <Block title={t.call.email} id="fx-call-email">
          <div className="fx-paper p-5 sm:p-6">
            <div className="flex items-start justify-between gap-4">
              <p className="fx-caps">{t.call.subject}</p>
              <CopyButton text={emailText(doc.email.objet, doc.email.phrases)} label={t.label.copy} done={t.label.copied} failed={t.label.copyFailed}
                className="fx-paper-button" />
            </div>
            <p className="fx-paper-title mt-1">{frenchSpaces(doc.email.objet, lang)}</p>
            <div className="mt-4 text-[15px] leading-relaxed">
              {doc.email.phrases.map((p, i) => {
                const slot = /^(Flexsis )?\[[^\]]+\]$/.test(p.texte);
                return <p key={i} className={i === 0 ? "" : slot ? "" : "mt-2"}>{slot ? <Slots text={p.texte} /> : <Said p={p} label={cite} lang={lang} />}</p>;
              })}
            </div>
          </div>
        </Block>

        <Block title={t.call.facts} id="fx-call-facts">
          <ol className="border-t border-[var(--fx-line)]">
            {prep.faits.map((f) => (
              <li key={f.id} id={`fait-${f.id}`} className="border-b border-[var(--fx-line)] py-4">
                <p className="flex flex-wrap items-center gap-x-3 gap-y-1">
                  <span className="fx-mono fx-muted text-[13px]">{f.id}</span>
                  <span className="fx-tag" data-kind={f.type}>{t.call.type[f.type]}</span>
                  <span className="fx-muted text-[13px]">{f.source[lang]}</span>
                </p>
                <p className="mt-2 text-[15px] leading-relaxed">{frenchSpaces(f[lang], lang)}</p>
                {f.portee ? <p className="fx-muted mt-1 text-[13px]">{t.call.scope}{t.label.colon} {f.portee[lang]}</p> : null}
                <p className="mt-1 text-[14px]">
                  {f.url.startsWith("app:") ? (
                    <Link className="fx-link inline-flex min-h-11 min-w-11 items-center" href={factHref(f, lang)}>{t.label.open}</Link>
                  ) : (
                    <a className="fx-link inline-flex min-h-11 items-center gap-1" href={f.url} target="_blank" rel="noopener noreferrer">
                      {f.url.replace(/^https:\/\/(www\.)?/, "").split("/")[0]} <ArrowUpRight aria-hidden className="size-3.5" strokeWidth={1.75} />
                    </a>
                  )}
                </p>
                <CorrectionNote url={f.url} lang={lang} className="fx-muted" />
              </li>
            ))}
          </ol>
          <p className="fx-muted mt-4 text-[13px]" data-testid="writer">{fmt(t.call.writer, { provider })}. {t.call.writerNote}</p>
        </Block>
      </div>
    </article>
  );
}
