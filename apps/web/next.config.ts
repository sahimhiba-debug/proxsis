import type { NextConfig } from "next";
import team from "./src/data/equipe/equipe.json";
import { teamMissing, type Team } from "./src/lib/team";

// Security headers of the served site (Vercel, `next start`). Everything the pages load comes from the site itself:
// scripts and styles (Next's inline bootstrap needs 'unsafe-inline'), the fonts served with the app, the grain drawn as a
// data: image; the phone of the presentation frames the site's own pages. NEXT_PUBLIC_SUPABASE_URL, when set, opens a
// call out to the call-feedback table (ready for the pilot; no page calls it today). Not in development (eval).
const supabase = process.env.NEXT_PUBLIC_SUPABASE_URL ? ` ${new URL(process.env.NEXT_PUBLIC_SUPABASE_URL).origin}` : "";
export const SECURITY_HEADERS = [
  { key: "Content-Security-Policy", value: [
    "default-src 'self'", "script-src 'self' 'unsafe-inline'", "style-src 'self' 'unsafe-inline'", "img-src 'self' data:",
    "font-src 'self'", `connect-src 'self'${supabase}`, "frame-src 'self'", "frame-ancestors 'self'", "base-uri 'self'",
    "form-action 'self'", "object-src 'none'",
  ].join("; ") },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "X-Frame-Options", value: "SAMEORIGIN" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=(), payment=(), usb=()" },
];

// « Qui sommes-nous » (brief « à distance », § 5): a production build (Vercel sets VERCEL_ENV=production) stops while a
// member's name or role is missing (lib/team.ts); previews and local builds go on.
const missing = teamMissing(team as Team);
if (process.env.VERCEL_ENV === "production" && missing.length) {
  throw new Error(`« Qui sommes-nous » incomplet, pas de mise en production : ${missing.join(", ")} (src/data/equipe/equipe.json)`);
}

// STATIC_EXPORT=1 builds the offline snapshot (`out/`): every page is pre-rendered, nothing needs a server (and no
// header either: the copy is opened from a disk or a local server).
const nextConfig: NextConfig = {
  output: process.env.STATIC_EXPORT ? "export" : undefined,
  // a separate build folder when another server already serves .next (e.g. NEXT_DIST_DIR=.next-verif)
  distDir: process.env.NEXT_DIST_DIR || ".next",
  trailingSlash: true,
  images: { unoptimized: true },
  poweredByHeader: false,
  devIndicators: false, // the development badge would sit on the presentation's mentions (captures, rehearsals)
  ...(process.env.STATIC_EXPORT || process.env.NODE_ENV !== "production"
    ? {}
    : { headers: async () => [{ source: "/:path*", headers: SECURITY_HEADERS }] }),
};

export default nextConfig;
