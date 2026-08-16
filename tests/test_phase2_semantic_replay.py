import pytest

from object_memory import (
    ArtifactRef,
    EncounterRecord,
    EvidencePolarity,
    EvidenceRecord,
    InMemorySemanticBackend,
    InstanceMatcher,
    InstanceParameters,
    Observation,
    ProvenanceRef,
    RecognitionSession,
    SymbolicStore,
    TurtleProgramRef,
)


def _populated_store() -> SymbolicStore:
    store = SymbolicStore(InMemorySemanticBackend())
    source = ProvenanceRef("source", "fixture")
    artifact = ArtifactRef.create(
        artifact_type="turtle_program",
        uri="memory://turtle/red",
        provenance=(source,),
    )
    observation = Observation.create(
        source_modality="logical_grid",
        artifacts=(artifact,),
        provenance=(source,),
    )
    store.put_observation(observation)
    store.put_encounter(
        EncounterRecord.create(
            observation_id=observation.observation_id,
            action_tree_node="known-node",
            object_identity_id="red_ball",
            instance=InstanceParameters(appearance={"color": "red"}),
            turtle_programs=(TurtleProgramRef(artifact),),
            provenance=(source,),
        )
    )
    candidate = store.put_encounter(
        EncounterRecord.create(
            observation_id="candidate-observation",
            action_tree_node="candidate-node",
            candidate_identity_id="candidate-red",
            instance=InstanceParameters(appearance={"color": "red"}),
            provenance=(source,),
        )
    )
    RecognitionSession(store, InstanceMatcher()).propose(candidate.encounter_id)
    store.put_evidence(
        EvidenceRecord.create(
            subject_id="red_ball",
            polarity=EvidencePolarity.SUPPORTS,
            source=source,
            detail={"manual": True},
        )
    )
    return store


def test_semantic_store_snapshot_replays_every_namespace_and_index() -> None:
    original = _populated_store()
    snapshot = original.snapshot()
    replayed = SymbolicStore(InMemorySemanticBackend()).replay(snapshot)

    assert replayed.snapshot() == snapshot
    assert replayed.encounters.deterministic_hash() == original.encounters.deterministic_hash()
    artifact_id = snapshot["artifacts"][0].artifact_id
    assert replayed.artifacts.get(artifact_id) == original.artifacts.get(artifact_id)
    assert replayed.replay(snapshot).snapshot() == snapshot


def test_semantic_store_replay_rejects_unknown_namespaces() -> None:
    with pytest.raises(ValueError, match="unknown semantic snapshot namespaces"):
        SymbolicStore(InMemorySemanticBackend()).replay({"mystery": ()})
