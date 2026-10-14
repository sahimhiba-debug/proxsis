// A statement with its strong word (Sora 600, orange from 24 px: identite.css), the sentence itself unchanged: what a
// screen reader reads and what the tests compare is the same text.
export function Fort({ text, strong }: { text: string; strong?: string }) {
  const i = strong ? text.indexOf(strong) : -1;
  if (!strong || i < 0) return <>{text}</>;
  return <>{text.slice(0, i)}<b>{strong}</b>{text.slice(i + strong.length)}</>;
}
