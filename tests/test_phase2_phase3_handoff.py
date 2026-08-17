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
    ObjectChange,
    Phase2LearnerPayloadBuilder,
    ProvenanceRef,
    phase2_transformation_learner,
    phase2_transition_analyzer,
    phase2_rule_inducer,
    phase2_rule_ranker,
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


def test_real_phase2_change_becomes_an_evidence_linked_transformation_candidate() -> None:
    before = GameObjectLearnerPayload(
        state_id="before",
        objects=({"id": "known-blue"},),
        provenance=("frame-before",),
    )
    change = ObjectChange.create(
        kind="moved",
        before_identity_ids=("known-blue",),
        after_candidate_ids=("candidate-blue",),
        properties={"position": {"from": [1, 1], "to": [2, 1]}},
        evidence_ids=("evidence-moved",),
    )
    after = GameObjectLearnerPayload(
        state_id="after",
        objects=({"id": "candidate-blue"},),
        transitions=(change.__dict__,),
        provenance=("frame-after",),
    )

    transition = phase2_transition_analyzer().analyze(before, "RIGHT", after)
    candidates = phase2_transformation_learner().learn(transition)

    assert transition.before_state_id == "before"
    assert transition.after_state_id == "after"
    assert transition.action_or_event == "RIGHT"
    assert transition.provenance == ("frame-before", "frame-after")
    assert len(candidates) == 1
    assert candidates[0].transformation["kind"] == "moved"
    assert candidates[0].evidence == ("evidence-moved",)
    assert candidates[0].candidate_id.startswith("transformation-")


def test_real_transformation_candidates_induce_explicitly_rival_bootstrap_rules() -> None:
    transition = phase2_transition_analyzer().analyze(
        GameObjectLearnerPayload("before", ({"id": "blue"},)),
        "RIGHT",
        GameObjectLearnerPayload(
            "after",
            ({"id": "candidate-blue"},),
            transitions=(
                {
                    "kind": "moved",
                    "before_identity_ids": ["blue"],
                    "after_candidate_ids": ["candidate-blue"],
                    "evidence_ids": ["evidence-move"],
                },
                {
                    "kind": "relationship_changed",
                    "before_identity_ids": ["blue"],
                    "after_candidate_ids": ["candidate-blue"],
                    "evidence_ids": ["evidence-relation"],
                },
            ),
        ),
    )
    candidates = phase2_transformation_learner().learn(transition)

    rules = phase2_rule_inducer().induce(candidates)
    ranked = phase2_rule_ranker().rank(rules)

    assert len(rules) == 2
    assert {rule.predicted_effects[0]["kind"] for rule in rules} == {
        "moved",
        "relationship_changed",
    }
    assert all(rule.rival_rule_ids for rule in rules)
    assert all("identity_present:blue" in rule.assumptions for rule in rules)
    assert all("single_observation_bootstrap" in rule.critiques for rule in rules)
    assert all("contradiction_check_pending" in rule.critiques for rule in rules)
    assert all(rule.supporting_evidence_ids for rule in rules)
    assert all(rule.probability_source == "bootstrap" for rule in rules)
    assert all(rule.coverage == 1.0 for rule in rules)
    assert all(rule.calibrated_probability is None for rule in rules)
    assert {rule.rule_id for rule in ranked} == {rule.rule_id for rule in rules}


def test_verified_prediction_history_outranks_bootstrap_without_rewriting_identity() -> None:
    rules = phase2_rule_inducer().induce(
        phase2_transformation_learner().learn(
            phase2_transition_analyzer().analyze(
                GameObjectLearnerPayload("before", ({"id": "blue"},)),
                "RIGHT",
                GameObjectLearnerPayload(
                    "after",
                    ({"id": "candidate-blue"},),
                    transitions=(
                        {"kind": "moved", "evidence_ids": ["move-evidence"]},
                        {"kind": "recolored", "evidence_ids": ["color-evidence"]},
                    ),
                ),
            )
        )
    )
    from object_memory import RuleStore

    store = RuleStore()
    for rule in rules:
        store.store(rule)
    original_id = rules[1].rule_id
    updated = store.record_prediction_grade(
        original_id,
        prediction_id="prediction-verified",
        grade=1.0,
    )

    ranked = phase2_rule_ranker().rank(store.rules())
    assert updated.rule_id == original_id
    assert updated.calibrated_probability == 2.0 / 3.0
    assert updated.probability_source == "verified_prediction_history"
    assert ranked[0].rule_id == original_id
