import { claims } from "@/lib/data";
import { getDict, type Lang } from "@/lib/i18n";
import type { Dict } from "@/i18n/dictionaries";
import { KindTag } from "@/futur/KindTag";
import { RULE, SOURCE_MAP, sourcesLine } from "@/lib/chaqueMatin";

export async function generateMetadata({ params }: PageProps<"/[lang]/mesures">) {
  const { lang } = await params;
  return { title: getDict(lang).fx.sources.title };
}

type SourceKey = keyof Dict["fx"]["sources"]["items"];
type Status = keyof Dict["fx"]["sources"]["status"];
// what Proxsis reads today, and what it could read tomorrow, with the state of each access (docs/demandes/,
// docs/affaires/demande-donnees-pilote.md): nothing is read without an authorised access. The four requests sent by
// Hiba in October 2026 come from the map of the sources (src/data/sources/carte.json, CLAIMS SOURCES-1, suite 10, § 3)
const TODAY: [SourceKey, Status][] = [["simap", "service"], ["bo", "service"]];
const SENT = new Set(SOURCE_MAP.demandes.liste.map((d) => d.cle));
const TOMORROW: [SourceKey, Status][] = [...(["portail", "zefix", "regbl", "jobroom"] as const).map((k): [SourceKey, Status] =>
  [k, SENT.has(k) ? "envoyee" : "licence"]), ["offres", "licence"], ["flexsis", "pilote"]];
