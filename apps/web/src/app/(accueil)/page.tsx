import Link from "next/link";
import { getDict } from "@/lib/i18n";
import { LangRedirect } from "./LangRedirect";

// The root, before a language is chosen: both languages side by side (the browser's language opens at once, see
// LangRedirect; this page is what shows without JavaScript).
const fr = getDict("fr").app;
const de = getDict("de").app;

export default function Home() {
  return (
    <main className="mx-auto flex min-h-dvh max-w-md flex-col justify-center gap-6 px-4">
      <div>
        <h1 className="text-3xl font-light tracking-tight">{fr.name}</h1>
        <p className="text-sm text-muted-foreground">{fr.signature} · <span lang="de-CH">{de.signature}</span></p>
        <p className="mt-1 text-xs uppercase tracking-wide text-muted-foreground">{fr.prototype} · <span lang="de-CH">{de.prototype}</span></p>
      </div>
      <p className="text-muted-foreground">{getDict("fr").home.choose} · <span lang="de-CH">{getDict("de").home.choose}</span></p>
      <div className="grid grid-cols-2 gap-3">
        <Link href="/fr/" hrefLang="fr" className="rounded-lg border p-4 text-center font-semibold hover:bg-muted">
          {fr.langName}
        </Link>
        <Link href="/de/" hrefLang="de" lang="de-CH" className="rounded-lg border p-4 text-center font-semibold hover:bg-muted">
          {de.langName}
        </Link>
      </div>
      <LangRedirect />
    </main>
  );
}
