// « Qui sommes-nous » (suite 6 of Hiba, § 5): only the members Hiba gave, as she wrote them, and never an empty slot. A
// production build stops (next.config.ts) if a name or a role is missing; the contact shows only when Hiba gives one.

export interface Team {
  membres: { nom: string | null; role: string | null }[];
  contact: string | null;
}

/** Every empty slot the page would show, as « membre 1 : nom »…; empty when there is none. No contact is not an empty
 *  slot: the page simply does not show one. */
export function teamMissing(t: Team): string[] {
  const missing = t.membres.flatMap((m, i) => [
    ...(m.nom ? [] : [`membre ${i + 1} : nom`]),
    ...(m.role ? [] : [`membre ${i + 1} : rôle`]),
  ]);
  if (!t.membres.length) missing.push("membres");
  return missing;
}
