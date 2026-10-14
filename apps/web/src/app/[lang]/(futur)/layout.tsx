import "@/futur/futur.css";
import type { Viewport } from "next";
import Link from "next/link";
import { Header } from "@/futur/Header";
import { MotionRoot } from "@/futur/MotionRoot";
import { TabBar } from "@/futur/TabBar";
import { allConsultants, meta } from "@/lib/data";
import { getDict, type Lang } from "@/lib/i18n";
import { consultantLabel } from "@/lib/roleLabel";
import { preloadFonts } from "@/lib/fonts";

// The consultant's tool, in the « futurisme suisse » frame (brief of Hiba, 06.10.2026). The fonts are served by the site
// itself (public/fonts, lib/fonts.ts): the offline copy works.

export const viewport: Viewport = { themeColor: "#121212", colorScheme: "dark" };

export default async function FuturLayout({ children, params }: LayoutProps<"/[lang]">) {
  const { lang: l } = await params;
  const lang = l as Lang;
  const t = getDict(lang);
  preloadFonts("app");
  const consultants = allConsultants().map((c) => ({
    code: c.code,
    libelle: consultantLabel(t, lang, c.specialite),
    agence: c.agence.id,
    agenceNom: c.agence.nom,
    specialite: c.specialite,
  }));
  return (
    <MotionRoot>
    <div className="fx">
      <a href="#contenu" className="sr-only focus:not-sr-only focus:absolute focus:left-3 focus:top-3 focus:z-50 focus:rounded-lg focus:bg-[var(--fx-2)] focus:p-3">
        {t.app.skip}
      </a>
      <Header lang={lang} brand={{ name: t.app.name, signature: t.app.signature, prototype: t.app.prototype }} demo={t.fx.demo}
        roleLabels={{ title: t.role.title, consultant: t.role.consultant, chef: t.role.chef, directeur: t.role.directeur }}
        consultants={consultants} />
      <main id="contenu">{children}</main>
      <footer className="fx-col fx-muted space-y-2 pb-40 pt-16 text-[14px] leading-relaxed">
        <p data-testid="simap-mention">{t.banner.simap} « {meta.mention_simap} »</p>
        <p>{t.fx.footerData}</p>
        {t.fx.reviewDe ? <p data-testid="review-de">{t.fx.reviewDe}</p> : null}
        <p>
          {t.fx.footerClaims}{" "}
          <Link className="fx-link inline-flex min-h-11 min-w-11 items-center justify-center" href={`/${lang}/mesures/`}>{t.nav.mesures}</Link>{" · "}
          <Link className="fx-link inline-flex min-h-11 min-w-11 items-center justify-center" href={`/${lang}/presentation/`}>{t.nav.presentation}</Link>{" · "}
          <Link className="fx-link inline-flex min-h-11 min-w-11 items-center justify-center" href={`/${lang}/roi/`}>{t.nav.roi}</Link>
        </p>
      </footer>
      <TabBar lang={lang} labels={{ semaine: t.nav.semaine, carte: t.nav.carte, redeploiement: t.nav.redeploiement,
        conformite: t.nav.conformite, agence: t.nav.agence, menu: t.nav.menu }} />
    </div>
    </MotionRoot>
  );
}
