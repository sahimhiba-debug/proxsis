import type { CSSProperties } from "react";

/**
 * A number that builds up to its real value, in CSS (a registered integer property animated from 0): it runs from the
 * first paint, needs no JavaScript, never flashes the final value first, and stays still when motion is reduced.
 * With `decimals`, the whole part builds up and the decimals stay (« 5,3 », « 66,8 % »: the decimal of CLAIMS is kept).
 * The exact value is always in the DOM for screen readers; the width is reserved so the label never moves.
 */
export function Counter({ value, decimals = 0, lang = "fr", suffix = "", className }: {
  value: number; decimals?: number; lang?: string; suffix?: string; className?: string;
}) {
  const scale = 10 ** decimals;
  const rounded = Math.round(value * scale) / scale;
  const whole = Math.trunc(rounded);
  const frac = decimals ? String(Math.round(Math.abs(rounded - whole) * scale)).padStart(decimals, "0") : "";
  const sep = lang === "de" ? "." : ",";
  const style = { ["--to" as string]: whole, ["--digits" as string]: String(whole).length } as CSSProperties;
  return (
    <span className={className}>
      <span aria-hidden>
        <span className={decimals ? "fx-count text-right" : "fx-count"} style={style} />
        {decimals ? `${sep}${frac}` : null}
        {suffix}
      </span>
      <span className="sr-only">{decimals ? `${whole}${sep}${frac}` : whole}{suffix}</span>
    </span>
  );
}
