from __future__ import annotations

from pathlib import Path

from resource_store import get_filesystem_provider


ROOT = Path(__file__).resolve().parents[1]


def test_active_atomspace_datatype_replaces_information_silo() -> None:
    directory = ROOT / "workbench" / "workspaces" / "shared" / "design" / "semantic_datatypes"
    resources = get_filesystem_provider()
    atomspace = resources.read_json(directory / "atomspace.semantic_datatype.json")
    information = resources.read_json(directory / "information.semantic_datatype.json")
    assert atomspace["id"] == "atomspace"
    assert atomspace["parents"] == ["information"]
    assert "atomspace" in information["children"]
    assert not (directory / "information_silo.semantic_datatype.json").exists()


def test_atomspace_guide_uses_direct_atomese_rule_syntax() -> None:
    guide = (ROOT / "docs" / "DATATYPES_MANIFEST_EXPLAINED.md").read_text(encoding="utf-8")
    assert "# Symbolic Datatypes in AtomSpace Explained" in guide
    for required in ("AtomSpace", "antecedent Atoms in one or more AtomSpaces", "retrieves Rule Atoms", "destination AtomSpaces", "(birthdate person:douglas", "(=>", "event occurs when an AtomSpace changes"):
        assert required in guide
    for classic_wrapper in ("ConceptNode", "EvaluationLink", "BindLink", "ExecutionOutputLink"):
        assert classic_wrapper not in guide
