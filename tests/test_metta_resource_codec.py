from __future__ import annotations

from metta_resource_codec import json_document_to_metta, metta_document_to_json


def test_metta_codec_round_trips_nested_resource_values() -> None:
    document = {
        "kind": "operation",
        "categories": ["core/values", "sample/core"],
        "settings": {"enabled": True, "limit": 3, "nothing": None},
        "emptyList": [],
        "emptyMap": {},
        "typedString": "true",
        "spacedString": "hello world",
    }

    source = json_document_to_metta(document)

    assert source.startswith("({}\n")
    assert '(typedString "true")' in source
    assert metta_document_to_json(source) == document
