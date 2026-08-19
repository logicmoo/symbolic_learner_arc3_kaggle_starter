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


def test_json_strings_containing_complete_objects_or_arrays_are_recursively_converted() -> None:
    document = {
        "kind": "operation",
        "embeddedObject": '{"enabled":true,"steps":[{"id":"one"}]}',
        "embeddedArray": '["alpha", {"nested":"{\\"limit\\":3}"}]',
        "promptText": (
            'Preserve this workflow-stage contract exactly: '
            '{"id":"normalize","inputs":{"images":"source_images"},'
            '"outputs":{"images":"normalized_images"}}.'
        ),
        "ordinaryText": 'Keep this prose with {"example":true} embedded inside it.',
        "typedString": "true",
    }

    source = json_document_to_metta(document)
    decoded = metta_document_to_json(source)

    assert decoded == {
        **document,
        "embeddedArray": '["alpha",{"nested":"{\\"limit\\":3}"}]',
    }
    assert decoded["typedString"] == "true"
    assert source.count("__metta_json_string_parts__") >= 4
    assert "(id normalize)" in source
    assert "(images source_images)" in source


def test_lists_with_spaced_strings_quote_all_string_items() -> None:
    document = {
        "kind": "operation",
        "tags": ["alpha", "two words", "gamma/delta"],
        "mixed": ["one", 2, "three words"],
    }

    source = json_document_to_metta(document)
    decoded = metta_document_to_json(source)

    assert decoded == document
    assert '    "alpha"' in source
    assert '    "two words"' in source
    assert '    "gamma/delta"' in source
    assert '    "one"' in source
    assert "    2" in source
    assert '    "three words"' in source


def test_numeric_lists_export_in_compact_single_line_form() -> None:
    document = {
        "kind": "operation",
        "indices": [1, 2, 3, 10],
        "weights": [0.25, 0.5, 1.0],
    }

    source = json_document_to_metta(document)
    decoded = metta_document_to_json(source)

    assert decoded == document
    assert "(indices ([] 1 2 3 10))" in source
    assert "(weights ([] 0.25 0.5 1.0))" in source
