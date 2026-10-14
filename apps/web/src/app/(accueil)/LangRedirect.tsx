"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

/** Opens the app in the browser language (German if preferred, French otherwise). */
export function LangRedirect() {
  const router = useRouter();
  useEffect(() => {
    const de = (navigator.languages || [navigator.language]).some((l) => l?.toLowerCase().startsWith("de"));
    router.replace(de ? "/de/" : "/fr/");
  }, [router]);
  return null;
}
