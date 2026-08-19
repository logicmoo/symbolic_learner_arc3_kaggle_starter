from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


SAFE_ATOM = re.compile(r'^[^\s(){}";\\]+$')
TYPED_ATOM = re.compile(r'^(?:true|false|null|-?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?)$', re.IGNORECASE)
NUMBER = re.compile(r'^-?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?$', re.IGNORECASE)
EMBEDDED_JSON_STRING_PARTS = "__metta_json_string_parts__"


def _quote(value: str, force: bool = False) -> str:
    if force:
        return json.dumps(value, ensure_ascii=False)
    if SAFE_ATOM.fullmatch(value) and value != "{}" and not TYPED_ATOM.fullmatch(value):
        return value
    return json.dumps(value, ensure_ascii=False)


def _single_quote(value: str) -> str:
    escaped = (
        value
        .replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )
    return f"'{escaped}'"


def _embedded_json_parts(value: str) -> list[Any] | None:
    decoder = json.JSONDecoder()
    parts: list[Any] = []
    cursor = 0
    scan = 0
    found = False
    while scan < len(value):
        if value[scan] not in "[{":
            scan += 1
            continue
        try:
            parsed, consumed = decoder.raw_decode(value[scan:])
        except json.JSONDecodeError:
            scan += 1
            continue
        if not isinstance(parsed, (dict, list)):
            scan += 1
            continue
        if scan > cursor:
            parts.append(value[cursor:scan])
        parts.append(parsed)
        found = True
        cursor = scan + consumed
        scan = cursor
    if not found:
        return None
    if cursor < len(value):
        parts.append(value[cursor:])
    return parts


def _compact_embedded_json_string(value: str) -> str:
    parts = _embedded_json_parts(value)
    if parts is None:
        return value
    return "".join(
        part if isinstance(part, str) else json.dumps(part, ensure_ascii=False, separators=(",", ":"))
        for part in parts
    )


def _formatted_embedded_string_list_item(value: str) -> list[str] | None:
    parts = _embedded_json_parts(value)
    if not parts or not any(not isinstance(part, str) for part in parts):
        return None
    lines: list[str] = [""]
    for part in parts:
        if isinstance(part, str):
            lines[-1] += part
            continue
        pretty_lines = json.dumps(part, ensure_ascii=False, indent=2).splitlines()
        lines[-1] += pretty_lines[0]
        lines.extend(pretty_lines[1:])
    return [json.dumps(lines[0], ensure_ascii=False), *(_single_quote(line) for line in lines[1:])]


def _split_long_sentence_lines(value: str, minimum_prefix: int = 50) -> list[str] | None:
    if len(value) <= minimum_prefix or "\n" in value or "\r" in value:
        return None
    lines: list[str] = []
    remaining = value
    while len(remaining) > minimum_prefix:
        split_at = -1
        for match in re.finditer(r"[A-Za-z][.!?]\s+", remaining):
            boundary = match.end()
            if boundary >= minimum_prefix:
                split_at = boundary
                break
        if split_at < 0:
            break
        lines.append(remaining[:split_at])
        remaining = remaining[split_at:]
    if not lines:
        return None
    lines.append(remaining)
    return lines


def _formatted_long_sentence_list_item(value: str) -> list[str] | None:
    lines = _split_long_sentence_lines(value)
    if not lines or len(lines) <= 1:
        return None
    return [json.dumps(lines[0], ensure_ascii=False), *(_single_quote(line) for line in lines[1:])]


def _restore_embedded_json_string(value: dict[str, Any]) -> Any:
    if set(value) != {EMBEDDED_JSON_STRING_PARTS}:
        return value
    parts = value[EMBEDDED_JSON_STRING_PARTS]
    if not isinstance(parts, list):
        return value
    return "".join(
        part if isinstance(part, str) else json.dumps(part, ensure_ascii=False, separators=(",", ":"))
        for part in parts
    )


