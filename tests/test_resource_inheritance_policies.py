from __future__ import annotations

import pytest

from resource_relationships import (
    implements_resource,
    resolve_inherited_document,
    specializes_resource,
)


def linked(parent: dict, child: dict) -> dict[str, dict]:
    parent["specializations"] = specializes_resource(child["id"])
    child["implements"] = implements_resource(parent["id"])
    return {parent["id"]: parent, child["id"]: child}


def test_child_borrows_lent_fields_but_not_parent_identity() -> None:
    parent = {"kind": "operation", "id": "job", "label": "Parent label", "description": "Parent contract", "inputs": {"value": "Text"}}
    child = {"kind": "operation", "id": "job.python", "label": "Python job", "implementation": "python.callable"}
    result = resolve_inherited_document(child, linked(parent, child))

    assert result["document"]["id"] == "job.python"
    assert result["document"]["label"] == "Python job"
    assert result["document"]["inputs"] == {"value": "Text"}
    assert "description" not in result["document"]
    assert "job:description" in result["withheld"]
    assert "job:id" in result["withheld"]


def test_borrow_and_lend_policies_both_limit_inheritance() -> None:
    parent = {"kind": "operation", "id": "job", "description": "Contract", "inputs": {"text": "Text"}, "outputs": {"text": "Text"}}
    child = {"kind": "operation", "id": "job.python"}
    documents = linked(parent, child)
    child["implements"]["job"] = {"borrow": ["description", "inputs"], "exclude": ["inputs"]}
    parent["specializations"]["job.python"] = {"lend": ["description", "inputs", "outputs"], "withhold": ["id"]}

    result = resolve_inherited_document(child, documents)

    assert result["document"]["description"] == "Contract"
    assert "inputs" not in result["document"]
    assert "outputs" not in result["document"]
    assert result["excluded"] == ["job:inputs.text"]


def test_conflicting_parents_require_a_local_override() -> None:
    left = {"kind": "operation", "id": "left", "timeout": 10}
    right = {"kind": "operation", "id": "right", "timeout": 20}
    child = {
        "kind": "operation",
        "id": "combined",
        "implements": {
            **implements_resource("left"),
            **implements_resource("right"),
        },
    }
    left["specializations"] = specializes_resource("combined")
    right["specializations"] = specializes_resource("combined")
    documents = {"left": left, "right": right, "combined": child}

    conflicted = resolve_inherited_document(child, documents)
    assert conflicted["conflicts"] == ["timeout: left <> right"]
    assert "timeout" not in conflicted["document"]

    child["timeout"] = 30
    resolved = resolve_inherited_document(child, documents)
    assert resolved["conflicts"] == []
    assert resolved["document"]["timeout"] == 30


def test_inheritance_cycles_are_rejected() -> None:
    first = {"kind": "operation", "id": "first", "implements": implements_resource("second")}
    second = {"kind": "operation", "id": "second", "implements": implements_resource("first")}
    first["specializations"] = specializes_resource("second")
    second["specializations"] = specializes_resource("first")

    with pytest.raises(ValueError, match="inheritance cycle"):
        resolve_inherited_document(first, {"first": first, "second": second})
