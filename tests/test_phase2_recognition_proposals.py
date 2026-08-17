from object_memory import InstanceMatcher, InstanceParameters


def _instance(
    *,
    position=(1.0, 2.0),
    scale=(1.0, 1.0),
    color="red",
    shape="square",
) -> InstanceParameters:
    return InstanceParameters(
        position=position,
        orientation=0.0,
        scale=scale,
        appearance={"color": color, "shape": shape},
        supported_transformations=("translation", "recolor", "scale", "rotation"),
    )


def test_match_proposal_explains_translation_recolor_and_scale() -> None:
    proposal = InstanceMatcher().compare(
        candidate_id="candidate-1",
        current=_instance(position=(4.0, 2.0), scale=(2.0, 2.0), color="blue"),
        stored_identity_id="object-1",
        stored=_instance(),
    )

    assert set(proposal.allowed_transformations) == {"translation", "recolor", "scale"}
    assert set(proposal.changed_properties) == {
        "position",
        "scale",
        "appearance.color",
    }
    assert set(proposal.matched_properties) == {"orientation", "appearance.shape"}
    assert proposal.similarity == 2 / 5


def test_all_rival_proposals_are_retained_in_deterministic_advisory_order() -> None:
    matcher = InstanceMatcher()
    proposals = matcher.proposals(
        candidate_id="candidate-1",
        current=_instance(position=(3.0, 2.0)),
        stored={
            "object-wrong-shape": _instance(shape="triangle", color="green"),
            "object-square": _instance(),
        },
    )

    assert tuple(item.stored_identity_id for item in proposals) == (
        "object-square",
        "object-wrong-shape",
    )
    account = matcher.recognition_account(
        candidate_id="candidate-1",
        proposals=proposals,
        selected_identity_id="object-square",
        decision_source="single_writer",
    )
    assert account.stored_identity_id == "object-square"
    assert account.rival_proposal_ids == (proposals[1].proposal_id,)
    assert account.calibrated_confidence == 0.0


def test_similarity_never_commits_identity_or_confidence_by_itself() -> None:
    matcher = InstanceMatcher()
    proposals = matcher.proposals(
        candidate_id="candidate-1",
        current=_instance(),
        stored={"perfect-match": _instance()},
    )
    unresolved = matcher.recognition_account(
        candidate_id="candidate-1",
        proposals=proposals,
    )

    assert proposals[0].similarity == 1.0
    assert unresolved.stored_identity_id is None
    assert unresolved.calibrated_confidence == 0.0
    assert unresolved.decision_source == "unresolved"


def test_embedding_retrieval_is_advisory_and_never_becomes_evidence() -> None:
    matcher = InstanceMatcher()
    proposals = matcher.proposals(
        candidate_id="candidate-1",
        current=_instance(),
        stored={
            "property-match": _instance(),
            "embedding-match": _instance(shape="triangle", color="blue"),
        },
        retrieval_scores={
            "property-match": 0.1,
            "embedding-match": 1.0,
        },
        retrieval_source="fixture-embedding-v1",
    )

    assert proposals[0].stored_identity_id == "property-match"
    embedding = next(
        item for item in proposals if item.stored_identity_id == "embedding-match"
    )
    assert embedding.retrieval_score == 1.0
    assert embedding.retrieval_source == "fixture-embedding-v1"
    assert embedding.evidence_ids == ()
    unresolved = matcher.recognition_account(
        candidate_id="candidate-1",
        proposals=proposals,
    )
    assert unresolved.stored_identity_id is None
    assert unresolved.calibrated_confidence == 0.0
    assert unresolved.supporting_evidence_ids == ()
    assert unresolved.contradicting_evidence_ids == ()
