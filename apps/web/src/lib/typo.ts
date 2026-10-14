// French typography for texts we write: a no-break space before « : ; ? ! » » and after « « », so that no sign starts a
// line. Only spaces change; German text is left as it is.

export function frenchSpaces(text: string, lang: "fr" | "de"): string {
  if (lang !== "fr") return text;
  return text.replace(/ ([:;?!»])/g, "\u00a0$1").replace(/« /g, "«\u00a0");
}

/** The same, through every string of a nested object of French texts (the shape and the keys stay the same). */
export function frenchDeep<T>(x: T): T {
  if (typeof x === "string") return frenchSpaces(x, "fr") as T;
  if (Array.isArray(x)) return x.map(frenchDeep) as T;
  if (x && typeof x === "object") return Object.fromEntries(Object.entries(x).map(([k, v]) => [k, frenchDeep(v)])) as T;
  return x;
}
