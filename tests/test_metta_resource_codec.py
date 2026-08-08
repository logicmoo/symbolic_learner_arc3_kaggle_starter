from __future__ import annotations

from metta_resource_codec import json_document_to_metta, metta_document_to_json, metta_documents_to_json, split_metta_document_spans


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

    assert source.startswith("(\n")
    assert "(categories ([]" in source
    assert "(emptyList ([]))" in source
    assert "(emptyMap ())" in source
    assert '(typedString "true")' in source
    assert metta_document_to_json(source) == document


def test_metta_codec_reads_multiple_top_level_resources_with_source_spans() -> None:
    source = "; keep this header\n((kind goal) (id one))\n\n; sibling comment\n((kind goal_variant) (id two))\n"

    assert metta_documents_to_json(source) == [
        {"kind": "goal", "id": "one"},
        {"kind": "goal_variant", "id": "two"},
    ]
    spans = split_metta_document_spans(source)
    assert [item[2] for item in spans] == ["((kind goal) (id one))", "((kind goal_variant) (id two))"]