def json_value_to_metta(value: Any, depth: int = 0, force_quote_string: bool = False) -> str:
    indent = "  " * depth
    child_indent = "  " * (depth + 1)
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return json.dumps(value, ensure_ascii=False, allow_nan=False)
    if isinstance(value, str):
        if force_quote_string:
            return _quote(value, force=True)
        embedded = _embedded_json_parts(value)
        if embedded is not None:
            return json_value_to_metta({EMBEDDED_JSON_STRING_PARTS: embedded}, depth, force_quote_string=False)
        return _quote(value)
    if isinstance(value, list):
        if not value:
            return "([])"
        if all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in value):
            compact = " ".join(json.dumps(item, ensure_ascii=False, allow_nan=False) for item in value)
            return f"([] {compact})"
        quote_string_items = any(
            isinstance(item, str) and any(character.isspace() for character in item)
            for item in value
        )
        items: list[str] = []
        for item in value:
            if quote_string_items and isinstance(item, str):
                formatted = _formatted_embedded_string_list_item(item)
                if formatted:
                    items.extend(f"{child_indent}{line}" for line in formatted)
                    continue
                wrapped = _formatted_long_sentence_list_item(item)
                if wrapped:
                    items.extend(f"{child_indent}{line}" for line in wrapped)
                    continue
            items.append(
                f"{child_indent}{json_value_to_metta(item, depth + 1, force_quote_string=quote_string_items and isinstance(item, str))}"
            )
        return f"([]\n{'\n'.join(items)}\n{indent})"
    if isinstance(value, dict):
        if not value:
            return "()"
        items = [f"{child_indent}({_quote(str(key))} {json_value_to_metta(item, depth + 1, force_quote_string=False)})" for key, item in value.items()]
        return f"(\n{'\n'.join(items)}\n{indent})"
    raise TypeError(f"unsupported resource value: {type(value).__name__}")


def json_document_to_metta(document: Any) -> str:
    if not isinstance(document, dict):
        raise ValueError("a resource document must be a map")
    return json_value_to_metta(document) + "\n"


@dataclass(frozen=True)
class Token:
    value: str
    quoted: bool = False
    quote_style: str | None = None


def _tokenize(source: str) -> list[Token]:
    tokens: list[Token] = []
    index = 0
    while index < len(source):
        character = source[index]
        if character.isspace():
            index += 1
            continue
        if character == ";":
            while index < len(source) and source[index] != "\n":
                index += 1
            continue
        if character in "()":
            tokens.append(Token(character))
            index += 1
            continue
        if character == '"':
            decoder = json.JSONDecoder()
            try:
                value, consumed = decoder.raw_decode(source[index:])
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid quoted string: {error.msg}") from error
            if not isinstance(value, str):
                raise ValueError("quoted atom must be a string")
            tokens.append(Token(value, True, "double"))
            index += consumed
            continue
        if character == "'":
            index += 1
            value_parts: list[str] = []
            while index < len(source):
                next_character = source[index]
                if next_character == "\\":
                    if index + 1 >= len(source):
                        raise ValueError("invalid single-quoted string")
                    escaped = source[index + 1]
                    value_parts.append("\n" if escaped == "n" else "\r" if escaped == "r" else "\t" if escaped == "t" else escaped)
                    index += 2
                    continue
                if next_character == "'":
                    tokens.append(Token("".join(value_parts), True, "single"))
                    index += 1
                    break
                value_parts.append(next_character)
                index += 1
            else:
                raise ValueError("invalid single-quoted string")
            continue
        start = index
        while index < len(source) and not source[index].isspace() and source[index] not in "()":
            index += 1
        tokens.append(Token(source[start:index]))
    return tokens


def _atom(token: Token) -> Any:
    if token.quoted:
        return _compact_embedded_json_string(token.value)
    if token.value == "true":
        return True
    if token.value == "false":
        return False
    if token.value == "null":
        return None
    if NUMBER.fullmatch(token.value):
        number = float(token.value) if any(character in token.value.lower() for character in ".e") else int(token.value)
        return number
    return token.value


