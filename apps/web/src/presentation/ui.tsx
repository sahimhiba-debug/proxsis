"use client";

// Building blocks of the editorial direction, in the shadcn/ui manner (base-ui primitive + cva variants, styled by
// direction.css). One copper action per scene; options are thin-ruled rows; navigation is text.
import { Button as ButtonPrimitive } from "@base-ui/react/button";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "cn";
import { Fragment } from "react";

const pbutton = cva("", {
  variants: {
    variant: {
      action: "d-action", // the scene's single action (copper)
      option: "d-option", // a choice of the director (thin rule, copper when chosen)
      nav: "d-navbtn", // Retour / Continuer
      quiet: "d-quiet", // secondary text action
      tool: "d-tool", // header tools (language, contents)
      paper: "d-paper-link", // link on a document
    },
  },
  defaultVariants: { variant: "action" },
});

export function PButton({ className, variant, ...props }: ButtonPrimitive.Props & VariantProps<typeof pbutton>) {
  return <ButtonPrimitive data-slot="pbutton" className={cn(pbutton({ variant }), className)} {...props} />;
}

/** « La piste est là. *Vous décidez.* » — words between stars are set in serif italic (a few words, never a whole line). */
export function Em({ text }: { text: string }) {
  return (
    <>
      {text.split(/(\*[^*]+\*)/).map((part, i) =>
        part.length > 2 && part.startsWith("*") && part.endsWith("*") ? (
          <em key={i} className="d-em">{part.slice(1, -1)}</em>
        ) : (
          <Fragment key={i}>{part}</Fragment>
        ),
      )}
    </>
  );
}

