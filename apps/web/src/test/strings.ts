// For the tests that read every text of a screen or of a data file (vocabulary, name, both languages).

/** Every string inside a value (nested objects and arrays); `skip` leaves out the keys that are not interface text. */
export function allStrings(o: unknown, skip: (key: string) => boolean = () => false): string[] {
  if (typeof o === "string") return [o];
  if (Array.isArray(o)) return o.flatMap((x) => allStrings(x, skip));
  if (o && typeof o === "object") return Object.entries(o).flatMap(([k, v]) => (skip(k) ? [] : allStrings(v, skip)));
  return [];
}