def metta_to_json_value(source: str, *, legacy: bool = False) -> Any:
    tokens = _tokenize(source)
    index = 0

    def parse() -> Any:
        nonlocal index
        if index >= len(tokens):
            raise ValueError("unexpected end of MeTTa resource")
        token = tokens[index]
        index += 1
        if token.value != "(":
            return _atom(token)
        marker = tokens[index].value if index < len(tokens) and tokens[index].value in {"{}", "[]"} else None
        if marker:
            index += 1
        if marker is None and not legacy:
            result: dict[str, Any] = {}
            while index < len(tokens) and tokens[index].value != ")":
                if tokens[index].value != "(":
                    raise ValueError("map entries must be (name value) pairs")
                index += 1
                if index >= len(tokens) or tokens[index].value in {"(", ")"}:
                    raise ValueError("map entry name must be an atom")
                key = _atom(tokens[index])
                index += 1
                if not isinstance(key, str):
                    raise ValueError("map entry name must be a string")
                result[key] = parse()
                if index >= len(tokens) or tokens[index].value != ")":
                    raise ValueError("map entries must contain exactly one value")
                index += 1
            if index >= len(tokens):
                raise ValueError("unclosed map")
            index += 1
            return _restore_embedded_json_string(result)
        values: list[Any] = []
        can_append_single_quoted = False
        while index >= len(tokens) or tokens[index].value != ")":
            if index >= len(tokens):
                raise ValueError("unclosed list")
            next_token = tokens[index]
            if next_token.quoted and next_token.quote_style == "double":
                values.append(next_token.value)
                index += 1
                can_append_single_quoted = True
                continue
            if next_token.quoted and next_token.quote_style == "single":
                trimmed = next_token.value.lstrip()
                if can_append_single_quoted and values and isinstance(values[-1], str):
                    values[-1] = f"{values[-1]}\n{trimmed}"
                else:
                    values.append(trimmed)
                index += 1
                can_append_single_quoted = True
                continue
            values.append(parse())
            can_append_single_quoted = False
        index += 1
        normalized_values = [
            _compact_embedded_json_string(item) if isinstance(item, str) else item
            for item in values
        ]
        if marker == "[]" or (legacy and marker != "{}"):
            return normalized_values
        result: dict[str, Any] = {}
        for entry in normalized_values:
            if not isinstance(entry, list) or len(entry) != 2 or not isinstance(entry[0], str):
                raise ValueError("map entries must be (name value) pairs")
            result[entry[0]] = entry[1]
        return result

    result = parse()
    if index != len(tokens):
        raise ValueError("unexpected tokens after resource")
    return result


def metta_document_to_json(source: str, *, legacy: bool = False) -> Any:
    result = metta_to_json_value(source, legacy=legacy)
    if not isinstance(result, dict):
        raise ValueError("a resource document must be a map")
    return result


def split_metta_document_spans(source: str) -> list[tuple[int, int, str]]:
    documents: list[tuple[int, int, str]] = []
    start: int | None = None
    depth = 0
    quoted: str | None = None
    escaped = False
    comment = False
    for index, character in enumerate(source):
        if comment:
            if character == "\n":
                comment = False
            continue
        if quoted is not None:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quoted:
                quoted = None
            continue
        if character == ";":
            comment = True
        elif character in {"'", '"'}:
            quoted = character
        elif character == "(":
            if depth == 0:
                start = index
            depth += 1
        elif character == ")":
            depth -= 1
            if depth < 0:
                raise ValueError("unexpected closing parenthesis")
            if depth == 0 and start is not None:
                documents.append((start, index + 1, source[start:index + 1]))
                start = None
        elif depth == 0 and not character.isspace():
            raise ValueError("top-level resource must be a map")
    if quoted is not None or depth or start is not None:
        raise ValueError("unclosed top-level resource")
    return documents


def split_metta_documents(source: str) -> list[str]:
    return [document for _, _, document in split_metta_document_spans(source)]


def metta_documents_to_json(source: str) -> list[dict[str, Any]]:
    documents = [metta_document_to_json(item) for item in split_metta_documents(source)]
    if not documents:
        raise ValueError("resource file is empty")
    return documents
