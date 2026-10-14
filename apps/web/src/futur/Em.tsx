import { Fragment } from "react";

/** A few words in Georgia italic for emotion: words between stars (« … à *appeler cette semaine.* »). */
export function Em({ text }: { text: string }) {
  return (
    <>
      {text.split(/(\*[^*]+\*)/).map((part, i) =>
        part.length > 2 && part.startsWith("*") && part.endsWith("*")
          ? <em key={i} className="fx-em">{part.slice(1, -1)}</em>
          : <Fragment key={i}>{part}</Fragment>,
      )}
    </>
  );
}
