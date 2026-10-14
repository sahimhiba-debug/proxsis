// Adapted from Magic UI « iphone » (free registry:ui component, not Pro): https://magicui.design/r/iphone.json,
// identical to apps/www/registry/magicui/iphone.tsx in github.com/magicuidesign/magicui at cdb348c (2026-10-05).
// Copyright (c) Magic UI — MIT License (full text and provenance in ./NOTICE.md).
// Changes: the screen holds any content (here the live app) instead of an image or a video; the colours follow the
// « Votre prochain lundi » direction (graphite body, thin rule, dark glass edge), without light/dark variants; the
// SVG lets pointer events through to the screen; mask ids are unique per instance; the paper's sober drop shadow sits
// under the body. No gradient, glow, reflection or blur.
import { useId, type ReactNode } from "react";
import { FRAME, SCREEN } from "./script";

const SCREEN_X = 21.25;
const SCREEN_Y = 19.25;
const SCREEN_WIDTH = 389.5;
const SCREEN_HEIGHT = 843.5;

/** The phone at its own size (433 × 882 units); the caller scales it. Children fill the 390 × 844 screen, whose
 *  background follows the page shown (`screen`). */
export function PhoneFrame({ children, label, screen }: { children: ReactNode; label: string; screen?: string }) {
  const id = `ph${useId().replace(/[^a-zA-Z0-9_-]/g, "")}`;
  const punch = `url(#${id}-punch)`;
  return (
    <div className="ph-frame" data-testid="phone-frame" role="group" aria-label={label}
      style={{ width: FRAME.width, height: FRAME.height }}>
      <div className="ph-shadow" aria-hidden />
      <div className="ph-screen" style={{ left: FRAME.screenX, top: FRAME.screenY, width: SCREEN.width,
        height: SCREEN.status + SCREEN.app, borderRadius: FRAME.radius, background: screen }}>
        {children}
      </div>
      <svg viewBox={`0 0 ${FRAME.width} ${FRAME.height}`} fill="none" xmlns="http://www.w3.org/2000/svg" className="ph-svg" aria-hidden>
        <g mask={punch}>
          <path className="ph-body" d="M2 73C2 32.6832 34.6832 0 75 0H357C397.317 0 430 32.6832 430 73V809C430 849.317 397.317 882 357 882H75C34.6832 882 2 849.317 2 809V73Z" />
          <path className="ph-key" d="M0 171C0 170.448 0.447715 170 1 170H3V204H1C0.447715 204 0 203.552 0 203V171Z" />
          <path className="ph-key" d="M1 234C1 233.448 1.44772 233 2 233H3.5V300H2C1.44772 300 1 299.552 1 299V234Z" />
          <path className="ph-key" d="M1 319C1 318.448 1.44772 318 2 318H3.5V385H2C1.44772 385 1 384.552 1 384V319Z" />
          <path className="ph-key" d="M430 279H432C432.552 279 433 279.448 433 280V384C433 384.552 432.552 385 432 385H430V279Z" />
          <path className="ph-bezel" d="M6 74C6 35.3401 37.3401 4 76 4H356C394.66 4 426 35.3401 426 74V808C426 846.66 394.66 878 356 878H76C37.3401 878 6 846.66 6 808V74Z" />
        </g>
        <path className="ph-key" opacity="0.5" d="M174 5H258V5.5C258 6.60457 257.105 7.5 256 7.5H176C174.895 7.5 174 6.60457 174 5.5V5Z" />
        <path className="ph-edge" mask={punch}
          d={`M${SCREEN_X} 75C${SCREEN_X} 44.2101 46.2101 ${SCREEN_Y} 77 ${SCREEN_Y}H355C385.79 ${SCREEN_Y} 410.75 44.2101 410.75 75V807C410.75 837.79 385.79 862.75 355 862.75H77C46.2101 862.75 ${SCREEN_X} 837.79 ${SCREEN_X} 807V75Z`} />
        <path className="ph-island" d="M154 48.5C154 38.2827 162.283 30 172.5 30H259.5C269.717 30 278 38.2827 278 48.5C278 58.7173 269.717 67 259.5 67H172.5C162.283 67 154 58.7173 154 48.5Z" />
        <path className="ph-island" d="M249 48.5C249 42.701 253.701 38 259.5 38C265.299 38 270 42.701 270 48.5C270 54.299 265.299 59 259.5 59C253.701 59 249 54.299 249 48.5Z" />
        <path className="ph-lens" d="M254 48.5C254 45.4624 256.462 43 259.5 43C262.538 43 265 45.4624 265 48.5C265 51.5376 262.538 54 259.5 54C256.462 54 254 51.5376 254 48.5Z" />
        <defs>
          <mask id={`${id}-punch`} maskUnits="userSpaceOnUse">
            <rect x="0" y="0" width={FRAME.width} height={FRAME.height} fill="white" />
            <rect x={SCREEN_X} y={SCREEN_Y} width={SCREEN_WIDTH} height={SCREEN_HEIGHT} rx={FRAME.radius} ry={FRAME.radius} fill="black" />
          </mask>
        </defs>
      </svg>
    </div>
  );
}
