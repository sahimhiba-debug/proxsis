import type { Metadata, Viewport } from "next";
import { notFound } from "next/navigation";
import "../globals.css";
import "../fonts.css";
import { getDict, isLang, LANGS } from "@/lib/i18n";

export const dynamicParams = false;

export function generateStaticParams() {
  return LANGS.map((lang) => ({ lang }));
}

export async function generateMetadata({ params }: LayoutProps<"/[lang]">): Promise<Metadata> {
  const { lang } = await params;
  const t = getDict(lang);
  // a demonstration, not a public site: never indexed (the deployment is also meant to sit behind Vercel protection)
  return { title: { default: t.app.name, template: `%s · ${t.app.name}` }, description: t.app.tagline,
    robots: { index: false, follow: false } };
}

export const viewport: Viewport = { width: "device-width", initialScale: 1, themeColor: "#ffffff" };

export default async function LangLayout({ children, params }: LayoutProps<"/[lang]">) {
  const { lang } = await params;
  if (!isLang(lang)) notFound();
  return (
    <html lang={lang === "de" ? "de-CH" : "fr-CH"}>
      <body className="min-h-dvh">{children}</body>
    </html>
  );
}