type Family = keyof Dict["fx"]["sources"]["excluded"];
// every line the application links to is here, open (never inside the folded registry), with a plain sentence
const MEASURED = ["SOURCES-1", "PRES-DATE-1", "REEL-SPEC-BAT", "REEL-SPEC-PIC", "REEL-SURPRISE", "REEL-SPEC-NOUVEAUX", "REEL-SPEC-AUTRES", "SIMAP-3", "CONF-1"];
const ESTIMATED = ["BESOIN-1", "PHAS-1", "PHAS-2"];
const FICTIONAL = ["CAND-1", "PROP-1", "REDEP-1", "EQ-1", "TAB-FICTIF-1"];
/** The registry's own text, without its markdown (bold, code). */
const plainText = (x: string) => x.replace(/\*\*(.+?)\*\*/g, "$1").replace(/`([^`]+)`/g, "$1");

// « Sources et mesures », futurisme suisse (Hiba, 07.10.2026): the sources as a roadmap, then the registry of measures.
// The anchors (#REEL-SPEC-BAT…) stay: every figure of the application links here.
export default async function SourcesPage({ params }: PageProps<"/[lang]/mesures">) {
  const { lang: l } = await params;
  const lang = l as Lang;
  const t = getDict(lang);
  const f = t.fx.sources;
  const m = t.measures;
  const source = ([key, status]: [SourceKey, Status]) => (
    <li key={key} className="fx-card flex flex-col p-5" data-testid="source" data-source={key} data-statut={status}>
      <p className="flex flex-wrap items-start justify-between gap-3">
        <span className="text-[17px]">{f.items[key].name}</span>
        <span className="fx-tag" data-kind={status === "service" || status === "envoyee" ? "reel" : "estimation"}>{f.status[status]}</span>
      </p>
      <p className="mt-2 text-[15px] leading-snug">{f.items[key].what}</p>
      <p className="fx-muted mt-2 text-[13px] leading-snug">{f.items[key].how}</p>
    </li>
  );
  // the registry line itself: kept in French, its language said (and declared for screen readers)
  const original = (id: string) => {
    const c = claims[id];
    return (
      <div lang="fr" className="fx-muted text-[14px] leading-snug">
        <p>{plainText(c.affirmation)}</p>
        <p className="mt-1">{plainText(c.valeur)}</p>
        <p className="mt-1 text-[13px]">{m.limit}{t.label.colon} {plainText(c.limite)} · CLAIMS.md, {id}</p>
      </div>
    );
  };
  const row = (id: string) => {
    const c = claims[id];
    if (!c) return null;
    const plain = f.plain[id];
    return (
      <li key={id} id={id} className="scroll-mt-24 border-b border-[var(--fx-line)] py-4" data-testid="claim">
        <p className="flex flex-wrap items-center gap-3">
          <KindTag kind={ESTIMATED.includes(id) ? "estimation" : c.donnees.startsWith("RÉEL") ? "reel"
            : c.donnees === "SOURCE PUBLIQUE" ? "publique" : "fictif"} t={t} />
          <span className="fx-mono fx-muted text-[12px]">{id}</span>
        </p>
        {plain ? (
          <>
            <p className="mt-2 max-w-[64ch] text-[16px] leading-snug">{plain}</p>
            <details className="mt-2">
              <summary className="fx-quiet">{f.original}</summary>
              <div className="mt-2">{original(id)}</div>
            </details>
          </>
        ) : <div className="mt-2">{original(id)}</div>}
      </li>
    );
  };
  const others = Object.keys(claims).filter((id) => ![...MEASURED, ...ESTIMATED, ...FICTIONAL].includes(id));
  return (
    <div className="fx-col pb-8 pt-6 sm:pt-10">
      <h1>
        <span className="fx-caps fx-muted block">{f.title}</span>
        <span className="fx-display mt-3 block text-[34px] sm:text-[52px]">{f.display}</span>
      </h1>
      {/* the map of the sources (suite 10, § 3): the real numbers of the catalogue, then the rule */}
      <p className="mt-5 max-w-[64ch] text-[18px] leading-snug sm:text-[20px]" data-testid="sources-carte">
        {sourcesLine(lang)}{" "}
        <a className="fx-link fx-muted inline-flex min-h-11 items-center text-[14px]" href="#SOURCES-1">{f.registryLine.replace("{id}", "SOURCES-1")}</a>
      </p>
      <p className="mt-2 max-w-[64ch] text-[18px] leading-snug sm:text-[20px]" data-testid="sources-regle"><strong>{RULE[lang]}</strong></p>
      <p className="fx-muted mt-4 max-w-[64ch] text-[16px] leading-relaxed">{f.lead}</p>

      <section className="mt-10" aria-labelledby="fx-src-today">
        <h2 id="fx-src-today" className="fx-caps fx-muted mb-4">{f.today}</h2>
        <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2">{TODAY.map(source)}</ul>
      </section>
      <section className="mt-10" aria-labelledby="fx-src-tomorrow">
        <h2 id="fx-src-tomorrow" className="fx-caps fx-muted mb-4">{f.tomorrow}</h2>
        <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">{TOMORROW.map(source)}</ul>
      </section>
      <section className="mt-10" aria-labelledby="fx-src-excluded">
        <h2 id="fx-src-excluded" className="fx-caps fx-muted mb-4">{f.excludedTitle}</h2>
        <ul className="border-t border-[var(--fx-line)]">
          {(Object.entries(SOURCE_MAP.ecartees.familles) as [Family, string[]][]).map(([family, lines]) => (
            <li key={family} className="flex gap-4 border-b border-[var(--fx-line)] py-3 text-[15px] leading-snug" data-testid="ecartee">
              <span className="fx-mono fx-muted w-6 shrink-0 text-right">{lines.length}</span>
              <span>{f.excluded[family]}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="mt-14" aria-labelledby="fx-src-measured">
        <h2 id="fx-src-measured" className="fx-display text-[30px]">{f.measuresTitle}</h2>
        <p className="fx-muted mt-2 max-w-[64ch] text-[15px] leading-relaxed">{m.intro}</p>
        {lang === "de" ? <p className="fx-muted mt-2 text-[13px]">{m.registryNote}</p> : null}
        <h3 className="fx-caps fx-muted mb-1 mt-8">{m.measured}</h3>
        <ul className="border-t border-[var(--fx-line)]">{MEASURED.map(row)}</ul>
        <h3 className="fx-caps fx-muted mb-1 mt-8">{f.estimatedTitle}</h3>
        <ul className="border-t border-[var(--fx-line)]">{ESTIMATED.map(row)}</ul>
        <h3 className="fx-caps fx-muted mb-1 mt-8">{m.fictional}</h3>
        <ul className="border-t border-[var(--fx-line)]">{FICTIONAL.map(row)}</ul>
      </section>

      <section className="mt-12" aria-labelledby="fx-src-limits">
        <h2 id="fx-src-limits" className="fx-caps fx-muted mb-3">{f.limitsTitle}</h2>
        <ul className="border-t border-[var(--fx-line)]">
          {[m.l1, m.l2, m.l3, f.l4].map((x) => <li key={x} className="border-b border-[var(--fx-line)] py-3 text-[15px] leading-snug">{x}</li>)}
        </ul>
        <div className="fx-card mt-6 p-5">
          <p className="fx-caps fx-muted">{m.missing}</p>
          <p className="mt-2 max-w-[64ch] text-[15px] leading-relaxed">{m.missingText}</p>
        </div>
      </section>

      <details className="mt-12">
        <summary className="fx-caps fx-muted flex min-h-11 items-center">{f.registryAll.replace("{n}", String(others.length))}</summary>
        <ul className="mt-2 border-t border-[var(--fx-line)]">{others.map(row)}</ul>
      </details>
    </div>
  );
}
