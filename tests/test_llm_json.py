from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from llm_json import LlmJsonError, parse_or_repair_json_object
from llm_json_patch import _required_keys, _resilient_create_response


def _artifact_input(*keys: str):
    return [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": (
                        "RETURN ONLY THESE ARTIFACT KEYS: "
                        + ", ".join(keys)
                        + ". Omit unrequested artifact keys."
                    ),
                }
            ],
        }
    ]


def test_repairs_missing_comma_and_literal_newline() -> None:
    malformed = (
        '{"new_identities":[] '
        '"objects_pl":"cell(a).\ncell(b).",'
        '"rules_pl":"rule(a)."}'
    )

    result, repaired = parse_or_repair_json_object(
        malformed,
        required_keys=("new_identities", "objects_pl", "rules_pl"),
    )

    assert repaired is True
    assert result["objects_pl"] == "cell(a).\ncell(b)."
    assert result["rules_pl"] == "rule(a)."


def test_required_key_validation_rejects_incomplete_bundle() -> None:
    with pytest.raises(LlmJsonError, match="missing required keys"):
        parse_or_repair_json_object(
            '{"new_identities":[]}',
            required_keys=("new_identities", "objects_pl"),
        )


def test_extracts_requested_artifact_keys() -> None:
    assert _required_keys(
        _artifact_input("new_identities", "objects_pl", "rules_pl")
    ) == ("new_identities", "objects_pl", "rules_pl")


def test_text_only_retry_recovers_incomplete_response(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ARC3_LLM_RESPONSE_DIR", str(tmp_path))
    monkeypatch.setenv("ARC3_LLM_SAVE_RAW_RESPONSE", "1")
    monkeypatch.setenv("ARC3_LLM_JSON_RETRY", "1")

    outputs = iter(
        [
            '{"new_identities":[]}',
            '{"new_identities":[],"objects_pl":"object(a)."}',
        ]
    )
    calls: list[dict[str, object]] = []

    def original(_router, **kwargs):
        calls.append(kwargs)
        return SimpleNamespace(output_text=next(outputs))

    response = _resilient_create_response(
        original,
        object(),
        model="provider-selected",
        input=_artifact_input("new_identities", "objects_pl"),
        reasoning={"effort": "high"},
        max_output_tokens=32000,
    )

    assert len(calls) == 2
    assert calls[1]["reasoning"] == {"effort": "low"}
    assert json.loads(response.output_text)["objects_pl"] == "object(a)."
    assert (tmp_path / "llm_response.raw.txt").exists()
    assert (tmp_path / "llm_response.retry.raw.txt").exists()
    assert (tmp_path / "llm_response.repaired.json").exists()
