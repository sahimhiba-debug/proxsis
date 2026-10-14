/** An amount as simap publishes it, exact (its content is not changed, AGB API simap ch. 5), written the Swiss way in
 *  both languages: « 1'574'663.35 », the centimes only when there are some. Client-safe (no dictionary). */
export function swissAmount(n: number): string {
  const [units, cents] = Math.abs(n).toFixed(2).split(".");
  const grouped = units.replace(/\B(?=(\d{3})+(?!\d))/g, "'");
  return `${n < 0 ? "−" : ""}${cents === "00" ? grouped : `${grouped}.${cents}`}`;
}
