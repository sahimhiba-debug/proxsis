"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { AnimatePresence, motion, useMotionValueEvent, useScroll } from "motion/react";
import { ChevronDown } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { RoleSwitcher } from "@/components/shell/RoleSwitcher";
import { Brand } from "./Brand";
import { DUR, EASE } from "./motion";

type Consultant = { code: string; libelle: string; agence: string; agenceNom: string; specialite: string };

/** The bar that tightens on scroll (glass once the page moves), with the discreet language switch and the « Démo » menu. */
export function Header({ lang, brand, demo, roleLabels, consultants }: {
  lang: string; brand: { name: string; signature: string; prototype: string }; demo: string;
  roleLabels: { title: string; consultant: string; chef: string; directeur: string };
  consultants: Consultant[];
}) {
  const { scrollY } = useScroll();
  const [compact, setCompact] = useState(false);
  // two thresholds (hysteresis): the bar does not flicker when the page rests near the top
  useMotionValueEvent(scrollY, "change", (y) => setCompact((c) => (c ? y > 8 : y > 40)));
  const [open, setOpen] = useState(false);
  const menu = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!open) return;
    const away = (e: MouseEvent | KeyboardEvent) => {
      if (e instanceof KeyboardEvent ? e.key === "Escape" : !menu.current?.contains(e.target as Node)) setOpen(false);
    };
    window.addEventListener("mousedown", away);
    window.addEventListener("keydown", away);
    return () => { window.removeEventListener("mousedown", away); window.removeEventListener("keydown", away); };
  }, [open]);
  const path = usePathname() || `/${lang}/`;
  const other = lang === "fr" ? "de" : "fr";
  const switchTo = path.replace(/^\/(fr|de)(?=\/|$)/, `/${other}`);
  return (
    <header className="fx-head" data-compact={compact}>
      <div className="fx-col flex items-center justify-between gap-3">
        <Brand href={`/${lang}/application/`} {...brand} />
        <div className="fx-tools flex items-center gap-2" ref={menu}>
          <Link href={switchTo} hrefLang={other} className="fx-tool" data-testid="lang-switch">{other.toUpperCase()}</Link>
          <div className="relative">
            <button type="button" className="fx-tool" aria-expanded={open} aria-controls="fx-demo-panel" onClick={() => setOpen((v) => !v)}>
              {demo} <ChevronDown aria-hidden className="size-3.5" strokeWidth={1.5} />
            </button>
            <AnimatePresence>
              {open ? (
                <motion.div id="fx-demo-panel" className="fx-menu" initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -6 }} transition={{ duration: DUR.short, ease: EASE }}>
                  <p className="fx-caps fx-muted mb-2" aria-hidden>{roleLabels.title}</p>
                  <RoleSwitcher lang={lang} labels={roleLabels} consultants={consultants} />
                </motion.div>
              ) : null}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </header>
  );
}
