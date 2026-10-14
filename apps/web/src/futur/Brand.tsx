import Link from "next/link";
import { Logo } from "@/lib/Logo";

/**
 * The name, always with its signature and the mention of what it is (brief of Hiba, 07.10.2026): the Proxsis logo
 * (docs/identite/logo: the word drawn from Urbanist, the dot of the « i » an orange diagonal), the signature
 * « La prochaine entreprise à appeler. » and « Prototype · concept non officiel » near it. Nothing of Flexsis's own logo.
 */
export function Brand({ href, name, signature, prototype }: { href: string; name: string; signature: string; prototype: string }) {
  return (
    <div className="fx-brand">
      <Link href={href} className="fx-wordmark block" aria-label={`${name}. ${signature}`}>
        <span className="fx-brand-name" aria-hidden><Logo title={name} /></span>
        <span className="fx-brand-signature" aria-hidden>{signature}</span>
      </Link>
      <p className="fx-brand-proto">{prototype}</p>
    </div>
  );
}
