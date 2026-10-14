// One curve, three durations (brief, « niveau de finition »): every transition links two states, nothing decorative.
export const EASE = [0.2, 0.7, 0.1, 1] as const;
export const DUR = { short: 0.22, medium: 0.42, long: 0.7 } as const;
export const T = {
  short: { duration: DUR.short, ease: EASE },
  medium: { duration: DUR.medium, ease: EASE },
  long: { duration: DUR.long, ease: EASE },
} as const;
