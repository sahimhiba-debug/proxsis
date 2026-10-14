"use client";

import { PButton } from "@/presentation/ui";

/** Opens the browser's print dialog (« Enregistrer au format PDF »): the PDF is made in the browser, never on a server. */
export function PrintButton({ label }: { label: string }) {
  return <PButton variant="action" onClick={() => window.print()}>{label}</PButton>;
}
