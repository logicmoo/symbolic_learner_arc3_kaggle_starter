export function relationshipIds(value: unknown): string[] {
  const values = Array.isArray(value) ? value : typeof value === "string" ? [value] : [];
  return [...new Set(values.map(String).filter(value => value.trim()))];
}
