"use client";

import { useRouter } from "next/navigation";
import { useMemo } from "react";
import { notifyStored, useStoredString } from "@/lib/useStored";

type Role = "consultant" | "chef" | "directeur";
const ROLE_KEY = "proxsis.role.v1";
const KEY = ROLE_KEY;

interface RoleState {
  role: Role;
  consultant: string;
  agence: string;
}

const DEFAULT_ROLE: RoleState = { role: "consultant", consultant: "M1", agence: "martigny" };

const ROLES: readonly unknown[] = ["consultant", "chef", "directeur"] satisfies Role[];
const CODE = /^[a-z0-9-]{1,24}$/i; // a consultant code (« M1 ») or an agency id (« martigny »): it goes into a URL

/** The role kept on this device, field by field: anything unreadable or unexpected falls back to the default. */
export function parseRole(raw: string | null): RoleState {
  try {
    const v: unknown = JSON.parse(raw || "{}");
    const o = v !== null && typeof v === "object" ? (v as Record<string, unknown>) : {};
    const code = (x: unknown, fallback: string) => (typeof x === "string" && CODE.test(x) ? x : fallback);
    return {
      role: ROLES.includes(o.role) ? (o.role as Role) : DEFAULT_ROLE.role,
      consultant: code(o.consultant, DEFAULT_ROLE.consultant),
      agence: code(o.agence, DEFAULT_ROLE.agence),
    };
  } catch {
    return DEFAULT_ROLE;
  }
}

export function readRole(): RoleState {
  try {
    return parseRole(window.localStorage.getItem(KEY));
  } catch {
    return DEFAULT_ROLE;
  }
}

export function useRole(): RoleState {
  const raw = useStoredString(KEY, "{}");
  return useMemo(() => parseRole(raw), [raw]);
}

function writeRole(r: RoleState) {
  try {
    window.localStorage.setItem(KEY, JSON.stringify(r));
  } catch {
    // storage blocked: the role only lasts for this page
  }
  notifyStored();
}

export function homeFor(lang: string, r: RoleState): string {
  if (r.role === "consultant") return `/${lang}/semaine/${r.consultant}/`;
  if (r.role === "chef") return `/${lang}/agence/${r.agence}/`;
  return `/${lang}/agence/`;
}

export function RoleSwitcher({
  lang,
  labels,
  consultants,
}: {
  lang: string;
  labels: { title: string; consultant: string; chef: string; directeur: string };
  consultants: { code: string; libelle: string; agence: string; agenceNom: string; specialite: string }[];
}) {
  const router = useRouter();
  const state = useRole();

  function choose(value: string) {
    const [role, id] = value.split(":");
    const c = consultants.find((x) => x.code === id);
    const next: RoleState =
      role === "consultant" && c
        ? { role: "consultant", consultant: c.code, agence: c.agence }
        : role === "chef"
          ? { ...state, role: "chef", agence: id }
          : { ...state, role: "directeur" };
    writeRole(next);
    router.push(homeFor(lang, next));
  }

  const current =
    state.role === "consultant" ? `consultant:${state.consultant}` : state.role === "chef" ? `chef:${state.agence}` : "directeur:";
  const agencies = Array.from(new Map(consultants.map((c) => [c.agence, c.agenceNom])).entries());
  return (
    <label className="flex items-center gap-1 text-xs">
      <span className="sr-only">{labels.title}</span>
      <select
        value={current}
        onChange={(e) => choose(e.target.value)}
        className="max-w-[11rem] rounded-md border bg-background px-1.5 py-1 text-xs"
        data-testid="role-switcher"
        aria-label={labels.title}
      >
        <optgroup label={labels.consultant}>
          {consultants.map((c) => (
            <option key={c.code} value={`consultant:${c.code}`}>
              {c.libelle} · {c.agenceNom.replace("Flexsis ", "")}
            </option>
          ))}
        </optgroup>
        <optgroup label={labels.chef}>
          {agencies.map(([id, nom]) => (
            <option key={id} value={`chef:${id}`}>
              {labels.chef} · {nom.replace("Flexsis ", "")}
            </option>
          ))}
        </optgroup>
        <option value="directeur:">{labels.directeur}</option>
      </select>
    </label>
  );
}
