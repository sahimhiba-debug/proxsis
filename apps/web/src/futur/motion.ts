// One curve family for the whole app, the same as the presentation: short, precise springs for touch, the curve for the
// rest. Every movement has its still version (prefers-reduced-motion, checked by useReducedMotion in each component).
export const EASE = [0.2, 0.7, 0.1, 1] as const;
export const DUR = { short: 0.22, medium: 0.42, long: 0.7 } as const;
export const SPRING = { type: "spring", stiffness: 520, damping: 34, mass: 0.6 } as const; // press, tab indicator
// a recent contract breathes twice (about 4 s), then stays still: moving content stops within 5 s (WCAG 2.2.2)
export const PULSE_REPEAT = 1;
