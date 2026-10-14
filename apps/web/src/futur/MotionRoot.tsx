"use client";

import { MotionConfig } from "motion/react";
import type { ReactNode } from "react";

// Reduced motion is honoured by Motion itself (no transform; the page renders the same HTML on server and client).
export function MotionRoot({ children }: { children: ReactNode }) {
  return <MotionConfig reducedMotion="user">{children}</MotionConfig>;
}
