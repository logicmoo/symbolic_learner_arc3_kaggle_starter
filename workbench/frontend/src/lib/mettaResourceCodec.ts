type Token = { value: string; quoted: boolean };

const SAFE_ATOM = /^[^\s(){}";\\]+$/;
const TYPED_ATOM = /^(?:true|false|null|-?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?)$/i;

function quote(value: string): string {
  return SAFE_ATOM.test(value) && value !== "{}" && !TYPED_ATOM.test(value) ? value : JSON.stringify(value);
}

export function jsonValueToMetta(value: unknown, depth = 0): string {
  const indent = "  ".repeat(depth);
  const childIndent = "  ".repeat(depth + 1);
  if (value === null) return "null";
  if (typeof value === "boolean" || typeof value === "number") return String(value);
  if (typeof value === "string") return quote(value);
  if (Array.isArray(value)) {
    if (!value.length) return "()";
    const items = value.map(item => `${childIndent}${jsonValueToMetta(item, depth + 1)}`);
    return `(\n${items.join("\n")}\n${indent})`;
  }
  if (typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>);
    if (!entries.length) return "({})";
    const items = entries.map(([key, item]) => `${childIndent}(${quote(key)} ${jsonValueToMetta(item, depth + 1)})`);
    return `({}\n${items.join("\n")}\n${indent})`;
  }
  throw new Error(`Unsupported resource value: ${typeof value}`);
}

export function jsonDocumentToMetta(source: string): string {
  return jsonValueToMetta(JSON.parse(source));
}

function tokenize(source: string): Token[] {
  const tokens: Token[] = [];
  let index = 0;
  while (index < source.length) {
    const character = source[index];
    if (/\s/.test(character)) { index += 1; continue; }
    if (character === ";") { while (index < source.length && source[index] !== "\n") index += 1; continue; }
    if (character === "(" || character === ")") { tokens.push({ value: character, quoted: false }); index += 1; continue; }
    if (character === '"') {
      let raw = '"'; index += 1;
      while (index < source.length) {
        const next = source[index++]; raw += next;
        if (next === "\\" && index < source.length) raw += source[index++];
        else if (next === '"') break;
      }
      try { tokens.push({ value: JSON.parse(raw), quoted: true }); }
      catch { throw new Error("Invalid quoted string"); }
      continue;
    }
    const start = index;
    while (index < source.length && !/[\s()]/.test(source[index])) index += 1;
    tokens.push({ value: source.slice(start, index), quoted: false });
  }
  return tokens;
}

function atom(token: Token): unknown {
  if (token.quoted) return token.value;
  if (token.value === "true") return true;
  if (token.value === "false") return false;
  if (token.value === "null") return null;
  if (/^-?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?$/i.test(token.value)) return Number(token.value);
  return token.value;
}

export function mettaToJsonValue(source: string): unknown {
  const tokens = tokenize(source);
  let index = 0;
  const parse = (): unknown => {
    const token = tokens[index++];
    if (!token) throw new Error("Unexpected end of MeTTa resource");
    if (token.value !== "(") return atom(token);
    const map = tokens[index]?.value === "{}";
    if (map) index += 1;
    const values: unknown[] = [];
    while (tokens[index]?.value !== ")") {
      if (index >= tokens.length) throw new Error("Unclosed list");
      values.push(parse());
    }
    index += 1;
    if (!map) return values;
    const result: Record<string, unknown> = {};
    for (const entry of values) {
      if (!Array.isArray(entry) || entry.length !== 2 || typeof entry[0] !== "string") throw new Error("Map entries must be (name value) pairs");
      result[entry[0]] = entry[1];
    }
    return result;
  };
  const result = parse();
  if (index !== tokens.length) throw new Error("Unexpected tokens after resource");
  return result;
}

export function mettaDocumentToJson(source: string): string {
  const value = mettaToJsonValue(source);
  if (!value || Array.isArray(value) || typeof value !== "object") throw new Error("A resource document must be a map");
  return JSON.stringify(value, null, 2);
}
