from dataclasses import replace

import pytest

from omega_vision import (
    ArtifactRef,
    EncounterRecord,
    InMemorySemanticBackend,
    Observation,
    SymbolicStore,
    TurtleProgramRef,
)


def test_symbolic_store_indexes_observation_and_turtle_artifacts() -> None:
    store = SymbolicStore(InMemorySemanticBackend())
    frame = ArtifactRef.create(
        artifact_type="source_grid",
        uri="nodes/00001/state.json",
        content_hash="sha256:grid",
    )
    turtle_artifact = ArtifactRef.create(
        artifact_type="turtle_program",
        uri="nodes/00001/object-red.metta",
        content_hash="sha256:turtle",
    )
    observation = Observation.create(
        source_modality="logical_grid",
        artifacts=(frame,),
        action_tree_node="nodes/00001",
    )
    encounter = EncounterRecord.create(
        observation_id=observation.observation_id,
        action_tree_node="nodes/00001",
        object_identity_id="object-red",
        turtle_programs=(TurtleProgramRef(turtle_artifact, fit_score=1.0),),
    )

    assert store.put_observation(observation) is observation
    assert store.put_encounter(encounter) is encounter
    assert store.get("observations", observation.observation_id) is observation
    assert store.artifacts.by_type("source_grid") == (frame,)
    assert store.artifacts.by_type("turtle_program") == (turtle_artifact,)
    assert store.encounters.for_object("object-red") == (encounter,)


def test_symbolic_store_is_idempotent_but_rejects_identity_conflicts() -> None:
    store = SymbolicStore(InMemorySemanticBackend())
    artifact = ArtifactRef.create(artifact_type="mask", uri="mask.json")

    assert store.put_artifact(artifact) is artifact
    assert store.put_artifact(artifact) is artifact
    with pytest.raises(ValueError, match="identity conflict"):
        store.put_artifact(replace(artifact, media_type="application/json"))
