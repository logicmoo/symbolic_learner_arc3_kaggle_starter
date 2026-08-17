import json
from pathlib import Path

import pytest

from object_memory import (
    ArtifactRef,
    ActionTreeSemanticReplay,
    AtomSpaceSemanticBackend,
    CommittedAtom,
    EncounterRecord,
    MettaFileAtomSpaceTransport,
    Observation,
    SymbolicStore,
    TurtleProgramRef,
)


def test_atomspace_backend_round_trips_nested_records_and_hydrates(tmp_path: Path) -> None:
    path = tmp_path / "semantic_memory.metta"
    store = SymbolicStore(AtomSpaceSemanticBackend(path=path))
    artifact = ArtifactRef.create(
        artifact_type="turtle_program",
        uri="memory://object/red",
        content_hash="sha256:red",
    )
    observation = store.put_observation(
        Observation.create(
            source_modality="logical_grid",
            artifacts=(artifact,),
            action_tree_node="node/initial",
        )
    )
    first = store.put_encounter(
        EncounterRecord.create(
            observation_id=observation.observation_id,
            action_tree_node="node/initial",
            object_identity_id="red_ball",
            turtle_programs=(TurtleProgramRef(artifact, fit_score=1.0),),
        )
    )
    second = store.put_encounter(
        EncounterRecord.create(
            observation_id="next-observation",
            action_tree_node="node/right",
            object_identity_id="red_ball",
            previous_encounter_id=first.encounter_id,
        )
    )
    atom = store.put_atom(
        CommittedAtom(
            "red_ball",
            "object",
            {"description": 'red "ball"\nwith unicode π', "nested": {"cells": [1, 2]}},
            confidence=0.75,
            provenance=("fixture",),
        )
    )

    loaded = SymbolicStore(AtomSpaceSemanticBackend(path=path)).hydrate()

    assert loaded.get("observations", observation.observation_id) == observation
    assert loaded.encounters.records() == (first, second)
    assert loaded.artifacts.get(artifact.artifact_id) == artifact
    assert loaded.get("atoms", atom.handle) == atom
    assert loaded.snapshot() == store.snapshot()
    source = path.read_text(encoding="utf-8")
    assert source.startswith("; Durable Phase 2 semantic-record AtomSpace.")
    assert '(semantic_record "atoms" "red_ball" ' in source
    assert "π" in source


def test_atomspace_backend_rejects_identity_conflicts(tmp_path: Path) -> None:
    backend = AtomSpaceSemanticBackend(path=tmp_path / "memory.metta")
    backend.write_once("atoms", "same", CommittedAtom("same", "object", {"value": 1}))

    with pytest.raises(ValueError, match="Semantic identity conflict"):
        backend.write_once("atoms", "same", CommittedAtom("same", "object", {"value": 2}))


def test_atomspace_backend_supports_an_injected_remote_transport() -> None:
    expressions: list[str] = []

    class Transport:
        def query(self, head: str) -> tuple[str, ...]:
            assert head == "semantic_record"
            return tuple(expressions)

        def assert_expression(self, expression: str) -> None:
            expressions.append(expression)

    first = AtomSpaceSemanticBackend(Transport())
    expected = first.write_once(
        "atoms", "remote", CommittedAtom("remote", "object", {"source": "remote"})
    )
    reloaded = AtomSpaceSemanticBackend(Transport())

    assert reloaded.get("atoms", "remote") == expected


def test_metta_file_transport_deduplicates_exact_atoms(tmp_path: Path) -> None:
    path = tmp_path / "memory.metta"
    transport = MettaFileAtomSpaceTransport(path)
    expression = '(semantic_record "atoms" "one" "{\\"handle\\":\\"one\\"}")'

    transport.assert_expression(expression)
    transport.assert_expression(expression)

    assert transport.query("semantic_record") == (expression,)


def test_action_tree_replays_into_atomspace_and_reloads_indexes(tmp_path: Path) -> None:
    tree = tmp_path / "tree"
    node = tree / "node"
    node.mkdir(parents=True)
    artifact = node / "observation.json"
    artifact.write_text(
        json.dumps(
            {
                "observation_id": "observation-one",
                "source_modality": "logical_grid",
                "artifacts": [
                    {
                        "artifact_id": "grid-one",
                        "artifact_type": "logical_grid",
                        "uri": "node/grid.json",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (node / "semantic_records.json").write_text(
        json.dumps(
            {
                "records": [
                    {
                        "record_type": "observation",
                        "record_id": "observation-one",
                        "artifact": "observation.json",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    atomspace_path = tmp_path / "semantic_memory.metta"

    replayed = ActionTreeSemanticReplay().replay(
        tree, SymbolicStore(AtomSpaceSemanticBackend(path=atomspace_path))
    )
    reloaded = SymbolicStore(
        AtomSpaceSemanticBackend(path=atomspace_path)
    ).hydrate()

    assert reloaded.snapshot() == replayed.snapshot()
    assert reloaded.get("observations", "observation-one") is not None
    assert reloaded.artifacts.get("grid-one") is not None
