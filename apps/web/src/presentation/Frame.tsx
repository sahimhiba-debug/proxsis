"use client";

import "./direction.css";
// the same order everywhere (direction, visit, identity): in production Next groups the sheets, and a page that
// loaded the identity without the visit sheet put visite.css after it, which undid identity rules of equal weight
import "@/visite/visite.css";
import "@/visite/identite.css";
import type { PresentationCopy } from "./copy";
import { MENTION_SIMAP } from "./SimapMention";

/** simap's mandatory mention, verbatim (general terms, ch. 5); on German screens the original plus a labelled translation. */
export function SimapLine({ t, lang }: { t: PresentationCopy; lang: "fr" | "de" }) {
  return (
    <span data-testid="simap-mention">
      {t.source.mention}
      {t.source.mentionOriginal}{lang === "de" ? ": " : "\u00a0: "}«&nbsp;{MENTION_SIMAP}&nbsp;»{lang === "de" ? ` ${t.source.translation}` : ""}
    </span>
  );
}
