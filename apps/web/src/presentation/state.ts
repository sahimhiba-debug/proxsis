// The actions of a story in the proof dossier (Stories.tsx, shown whole by Proofs.tsx): open a source, reveal the next
// part. The former presentation by steps, and its state machine, were retired with it (the visit has its own state).
export type Action = { type: "openSource"; url: string } | { type: "reveal"; n: number };

/** Every part of a story revealed at once. */
export const ALL = 99;
