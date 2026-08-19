type Token = { value: string; quoted: boolean; quoteStyle?: "single" | "double" };

const SAFE_ATOM = /^[^\s(){}";\\]+$/;
const TYPED_ATOM = /^(?:true|false|null|-?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?)$/i;
const EMBEDDED_JSON_STRING_PARTS = "__metta_json_string_parts__";

function quote(value: string, force = false): string {
  if (force) return JSON.stringify(value);
  return SAFE_ATOM.test(value) && value !== "{}" && !TYPED_ATOM.test(value) ? value : JSON.stringify(value);
}

function singleQuote(value: string): string {
  return `'${value
    .replace(/\\/g, "\\\\")
    .replace(/'/g, "\\'")
    .replace(/\n/g, "\\n")
    .replace(/\r/g, "\\r")
    .replace(/\t/g, "\\t")}'`;
}

function embeddedJsonParts(value: string): unknown[] | undefined {
  const parts: unknown[] = [];
  let cursor = 0;
  let scan = 0;
  let found = false;
  while (scan < value.length) {
    if (value[scan] !== "{" && value[scan] !== "[") { scan += 1; continue; }
    const start = scan;
    const stack: string[] = [];
    let quoted = false;
    let escaped = false;
    let end = -1;
    for (; scan < value.length; scan += 1) {
      const character = value[scan];
      if (quoted) {
        if (escaped) escaped = false;
        else if (character === "\\") escaped = true;
        else if (character === '"') quoted = false;
        continue;
      }

      if (character === '"') { quoted = true; continue; }
      if (character === "{" || character === "[") stack.push(character);
      else if (character === "}" || character === "]") {
        const opener = stack.pop();
        if ((opener === "{" && character !== "}") || (opener === "[" && character !== "]")) break;
        if (!stack.length) { end = scan + 1; break; }
      }

    }
    if (end < 0) { scan = start + 1; continue; }
    try {
      const parsed: unknown = JSON.parse(value.slice(start, end));
      if (parsed === null || typeof parsed !== "object") { scan = start + 1; continue; }
      if (start > cursor) parts.push(value.slice(cursor, start));
      parts.push(parsed);
      found = true;
      cursor = end;
      scan = end;
    } catch {
      scan = start + 1;
    }
  }
  if (!found) return undefined;
  if (cursor < value.length) parts.push(value.slice(cursor));
  return parts;
}

function compactEmbeddedJsonString(value: string): string {
  const parts = embeddedJsonParts(value);
  if (parts === undefined) return value;
  return parts.map((part) => typeof part === "string" ? part : JSON.stringify(part)).join("");
}

function formattedEmbeddedStringListItem(value: string): string[] | undefined {
  const parts = embeddedJsonParts(value);
  if (parts === undefined || !parts.some((part) => typeof part !== "string")) return undefined;
  const lines: string[] = [""];
  parts.forEach((part) => {
    if (typeof part === "string") {
      lines[lines.length - 1] += part;
      return;
    }
    const prettyLines = JSON.stringify(part, null, 2).split("\n");
    lines[lines.length - 1] += prettyLines[0];
    prettyLines.slice(1).forEach((line) => lines.push(line));
  });
  return [JSON.stringify(lines[0]), ...lines.slice(1).map((line) => singleQuote(line))];
}

function splitLongSentenceLines(value: string, minimumPrefix = 50): string[] | undefined {
  if (value.length <= minimumPrefix || /\r|\n/.test(value)) return undefined;
  const lines: string[] = [];
  let remaining = value;
  while (remaining.length > minimumPrefix) {
    const sentenceBoundary = /[A-Za-z][.!?]\s+/g;
    let splitAt = -1;
    let match: RegExpExecArray | null;
    while ((match = sentenceBoundary.exec(remaining)) !== null) {
      const boundary = match.index + match[0].length;
      if (boundary >= minimumPrefix) { splitAt = boundary; break; }
    }
    if (splitAt < 0) break;
    lines.push(remaining.slice(0, splitAt));
    remaining = remaining.slice(splitAt);
  }
  if (!lines.length) return undefined;
  lines.push(remaining);
  return lines;
}

function formattedLongSentenceListItem(value: string): string[] | undefined {
  const lines = splitLongSentenceLines(value);
  if (!lines || lines.length <= 1) return undefined;
  return [JSON.stringify(lines[0]), ...lines.slice(1).map((line) => singleQuote(line))];
}

export function jsonValueToMetta(value: unknown, depth = 0, forceQuoteString = false): string {
  const indent = "  ".repeat(depth);
  const childIndent = "  ".repeat(depth + 1);
  if (value === null) return "null";
  if (typeof value === "boolean" || typeof value === "number") return String(value);
  if (typeof value === "string") {
    if (forceQuoteString) return quote(value, true);
    const embedded = embeddedJsonParts(value);
    return embedded === undefined ? quote(value) : jsonValueToMetta({ [EMBEDDED_JSON_STRING_PARTS]: embedded }, depth, false);
  }
  if (Array.isArray(value)) {
    if (!value.length) return "([])";
    if (value.every((item) => typeof item === "number")) {
      return `([] ${value.map((item) => String(item)).join(" ")})`;
    }
    const quoteStringItems = value.some((item) => typeof item === "string" && /\s/.test(item));
    const items = value.flatMap((item) => {
      if (quoteStringItems && typeof item === "string") {
        const formatted = formattedEmbeddedStringListItem(item);
        if (formatted) return formatted.map((line) => `${childIndent}${line}`);
        const wrapped = formattedLongSentenceListItem(item);
        if (wrapped) return wrapped.map((line) => `${childIndent}${line}`);
      }
      return [`${childIndent}${jsonValueToMetta(item, depth + 1, quoteStringItems && typeof item === "string")}`];
    });
    return `([]\n${items.join("\n")}\n${indent})`;
  }
  if (typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>);
    if (!entries.length) return "()";
    const items = entries.map(([key, item]) => `${childIndent}(${quote(key)} ${jsonValueToMetta(item, depth + 1, false)})`);
    return `(\n${items.join("\n")}\n${indent})`;
  }
  throw new Error(`Unsupported resource value: ${typeof value}`);
}

