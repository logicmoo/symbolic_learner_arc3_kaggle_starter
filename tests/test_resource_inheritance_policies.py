from __future__ import annotations

import pytest

from resource_relationships import (
    depended_on_by_resource,
    depends_on_resource,
    implemented_by_resource,
    implements_resource,
    inherited_by_resource,
    inherits_from_resource,
    normalize_resource_relationships,
    resolve_dependency_enablement,
    resolve_inherited_document,
)


def linked(parent: dict, child: dict) -> dict[str, dict]:
    parent["implementedBy"] = implemented_by_resource(child["id"])
    parent["inheritedBy"] = inherited_by_resource(child["id"])
    child["implements"] = implements_resource(parent["id"])
    child["inheritsFrom"] = inherits_from_resource(parent["id"])
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
    child["inheritsFrom"]["job"] = {"borrow": ["description", "inputs"], "exclude": ["inputs"]}
    parent["inheritedBy"]["job.python"] = {"lend": ["description", "inputs", "outputs"], "withhold": ["id"]}

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
        "inheritsFrom": {
            **inherits_from_resource("left"),
            **inherits_from_resource("right"),
        },
    }
    left["implementedBy"] = implemented_by_resource("combined")
    right["implementedBy"] = implemented_by_resource("combined")
    left["inheritedBy"] = inherited_by_resource("combined")
    right["inheritedBy"] = inherited_by_resource("combined")
    documents = {"left": left, "right": right, "combined": child}

    conflicted = resolve_inherited_document(child, documents)
    assert conflicted["conflicts"] == ["timeout: left <> right"]
    assert "timeout" not in conflicted["document"]

    child["timeout"] = 30
    resolved = resolve_inherited_document(child, documents)
    assert resolved["conflicts"] == []
    assert resolved["document"]["timeout"] == 30


def test_inheritance_cycles_are_rejected() -> None:
    first = {"kind": "operation", "id": "first", "inheritsFrom": inherits_from_resource("second")}
    second = {"kind": "operation", "id": "second", "inheritsFrom": inherits_from_resource("first")}
    first["inheritedBy"] = inherited_by_resource("second")
    second["inheritedBy"] = inherited_by_resource("first")

    with pytest.raises(ValueError, match="inheritance cycle"):
        resolve_inherited_document(first, {"first": first, "second": second})


def test_enablement_uses_dependencies_not_inheritance_parents() -> None:
    inheritance_parent = {
        "kind": "backend",
        "id": "inheritance-parent",
        "enabled": False,
        "implementedBy": implemented_by_resource("child"),
        "inheritedBy": inherited_by_resource("child"),
    }
    dependency = {
        "kind": "system",
        "id": "dependency",
        "enabled": True,
        "dependedOnBy": depended_on_by_resource("child"),
    }
    child = {
        "kind": "model",
        "id": "child",
        "implements": implements_resource("inheritance-parent"),
        "inheritsFrom": inherits_from_resource("inheritance-parent"),
        "dependsOn": depends_on_resource("dependency"),
    }
    documents = {
        inheritance_parent["id"]: inheritance_parent,
        dependency["id"]: dependency,
        child["id"]: child,
    }

    inherited = resolve_inherited_document(child, documents)
    assert "enabled" not in inherited["document"]
    assert resolve_dependency_enablement(child, documents)["enabled"] is True

    dependency["enabled"] = False
    resolved = resolve_dependency_enablement(child, documents)
    assert resolved["enabled"] is False
    assert resolved["blockingDependencies"] == ["dependency"]


def test_dependency_backlink_and_cycle_are_required() -> None:
    first = {
        "kind": "system",
        "id": "first",
        "dependsOn": depends_on_resource("second"),
        "dependedOnBy": depended_on_by_resource("second"),
    }
    second = {
        "kind": "system",
        "id": "second",
        "dependsOn": depends_on_resource("first"),
        "dependedOnBy": depended_on_by_resource("first"),
    }

    with pytest.raises(ValueError, match="dependency cycle"):
        resolve_dependency_enablement(first, {"first": first, "second": second})

    second["dependsOn"] = {}
    second["dependedOnBy"] = {}
    resolved = resolve_dependency_enablement(first, {"first": first, "second": second})
    assert resolved["enabled"] is False
    assert resolved["missingBacklinks"] == ["second.dependedOnBy[first]"]


def test_legacy_relationships_normalize_to_canonical_graphs() -> None:
    legacy = {
        "kind": "operation",
        "id": "parent",
        "specializations": {
            "child": {
                "lend": ["*"],
                "withhold": ["id"],
            }
        },
        "preferredSpecialization": "child",
    }
    normalized = normalize_resource_relationships(legacy)
    assert normalized["implementedBy"] == {"child": {}}
    assert normalized["inheritedBy"]["child"]["lend"] == ["*"]
    assert normalized["preferredImplementation"] == "child"
    assert "specializations" not in normalized
    assert "preferredSpecialization" not in normalized

    child = normalize_resource_relationships({
        "kind": "operation",
        "id": "child",
        "implements": {
            "parent": {
                "borrow": ["*"],
                "exclude": [],
            }
        },
    })
    assert child["implements"] == {"parent": {}}
    assert child["inheritsFrom"]["parent"]["borrow"] == ["*"]


def test_preferred_implementation_must_belong_to_implemented_by() -> None:
    with pytest.raises(ValueError, match="must belong to implementedBy"):
        normalize_resource_relationships({
            "kind": "operation",
            "id": "parent",
            "implementedBy": implemented_by_resource("first"),
            "preferredImplementation": "other",
        })


def test_implements_alone_does_not_inherit_properties() -> None:
    parent = {
        "kind": "operation",
        "id": "parent",
        "description": "must not be inherited",
        "implementedBy": implemented_by_resource("child"),
    }
    child = {
        "kind": "operation",
        "id": "child",
        "implements": implements_resource("parent"),
    }
    resolved = resolve_inherited_document(
        child, {"parent": parent, "child": child}
    )
    assert "description" not in resolved["document"]
    assert resolved["borrowed"] == []
