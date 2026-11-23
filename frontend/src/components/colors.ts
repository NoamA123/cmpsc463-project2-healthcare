const PALETTE = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f", "#edc948", "#b07aa1", "#ff9da7"];

export function colorFor(key: string, keys: string[]): string {
  const i = keys.indexOf(key);
  return PALETTE[(i < 0 ? 0 : i) % PALETTE.length];
}
