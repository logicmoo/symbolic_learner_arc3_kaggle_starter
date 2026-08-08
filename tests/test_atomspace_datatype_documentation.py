from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_active_atomspace_datatype_replaces_information_silo() -> None:
    directory = ROOT / "workbench" / "workspaces" / "shared" / "datatypes"
    atomspace = json.loads((directory / "atomspace.semantic_datatype.json").read_text(encoding="utf-8"))
    information = json.loads((directory / "information.semantic_datatype.json").read_text(encoding="utf-8"))
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
