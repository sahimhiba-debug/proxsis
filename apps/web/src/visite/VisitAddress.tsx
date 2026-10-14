"use client";

import { useSyncExternalStore } from "react";
import { visitPath } from "./paths";

const noop = () => () => {};

/** The address of the visit, as the reader opened it (printed on paper, it leads back to the visit). */
export function VisitAddress({ lang, label }: { lang: "fr" | "de"; label: string }) {
  const host = useSyncExternalStore(noop, () => window.location.host, () => "");
  // on paper only: on screen the page has its link back, and the address (with its port) would differ between machines
  return host ? <p className="d-small d-print-only" data-testid="visit-address">{label.replace("{url}", `${host}${visitPath(lang)}`)}</p> : null;
}
