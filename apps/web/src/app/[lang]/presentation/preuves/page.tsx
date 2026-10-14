import histoires from "@/data/presentation/histoires.json";
import { preloadFonts } from "@/lib/fonts";
import { isLang, type Lang } from "@/lib/i18n";
import { COPY_C } from "@/presentation/copy_c";
import { ProofDossier } from "@/presentation/Proofs";
import type { StoriesData } from "@/presentation/storyData";

export async function generateMetadata({ params }: PageProps<"/[lang]/presentation/preuves">) {
  const { lang } = await params;
  return { title: COPY_C[isLang(lang) ? lang : "fr"].dir.preuves.title };
}

// « Votre prochain lundi », proof dossier: the three dated stories of act 4, in reserve since 07.10.2026.
export default async function ProofsPage({ params }: PageProps<"/[lang]/presentation/preuves">) {
  const { lang: l } = await params;
  const lang = (isLang(l) ? l : "fr") as Lang;
  preloadFonts("presentation");
  // checked against its schema, and the schema against this type (src/lib/schema.test.ts)
  return <ProofDossier lang={lang} stories={histoires as unknown as StoriesData} />;
}