export function jsonDocumentToMetta(source: string): string {
  return jsonValueToMetta(JSON.parse(source));
}

function tokenize(source: string): Token[] {
  const tokens: Token[] = [];
  const decodeSingleQuoted = (text: string, start: number): { value: string; next: number } => {
    let index = start + 1;
    let value = "";
    while (index < text.length) {
      const character = text[index];
      if (character === "\\") {
        if (index + 1 >= text.length) throw new Error("Invalid single-quoted string");
        const escaped = text[index + 1];
        value += escaped === "n" ? "\n"
          : escaped === "r" ? "\r"
            : escaped === "t" ? "\t"
              : escaped;
        index += 2;
        continue;
      }
      if (character === "'") return { value, next: index + 1 };
      value += character;
      index += 1;
    }
    throw new Error("Invalid single-quoted string");
  };
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
      try { tokens.push({ value: JSON.parse(raw), quoted: true, quoteStyle: "double" }); }
      catch { throw new Error("Invalid quoted string"); }
      continue;
    }
    if (character === "'") {
      const decoded = decodeSingleQuoted(source, index);
      tokens.push({ value: decoded.value, quoted: true, quoteStyle: "single" });
      index = decoded.next;
      continue;
    }
    const start = index;
    while (index < source.length && !/[\s()]/.test(source[index])) index += 1;
    tokens.push({ value: source.slice(start, index), quoted: false });
  }
  return tokens;
}

function atom(token: Token): unknown {
  if (token.quoted) return compactEmbeddedJsonString(token.value);
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
    const list = tokens[index]?.value === "[]";
    if (list) index += 1;
    if (!list) {
      const result: Record<string, unknown> = {};
      while (tokens[index]?.value !== ")") {
        if (tokens[index++]?.value !== "(") throw new Error("Map entries must be (name value) pairs");
        const key = tokens[index++];
        if (!key || key.value === "(" || key.value === ")") throw new Error("Map entry name must be an atom");
        const name = atom(key);
        if (typeof name !== "string") throw new Error("Map entry name must be a string");
        result[name] = parse();
        if (tokens[index++]?.value !== ")") throw new Error("Map entries must contain exactly one value");
      }
      index += 1;
      if (Object.keys(result).length === 1 && Array.isArray(result[EMBEDDED_JSON_STRING_PARTS])) {
        return (result[EMBEDDED_JSON_STRING_PARTS] as unknown[])
          .map(part => typeof part === "string" ? part : JSON.stringify(part))
          .join("");
      }
      return result;
    }
    const values: unknown[] = [];
    let canAppendSingleQuoted = false;
    while (tokens[index]?.value !== ")") {
      if (index >= tokens.length) throw new Error("Unclosed list");
      const next = tokens[index];
      if (next?.quoted && next.quoteStyle === "double") {
        index += 1;
        values.push(next.value);
        canAppendSingleQuoted = true;
        continue;
      }
      if (next?.quoted && next.quoteStyle === "single") {
        index += 1;
        const trimmed = next.value.replace(/^\s+/, "");
        if (canAppendSingleQuoted && typeof values[values.length - 1] === "string") {
          values[values.length - 1] = `${values[values.length - 1]}\n${trimmed}`;
        } else {
          values.push(trimmed);
        }
        canAppendSingleQuoted = true;
        continue;
      }
      values.push(parse());
      canAppendSingleQuoted = false;
    }
    index += 1;
    return values.map((item) => typeof item === "string" ? compactEmbeddedJsonString(item) : item);
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
