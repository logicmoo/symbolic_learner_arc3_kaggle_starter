from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


SAFE_ATOM = re.compile(r'^[^\s(){}";\\]+$')
TYPED_ATOM = re.compile(r'^(?:true|false|null|-?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?)$', re.IGNORECASE)
NUMBER = re.compile(r'^-?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?$', re.IGNORECASE)


def _quote(value: str) -> str:
    if SAFE_ATOM.fullmatch(value) and value != "{}" and not TYPED_ATOM.fullmatch(value):
        return value
    return json.dumps(value, ensure_ascii=False)


def json_value_to_metta(value: Any, depth: int = 0) -> str:
    indent = "  " * depth
    child_indent = "  " * (depth + 1)
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return json.dumps(value, ensure_ascii=False, allow_nan=False)
    if isinstance(value, str):
        return _quote(value)
    if isinstance(value, list):
        if not value:
            return "()"
        items = [f"{child_indent}{json_value_to_metta(item, depth + 1)}" for item in value]
        return f"(\n{'\n'.join(items)}\n{indent})"
    if isinstance(value, dict):
        if not value:
            return "({})"
        items = [f"{child_indent}({_quote(str(key))} {json_value_to_metta(item, depth + 1)})" for key, item in value.items()]
        return f"({{}}\n{'\n'.join(items)}\n{indent})"
    raise TypeError(f"unsupported resource value: {type(value).__name__}")


def json_document_to_metta(document: Any) -> str:
    if not isinstance(document, dict):
        raise ValueError("a resource document must be a map")
    return json_value_to_metta(document) + "\n"


@dataclass(frozen=True)
class Token:
    value: str
    quoted: bool = False


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
            tokens.append(Token(value, True))
            index += consumed
            continue
        start = index
        while index < len(source) and not source[index].isspace() and source[index] not in "()":
            index += 1
        tokens.append(Token(source[start:index]))
    return tokens


def _atom(token: Token) -> Any:
    if token.quoted:
        return token.value
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


def metta_to_json_value(source: str) -> Any:
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
        is_map = index < len(tokens) and tokens[index].value == "{}"
        if is_map:
            index += 1
        values: list[Any] = []
        while index >= len(tokens) or tokens[index].value != ")":
            if index >= len(tokens):
                raise ValueError("unclosed list")
            values.append(parse())
        index += 1
        if not is_map:
            return values
        result: dict[str, Any] = {}
        for entry in values:
            if not isinstance(entry, list) or len(entry) != 2 or not isinstance(entry[0], str):
                raise ValueError("map entries must be (name value) pairs")
            result[entry[0]] = entry[1]
        return result

    result = parse()
    if index != len(tokens):
        raise ValueError("unexpected tokens after resource")
    return result


def metta_document_to_json(source: str) -> Any:
    result = metta_to_json_value(source)
    if not isinstance(result, dict):
        raise ValueError("a resource document must be a map")
    return result
