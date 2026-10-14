import { writeStored } from "@/lib/useStored";

// Presenter preferences kept on this computer only (not in the session state: they do not travel to the phone).
export const PREF_MOTION = "proxsis.presentation.motion";
export const PREF_PROJECTION = "proxsis.presentation.projection";

/** Storage refused: the preference is kept in memory for this visit (« Sans mouvement » still works). */
export function setPref(key: string, v: string) {
  writeStored(key, v);
}
