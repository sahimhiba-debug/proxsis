"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { homeFor, readRole } from "@/components/shell/RoleSwitcher";

export function HomeRedirect({ lang }: { lang: string }) {
  const router = useRouter();
  useEffect(() => router.replace(homeFor(lang, readRole())), [router, lang]);
  return null;
}
