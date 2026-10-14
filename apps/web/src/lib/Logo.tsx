// The Proxsis logo (docs/identite/logo, 07.10.2026): the word drawn from Urbanist outlines at weight 820,
// the dot of the « i » an orange diagonal. Letters in currentColor (black on light, white on dark), the dot always
// orange. Paths copied from proxsis-logo-noir-orange.svg, unchanged (its provenance metadata left out).
// Animation (IDENTITE.md): the letters rise from the baseline one after the other (35 ms apart, 0.42 s each), then
// the diagonal lands with a slight bounce; nothing moves without motion (identite.css).
import { DOT, LETTERS, VIEWBOX } from "@/iris/logo-paths";

export function Logo({ className, animate = false, title = "Proxsis" }: { className?: string; animate?: boolean; title?: string }) {
  return (
    <svg className={["px-logo", className].filter(Boolean).join(" ")} data-animate={animate || undefined} viewBox={VIEWBOX}
      role="img" aria-label={title} xmlns="http://www.w3.org/2000/svg">
      <g fill="currentColor">
        {LETTERS.map((d, i) => <path key={i} d={d} style={{ ["--i" as string]: i }} />)}
      </g>
      <path className="px-logo-dot" fill="#E6530F" d={DOT} />
    </svg>
  );
}
