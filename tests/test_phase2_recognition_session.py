from python.object_memory import (
    EncounterRecord,
    InMemorySemanticBackend,
    InstanceParameters,
    RecognitionSession,
    SymbolicStore,
)


def test_recognition_session_persists_all_unresolved_proposals() -> None:
    store = SymbolicStore(InMemorySemanticBackend())
    store.put_encounter(
        EncounterRecord.create(
            observation_id="before",
            action_tree_node="node-before-red",
            object_identity_id="red_ball",
            instance=InstanceParameters(position=(1.0, 1.0), appearance={"color": "red"}),
        )
    )
    store.put_encounter(
        EncounterRecord.create(
            observation_id="before",
            action_tree_node="node-before-blue",
            object_identity_id="blue_square",
            instance=InstanceParameters(position=(4.0, 4.0), appearance={"color": "blue"}),
        )
    )
    candidate = store.put_encounter(
        EncounterRecord.create(
            observation_id="after",
            action_tree_node="node-after",
            candidate_identity_id="candidate_red",
            instance=InstanceParameters(position=(2.0, 1.0), appearance={"color": "red"}),
        )
    )

    proposals = RecognitionSession(store).propose(candidate.encounter_id)

    assert [item.stored_identity_id for item in proposals] == ["red_ball", "blue_square"]
    assert len(store.values("match_proposals")) == 2
    assert len(store.values("evidence")) > 0
    assert all(item.evidence_ids for item in proposals)
    account = store.values("recognition_accounts")[0]
    assert account.stored_identity_id is None
    assert account.decision_source == "unresolved"
    assert set(account.rival_proposal_ids) == {item.proposal_id for item in proposals}


def test_recognition_session_uses_latest_instance_per_known_identity() -> None:
    store = SymbolicStore(InMemorySemanticBackend())
    first = store.put_encounter(
        EncounterRecord.create(
            observation_id="one",
            action_tree_node="node-one",
            object_identity_id="red_ball",
            instance=InstanceParameters(position=(1.0, 1.0)),
        )
    )
    store.put_encounter(
        EncounterRecord.create(
            observation_id="two",
            action_tree_node="node-two",
            object_identity_id="red_ball",
            instance=InstanceParameters(position=(3.0, 3.0)),
            previous_encounter_id=first.encounter_id,
        )
    )
    candidate = store.put_encounter(
        EncounterRecord.create(
            observation_id="three",
            action_tree_node="node-three",
            candidate_identity_id="candidate",
            instance=InstanceParameters(position=(3.0, 3.0)),
        )
    )

    proposal = RecognitionSession(store).propose(candidate.encounter_id)[0]

    assert proposal.stored_identity_id == "red_ball"
    assert proposal.similarity == 1.0


def test_recognition_session_rejects_non_candidate_encounters() -> None:
    store = SymbolicStore(InMemorySemanticBackend())
    encounter = store.put_encounter(
        EncounterRecord.create(
            observation_id="known",
            action_tree_node="node-known",
            object_identity_id="known_object",
        )
    )

    try:
        RecognitionSession(store).propose(encounter.encounter_id)
    except ValueError as exc:
        assert "candidate encounter" in str(exc)
    else:
        raise AssertionError("known encounters must not be proposed as new candidates")
