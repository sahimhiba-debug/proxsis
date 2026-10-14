import { preloadFonts } from "@/lib/fonts";
import { isLang, type Lang } from "@/lib/i18n";
import { VisitNotes } from "@/visite/NotesWindow";
import { NOTE_ROWS } from "@/visite/notes";

export async function generateMetadata({ params }: PageProps<"/[lang]/presentation/notes">) {
  const { lang } = await params;
  return { title: NOTE_ROWS[isLang(lang) ? lang : "fr"].title };
}

// Presenter mode: narration and notes of the visit, in a separate window (never on the shared screen).
export default async function NotesPage({ params }: PageProps<"/[lang]/presentation/notes">) {
  const { lang: l } = await params;
  const lang = (isLang(l) ? l : "fr") as Lang;
  preloadFonts("presentation");
  return <VisitNotes lang={lang} />;
}
