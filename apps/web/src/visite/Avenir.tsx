// The future in three steps (brief of 07.10.2026, suite 2, § 7), in « Une décision » and in the conclusion: « Si la
// solution vous intéresse », then for each step what he gains, what he gives and when he can stop; the third only if the
// threshold is reached, with the door (suite 9, § 8: « Si les résultats sont là : Iris installée chez Flexsis… », then
// « Demain, si Flexsis le souhaite », a possible future, never a function that exists, with its guardrails said at the
// same time and, in the future, the sentence of the silence); then the years ahead, with their public sources visible.
// Proxsis does not have those contracts in its data, and never says so.
import { ArrowUpRight } from "lucide-react";
import { Plus } from "@/lib/Plus";
import { VISIT_COPY } from "./copy";
import { PAGES_COPY } from "./pages";

const IRIS = "Iris"; // the speaker of the sentence of the silence (her name, the same in both languages)

/** The sources of « Les prochaines années », as CLAIMS.md reads them (avenir.test.ts compares them with claims.json). */
export const YEARS_SOURCES = [
  { claims: "EXT-A9-FINGES", label: "swissinfo.ch, 05.08.2026",
    url: "https://www.swissinfo.ch/fre/travers%c3%a9e-du-bois-de-finges%3a-travaux-pr%c3%a9liminaires-bien-avanc%c3%a9s/91848472" },
  { claims: "EXT-HOPITAUX-VS", label: "latele.ch, 09.03.2026",
    url: "https://latele.ch/articles/hopitaux-vs-76-millions-pour-les-equipements-de-sion-et-de-brigue" },
] as const;

export function Avenir({ lang, id }: { lang: "fr" | "de"; id: string }) {
  const t = VISIT_COPY[lang].avenir;
  return (
    <section className="v-avenir" aria-labelledby={`${id}-titre`} data-testid="avenir">
      <header>
        <h2 id={`${id}-titre`} className="d-sub">{t.title}</h2>
        <p className="d-lead">{t.lead}</p>
      </header>
      <ol className="v-avenir-steps">
        {t.steps.map((st, i) => (
          <li key={st.name} className="v-avenir-step" data-testid="avenir-step">
            <h3><span className="v-avenir-num d-num" aria-hidden>{i + 1}</span>{st.name}<span className="v-avenir-who">{st.who}</span></h3>
            <dl>
              <div><dt>{t.gain}</dt><dd>{st.gain}</dd></div>
              <div><dt>{t.give}</dt><dd>{st.give}</dd></div>
              <div><dt>{t.stop}</dt><dd>{st.stop}</dd></div>
            </dl>
          </li>
        ))}
        <li className="v-avenir-step" data-testid="avenir-step">
          <h3><span className="v-avenir-num d-num" aria-hidden>3</span>{t.third.name}<span className="v-avenir-who">{t.third.who}</span></h3>
          <p className="v-avenir-lead" data-testid="avenir-porte">{t.third.lead}</p>
          <ul className="v-list">{t.third.items.map((x) => <li key={x}>{x}</li>)}</ul>
          {/* the door (suite 9, § 8): closed at first; on a phone, its guardrails under « En savoir plus » (§ 10) */}
          <details className="v-iris-demain" data-testid="iris-demain">
            <summary>{t.iris.title}</summary>
            <p>{t.iris.today}</p>
            <p>{t.iris.tomorrow}</p>
            <p>{t.iris.apertus}</p>
            <p className="v-porte-silence" data-testid="porte-silence">
              <span className="v-porte-qui">{IRIS}</span>{lang === "fr" ? `«\u00a0${t.iris.silence}\u00a0»` : `«${t.iris.silence}»`}
            </p>
            <Plus label={PAGES_COPY[lang].plus} about={t.iris.guardsTitle}>
              <p className="px-bref" data-testid="garde-fou-bref">{t.iris.guards[0]}</p>
              <h4 className="px-plus-detail">{t.iris.guardsTitle}</h4>
              <ul className="v-list px-plus-detail" data-testid="porte-garde-fous">{t.iris.guards.map((x) => <li key={x}>{x}</li>)}</ul>
            </Plus>
            <p className="d-small v-iris-future">{t.iris.future}</p>
          </details>
        </li>
      </ol>
      <div className="v-years" data-testid="years">
        <h3>{t.years.title}</h3>
        <p>{t.years.text}</p>
        <p className="v-years-phrase">{t.years.phrase}</p>
        <p className="d-small d-muted">
          {t.years.sources}{" "}
          {YEARS_SOURCES.map((s, i) => (
            <span key={s.claims}>{i ? " · " : ""}<a className="v-link" href={s.url} target="_blank" rel="noopener noreferrer">{s.label} <ArrowUpRight className="inline size-[0.9em]" aria-hidden /></a></span>
          ))}
        </p>
      </div>
    </section>
  );
}
