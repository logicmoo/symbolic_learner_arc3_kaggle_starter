from object_memory import (
    ArtifactRef,
    EncounterRecord,
    EvidencePolarity,
    EvidenceRecord,
    GameObjectLearnerPayload,
    InMemorySemanticBackend,
    InstanceParameters,
    MatchProposal,
    Observation,
    Phase2LearnerPayloadBuilder,
    ProvenanceRef,
    SymbolicStore,
    TurtleProgramRef,
)


def test_real_phase2_records_build_a_versioned_serializable_learner_payload() -> None:
    store = SymbolicStore(InMemorySemanticBackend())
    source = ProvenanceRef("frame-1", "grid_adapter", "nodes/one")
    grid = ArtifactRef.create(
        artifact_type="logical_grid",
        uri="nodes/one/state.json",
        provenance=(source,),
    )
    turtle_artifact = ArtifactRef.create(
        artifact_type="turtle_program",
        uri="nodes/one/object.turtle.pl",
        provenance=(source,),
    )
    observation = store.put_observation(
        Observation.create(
            source_modality="logical_grid",
            artifacts=(grid,),
            candidate_object_ids=("candidate-blue",),
            action_tree_node="nodes/one",
            provenance=(source,),
        )
    )
    evidence = store.put_evidence(
        EvidenceRecord.create(
            subject_id="known-blue",
            polarity=EvidencePolarity.SUPPORTS,
            source=source,
            detail={"property": "relationships"},
        )
    )
    encounter = store.put_encounter(
        EncounterRecord.create(
            observation_id=observation.observation_id,
            action_tree_node="nodes/one",
            candidate_identity_id="candidate-blue",
            instance=InstanceParameters(
                appearance={"color": "blue"},
                relationships=({"target": "marker", "relation": "left_of"},),
            ),
            turtle_programs=(TurtleProgramRef(turtle_artifact, fit_score=1.0),),
            evidence_ids=(evidence.evidence_id,),
            changed_properties={"action": "RIGHT"},
            provenance=(source,),
        )
    )
    store.put_match_proposal(
        MatchProposal.create(
            candidate_id="candidate-blue",
            stored_identity_id="known-blue",
            matched_properties=("relationships",),
            evidence_ids=(evidence.evidence_id,),
            provenance=(source,),
        )
    )

    payload = Phase2LearnerPayloadBuilder(store).for_observation(
        observation.observation_id
    )
    restored = GameObjectLearnerPayload.from_dict(payload.to_dict())

    assert restored == payload
    assert payload.observation_id == observation.observation_id
    assert payload.encounter_ids == (encounter.encounter_id,)
    assert payload.objects[0]["relationships"] == [
        {"target": "marker", "relation": "left_of"}
    ]
    assert payload.objects[0]["turtle_artifact_ids"] == [
        turtle_artifact.artifact_id
    ]
    assert payload.correspondences[0]["candidate_id"] == "candidate-blue"
    assert payload.objects[0]["changed_properties"] == {"action": "RIGHT"}
    assert payload.evidence[0]["evidence_id"] == evidence.evidence_id
    assert payload.provenance == ("frame-1",)
