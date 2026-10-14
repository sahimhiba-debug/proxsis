/**
 * Numbers written the Swiss way, identically on the server and in the browser (Intl's separators differ between
 * Node's and Chrome's ICU, which broke hydration): thin space between thousands in French, ’ in German.
 */
export function groupDigits(n: number, decimals: number, locale: string): string {
  const de = locale.startsWith("de");
  const [whole, frac] = Math.abs(n).toFixed(decimals).split(".");
  const grouped = whole.replace(/\B(?=(\d{3})+(?!\d))/g, de ? "’" : "\u202f");
  return `${n < 0 && Number(whole + (frac ?? "")) !== 0 ? "−" : ""}${grouped}${frac ? (de ? "." : ",") + frac : ""}`;
}
