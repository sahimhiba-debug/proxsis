"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { useRole } from "@/components/shell/RoleSwitcher";
import { WEEK_KEY } from "./CompanyCard";

/**
 * Back to the consultant's own week. Coming from that list, it goes back in history: the list reopens at the same
 * scroll position and the dossier head flies back into its card. Otherwise it opens the list.
 */
export function BackLink({ lang, label }: { lang: string; label: string }) {
  const router = useRouter();
  const consultant = useRole().consultant;
  const href = `/${lang}/semaine/${consultant}/`;
  function back(e: React.MouseEvent) {
    try {
      if (window.sessionStorage.getItem(WEEK_KEY) === href && window.history.length > 1) {
        e.preventDefault();
        router.back();
      }
    } catch {
      // storage blocked: follow the link
    }
  }
  return (
    <Link href={href} onClick={back} className="fx-quiet -ml-1">
      <ArrowLeft aria-hidden className="size-4" strokeWidth={1.5} /> {label}
    </Link>
  );
}
