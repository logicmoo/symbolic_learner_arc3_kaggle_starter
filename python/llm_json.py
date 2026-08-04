from __future__ import annotations

import json
import re
from collections.abc import Iterable
from typing import Any

from json_repair import repair_json


class LlmJsonError(RuntimeError):
    """Raised when an LLM response cannot be recovered as the required object."""


def _candidate(text: str) -> str:
    value = text.strip()
    value = re.sub(r"^```(?:json)?\s*", "", value, flags=re.I)
    value = re.sub(r"\s*```$", "", value)
    start, end = value.find("{"), value.rfind("}")
    if 0 <= start < end:
        return value[start : end + 1]
    return value


def _validate_object(value: Any, required_keys: Iterable[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LlmJsonError("Combined LLM response must be one JSON object")
    missing = [key for key in required_keys if key not in value]
    if missing:
        raise LlmJsonError(
            "Combined LLM response is missing required keys: " + ", ".join(missing)
        )
    return value


def parse_or_repair_json_object(
    text: str,
    *,
    required_keys: Iterable[str] = (),
) -> tuple[dict[str, Any], bool]:
    """Parse strict JSON, then deterministically repair common LLM defects.

    Returns ``(object, repaired)``. The repair library handles missing commas,
    quotes, brackets, literal newlines, trailing commentary, and truncation.
    Required-key validation prevents a syntactically repaired but incomplete
    bundle from being accepted silently.
    """
    candidate = _candidate(text)
    if not candidate:
        raise LlmJsonError("Combined LLM response was empty")

    try:
        return _validate_object(json.loads(candidate), required_keys), False
    except (json.JSONDecodeError, LlmJsonError) as strict_error:
        try:
            repaired = repair_json(candidate, return_objects=True)
            return _validate_object(repaired, required_keys), True
        except Exception as repair_error:
            raise LlmJsonError(
                f"Combined LLM response was not recoverable as JSON: {strict_error}; "
                f"repair failed: {repair_error}"
            ) from repair_error


def strict_json_text(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
