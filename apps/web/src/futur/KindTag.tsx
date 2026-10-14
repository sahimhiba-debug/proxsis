import type { Dict } from "@/i18n/dictionaries";

export type DataKind = "reel" | "fictif" | "estimation" | "maison" | "hypothese" | "publique";

/** What a figure or a line is (real, fictional, estimated, Flexsis's own, a hypothesis, read in a public source), always written in words. */
export function KindTag({ kind, t }: { kind: DataKind; t: Dict }) {
  return <span className="fx-tag" data-kind={kind}>{t.label[kind]}</span>;
}
