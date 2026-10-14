import type { Metadata } from "next";
import { getDict } from "@/lib/i18n";
import "../globals.css";

export const metadata: Metadata = { title: getDict("fr").app.name,
  description: `${getDict("fr").app.signature} · ${getDict("de").app.signature}`, robots: { index: false, follow: false } };

export default function HomeLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr-CH">
      <body className="min-h-dvh">{children}</body>
    </html>
  );
}
