"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "motion/react";
import { CalendarCheck, LayoutDashboard, Map, Repeat, ShieldCheck } from "lucide-react";
import { useRole } from "@/components/shell/RoleSwitcher";
import { SPRING } from "./motion";

// A German label too long for its tab at 360 px breaks only where a hyphen makes sense (« Einsatz-ende », « Melde-pflicht »),
// with a soft hyphen; never in the middle of a part (Q18, Hiba, 13.10.2026: no text cut on a phone)
const COMPOUNDS: [string, string][] = [["Einsatzende", "Einsatz\u00ADende"], ["Meldepflicht", "Melde\u00ADpflicht"]];
const breakable = (s: string) => COMPOUNDS.reduce((t, [word, soft]) => (t === word ? soft : t), s);

/** Frosted-glass tab bar: fine ivory icons, the active tab in copper, its indicator slides from one tab to the next. */
export function TabBar({ lang, labels }: { lang: string; labels: Record<string, string> }) {
  const path = usePathname() || "";
  const consultant = useRole().consultant;
  const items = [
    { href: `/${lang}/semaine/${consultant}/`, match: ["/semaine", "/entreprise"], label: labels.semaine, Icon: CalendarCheck },
    { href: `/${lang}/carte/`, match: ["/carte"], label: labels.carte, Icon: Map },
    { href: `/${lang}/redeploiement/`, match: ["/redeploiement"], label: labels.redeploiement, Icon: Repeat },
    { href: `/${lang}/conformite/`, match: ["/conformite"], label: labels.conformite, Icon: ShieldCheck },
    { href: `/${lang}/agence/`, match: ["/agence"], label: labels.agence, Icon: LayoutDashboard },
  ];
  return (
    <nav aria-label={labels.menu} className="fx-tabbar">
      <ul className="grid grid-cols-5">
        {items.map(({ href, match, label, Icon }) => {
          const active = match.some((m) => path.includes(m));
          return (
            <li key={href}>
              <Link href={href} aria-current={active ? "page" : undefined} className="fx-tab">
                {active ? <motion.span layoutId="fx-tab-indicator" className="fx-tab-indicator" transition={SPRING} /> : null}
                <Icon aria-hidden />
                <span>{breakable(label)}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
