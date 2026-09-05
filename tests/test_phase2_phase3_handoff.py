import pytest

from omega_vision import (
    ArtifactRef,
    CommittedAtom,
    EncounterRecord,
    EvidencePolarity,
    EvidenceRecord,
    GameLearningPipeline,
    GameObjectLearnerPayload,
    IntegrationError,
    IntegrationValidator,
    InMemorySemanticBackend,
    InstanceParameters,
    MatchProposal,
    Observation,
    ObjectChange,
    Phase2LearnerPayloadBuilder,
    PredictionLedger,
    ProvenanceRef,
    phase2_transformation_learner,
    phase2_transition_analyzer,
    phase2_rule_inducer,
    phase2_rule_executor,
    phase2_rule_ranker,
    RuleStore,
    SymbolicStore,
    TurtleProgramRef,
    TransitionRecord,
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
    store.put_atom(CommittedAtom("known-blue", "object", {"label": "Known blue"}))

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
    assert payload.identity_ids == ("known-blue",)


def test_learner_payload_rejects_dangling_identity_candidate_and_provenance_refs() -> None:
    base = dict(
        state_id="state",
        objects=(
            {
                "id": "candidate-blue",
                "candidate_identity_id": "candidate-blue",
                "object_identity_id": "known-blue",
                "provenance": [
                    {"source_id": "frame-1", "provider": "grid_adapter"}
                ],
            },
        ),
        identity_ids=("known-blue",),
        provenance=("frame-1",),
    )
    assert IntegrationValidator().validate(GameObjectLearnerPayload(**base))

    invalid_payloads = (
        GameObjectLearnerPayload(**{**base, "identity_ids": ()}),
        GameObjectLearnerPayload(
            **{
                **base,
                "correspondences": (
                    {
                        "candidate_id": "candidate-missing",
                        "stored_identity_id": "known-blue",
                    },
                ),
            }
        ),
        GameObjectLearnerPayload(**{**base, "provenance": ()}),
    )
    for payload in invalid_payloads:
        try:
            IntegrationValidator().validate(payload)
        except IntegrationError:
            pass
        else:
            raise AssertionError("dangling learner reference must be rejected")


def test_learner_payload_strictly_validates_durable_identity_and_provenance() -> None:
    payload = GameObjectLearnerPayload(
        state_id="state",
        objects=({"id": "known-blue", "object_identity_id": "known-blue"},),
        identity_ids=("known-blue",),
        provenance=("frame-1",),
    )
    assert IntegrationValidator(
        registry_identity_ids={"known-blue"},
        provenance_source_ids={"frame-1"},
    ).validate(payload) == payload

    with pytest.raises(IntegrationError, match="absent from durable memory"):
        IntegrationValidator(
            registry_identity_ids=set(),
            provenance_source_ids={"frame-1"},
        ).validate(payload)
    with pytest.raises(IntegrationError, match="provenance sources"):
        IntegrationValidator(
            registry_identity_ids={"known-blue"},
            provenance_source_ids=set(),
        ).validate(payload)


def test_real_phase2_change_becomes_an_evidence_linked_transformation_candidate() -> None:
    before = GameObjectLearnerPayload(
        state_id="before",
        objects=({"id": "known-blue"},),
        identity_ids=("known-blue",),
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
        objects=({"id": "candidate-blue", "candidate_identity_id": "candidate-blue"},),
        transitions=(change.__dict__,),
        identity_ids=("known-blue",),
        evidence=({"evidence_id": "evidence-moved"},),
        provenance=("frame-after",),
    )

    transition = phase2_transition_analyzer().analyze(before, "RIGHT", after)
    candidates = phase2_transformation_learner().learn(transition)

    assert transition.before_state_id == "before"
    assert transition.after_state_id == "after"
    assert transition.action_or_event == "RIGHT"
    assert transition.provenance == ("frame-before", "frame-after")
    assert len(candidates) == 2
    assert {item.transformation["interpretation"] for item in candidates} == {
        "absolute_target",
        "relative_delta",
    }
    assert all(item.transformation["kind"] == "moved" for item in candidates)
    assert all(item.evidence == ("evidence-moved",) for item in candidates)
    assert all(item.candidate_id.startswith("transformation-") for item in candidates)


def test_real_transformation_candidates_induce_explicitly_rival_bootstrap_rules() -> None:
    transition = phase2_transition_analyzer().analyze(
        GameObjectLearnerPayload("before", ({"id": "blue"},), identity_ids=("blue",)),
        "RIGHT",
        GameObjectLearnerPayload(
            "after",
            ({"id": "candidate-blue", "candidate_identity_id": "candidate-blue"},),
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
            identity_ids=("blue",),
            evidence=(
                {"evidence_id": "evidence-move"},
                {"evidence_id": "evidence-relation"},
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
                GameObjectLearnerPayload("before", ({"id": "blue"},), identity_ids=("blue",)),
                "RIGHT",
                GameObjectLearnerPayload(
                    "after",
                    ({"id": "candidate-blue"},),
                    transitions=(
                        {"kind": "moved", "evidence_ids": ["move-evidence"]},
                        {"kind": "recolored", "evidence_ids": ["color-evidence"]},
                    ),
                    evidence=(
                        {"evidence_id": "move-evidence"},
                        {"evidence_id": "color-evidence"},
                    ),
                ),
            )
        )
    )
    from omega_vision import RuleStore

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


def test_learned_translation_applies_relative_delta_to_an_unseen_object() -> None:
    transition = phase2_transition_analyzer().analyze(
        GameObjectLearnerPayload("before", ({"id": "known", "position": [1, 1]},)),
        "RIGHT",
        GameObjectLearnerPayload(
            "after",
            ({"id": "known-after", "position": [2, 1]},),
            transitions=(
                {
                    "kind": "moved",
                    "properties": {"position": {"from": [1, 1], "to": [2, 1]}},
                    "evidence_ids": ["move-evidence"],
                },
            ),
            evidence=({"evidence_id": "move-evidence"},),
        ),
    )
    rules = phase2_rule_inducer().induce(
        phase2_transformation_learner().learn(transition)
    )
    assert len(rules) == 2
    assert all(item.rival_rule_ids for item in rules)
    rule = next(
        item
        for item in rules
        if item.predicted_effects[0]["interpretation"] == "relative_delta"
    )
    store = RuleStore()
    store.store(rule)
    unseen = {"id": "previously-unseen-red", "position": [7, 4], "color": "red"}

    executor = phase2_rule_executor(store, "RIGHT")
    assert executor.applicable(rule.rule_id, unseen)
    assert executor.apply(rule.rule_id, unseen) == {
        "id": "previously-unseen-red",
        "position": [8, 4],
        "color": "red",
    }
    assert unseen["position"] == [7, 4]
    assert not phase2_rule_executor(store, "LEFT").applicable(rule.rule_id, unseen)

    absolute_rule = next(
        item
        for item in rules
        if item.predicted_effects[0]["interpretation"] == "absolute_target"
    )
    store.store(absolute_rule)
    assert executor.apply(absolute_rule.rule_id, unseen)["position"] == [2, 1]

    ledger = PredictionLedger()
    pipeline = GameLearningPipeline(
        phase2_transition_analyzer(),
        phase2_transformation_learner(),
        phase2_rule_inducer(),
        phase2_rule_ranker(),
        store,
        ledger,
    )
    predicted, record = pipeline.predict(
        prediction_id="prediction-unseen-red",
        rule_id=rule.rule_id,
        source_state_id="unseen-state",
        state=unseen,
        created_sequence=10,
        executor=executor,
    )
    assert predicted["position"] == [8, 4]
    assert record.predicted_effects == (predicted,)
    assert ledger.get(record.prediction_id) == record


def test_domain_generalizations_scale_toggle_and_edit_unseen_state() -> None:
    transition = TransitionRecord(
        before_state_id="before",
        action_or_event="TRANSFORM",
        after_state_id="after",
        changes=(
            {
                "kind": "scaled",
                "properties": {
                    "size": {"from": [2, 4], "to": [4, 2]},
                    "visible": {"from": True, "to": False},
                    "tags": {"from": ["old", "keep"], "to": ["keep", "new"]},
                },
                "evidence_ids": ["transform-evidence"],
            },
        ),
    )
    candidates = phase2_transformation_learner().learn(transition)
    by_kind = {item.transformation["interpretation"]: item for item in candidates}
    assert {
        "absolute_target",
        "relative_delta",
        "multiplicative_scale",
        "boolean_toggle",
        "set_edit",
    } <= set(by_kind)

    rules = phase2_rule_inducer().induce(candidates)
    store = RuleStore()
    for rule in rules:
        store.store(rule)
    executor = phase2_rule_executor(store, "TRANSFORM")
    unseen = {"size": [3, 10], "visible": False, "tags": ["old", "other"]}

    rule_by_kind = {
        rule.predicted_effects[0]["interpretation"]: rule for rule in rules
    }
    assert executor.apply(
        rule_by_kind["multiplicative_scale"].rule_id, unseen
    )["size"] == [6.0, 5.0]
    assert executor.apply(
        rule_by_kind["boolean_toggle"].rule_id, unseen
    )["visible"] is True
    assert executor.apply(rule_by_kind["set_edit"].rule_id, unseen)["tags"] == [
        "other",
        "new",
    ]


def test_relationship_edit_generalizes_attachment_to_unseen_state() -> None:
    transition = TransitionRecord(
        before_state_id="before",
        action_or_event="ATTACH",
        after_state_id="after",
        changes=(
            {
                "kind": "relationship_changed",
                "properties": {
                    "relationships": {
                        "from": [{"relation": "near", "target": "anchor"}],
                        "to": [{"relation": "attached_to", "target": "anchor"}],
                    }
                },
                "evidence_ids": ["attachment-evidence"],
            },
        ),
    )
    rules = phase2_rule_inducer().induce(
        phase2_transformation_learner().learn(transition)
    )
    relationship_rule = next(
        rule
        for rule in rules
        if rule.predicted_effects[0]["interpretation"] == "relationship_edit"
    )
    store = RuleStore()
    store.store(relationship_rule)
    unseen = {
        "relationships": [
            {"relation": "near", "target": "anchor"},
            {"relation": "left_of", "target": "marker"},
        ]
    }

    result = phase2_rule_executor(store, "ATTACH").apply(
        relationship_rule.rule_id, unseen
    )
    assert result["relationships"] == [
        {"relation": "left_of", "target": "marker"},
        {"relation": "attached_to", "target": "anchor"},
    ]


def test_object_relative_motion_uses_the_unseen_reference_position() -> None:
    transition = TransitionRecord(
        before_state_id="before",
        action_or_event="DOCK",
        after_state_id="after",
        changes=(
            {
                "kind": "moved",
                "properties": {
                    "position": {"from": [1, 1], "to": [4, 3]},
                    "reference_position": {"from": [5, 1], "to": [7, 3]},
                },
                "evidence_ids": ["dock-evidence"],
            },
        ),
    )
    rules = phase2_rule_inducer().induce(
        phase2_transformation_learner().learn(transition)
    )
    relative = next(
        rule
        for rule in rules
        if rule.predicted_effects[0]["interpretation"] == "object_relative_position"
    )
    store = RuleStore()
    store.store(relative)

    result = phase2_rule_executor(store, "DOCK").apply(
        relative.rule_id,
        {"position": [20, 20], "reference_position": [100, 50], "color": "blue"},
    )

    assert result == {
        "position": [97, 50],
        "reference_position": [100, 50],
        "color": "blue",
    }
    assert relative.predicted_effects[0]["offset"] == [-3, 0]


def test_topology_rewrite_preserves_unobserved_structure_on_unseen_state() -> None:
    transition = TransitionRecord(
        before_state_id="before",
        action_or_event="OPEN",
        after_state_id="after",
        changes=(
            {
                "kind": "topology_changed",
                "properties": {
                    "topology": {
                        "from": {
                            "holes": 0,
                            "components": 1,
                            "boundary": {"closed": True, "segments": 4},
                        },
                        "to": {
                            "holes": 1,
                            "components": 1,
                            "boundary": {"closed": False, "segments": 4},
                        },
                    }
                },
                "evidence_ids": ["topology-evidence"],
            },
        ),
    )
    rules = phase2_rule_inducer().induce(
        phase2_transformation_learner().learn(transition)
    )
    rewrite = next(
        rule
        for rule in rules
        if rule.predicted_effects[0]["interpretation"]
        == "structural_topology_rewrite"
    )
    store = RuleStore()
    store.store(rewrite)

    result = phase2_rule_executor(store, "OPEN").apply(
        rewrite.rule_id,
        {
            "topology": {
                "holes": 3,
                "components": 9,
                "boundary": {"closed": True, "segments": 12, "material": "stone"},
                "symmetry": "vertical",
            }
        },
    )

    assert result["topology"] == {
        "holes": 1,
        "components": 9,
        "boundary": {"closed": False, "segments": 12, "material": "stone"},
        "symmetry": "vertical",
    }
