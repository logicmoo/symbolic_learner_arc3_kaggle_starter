from dataclasses import asdict

import pytest

from omega_vision import (
    InstanceMatcher,
    InstanceParameters,
    RecognitionAccount,
    RecognitionCalibrator,
    SemanticRecordCodec,
)


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


def test_match_proposal_covers_the_complete_supported_transformation_matrix() -> None:
    supported = (
        "translation",
        "rotation",
        "scale",
        "reflection",
        "recolor",
        "noise",
        "partial_visibility",
    )
    stored = InstanceParameters(
        position=(1.0, 2.0),
        orientation=0.0,
        scale=(1.0, 1.0),
        reflection="none",
        appearance={"color": "red", "shape": "square"},
        supported_transformations=supported,
    )
    current = InstanceParameters(
        position=(4.0, 5.0),
        orientation=90.0,
        scale=(2.0, 2.0),
        reflection="horizontal",
        appearance={"color": "blue", "shape": "square"},
        supported_transformations=supported,
        visibility=0.6,
        noise_score=0.1,
    )

    proposal = InstanceMatcher().compare(
        candidate_id="degraded-transform",
        current=current,
        stored_identity_id="object-1",
        stored=stored,
    )

    assert set(proposal.allowed_transformations) == set(supported)
    assert set(proposal.changed_properties) == {
        "position",
        "orientation",
        "scale",
        "reflection",
        "visibility",
        "noise_score",
        "appearance.color",
    }


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
    assert sum(item.probability for item in proposals) == pytest.approx(1.0)
    assert proposals[0].probability > proposals[1].probability
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


def test_scoped_policy_calibrates_and_normalizes_complete_rival_set() -> None:
    def account(confidence: float, outcome: bool, candidate: str) -> RecognitionAccount:
        return RecognitionAccount.create(
            candidate_id=candidate,
            stored_identity_id="known" if outcome else None,
            decision_confidence=confidence,
            decision_outcome=outcome,
            decision_source="fixture_authority",
        )

    policy = RecognitionCalibrator().fit(
        (
            account(0.2, False, "low-a"),
            account(0.4, False, "low-b"),
            account(0.8, True, "high-a"),
            account(1.0, True, "high-b"),
        ),
        scope="grid/exact-v1",
    )
    proposals = InstanceMatcher().proposals(
        candidate_id="candidate",
        current=_instance(),
        stored={
            "exact": _instance(),
            "different": _instance(shape="triangle", color="blue"),
        },
        calibration_policy=policy,
    )

    assert sum(item.probability for item in proposals) == pytest.approx(1.0)
    assert proposals[0].stored_identity_id == "exact"
    assert proposals[0].probability == 1.0
    assert proposals[1].probability == 0.0
    assert all(item.probability_source == "isotonic:grid/exact-v1" for item in proposals)
    assert SemanticRecordCodec.decode("match_proposal", asdict(proposals[0])) == proposals[0]
