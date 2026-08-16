from dataclasses import FrozenInstanceError, asdict

import pytest

from object_memory import (
    ArtifactRef,
    EncounterRecord,
    EvidencePolarity,
    EvidenceRecord,
    IdentityDecision,
    InstanceParameters,
    MatchProposal,
    MergeDecision,
    Observation,
    PHASE2_SCHEMA_VERSION,
    ProvenanceRef,
    RecognitionAccount,
    SplitDecision,
    TurtleProgramRef,
    deterministic_identifier,
)


def test_deterministic_identifier_is_order_independent_and_type_scoped() -> None:
    left = deterministic_identifier("observation", {"frame": 7, "shape": {"x": 1, "y": 2}})
    right = deterministic_identifier("observation", {"shape": {"y": 2, "x": 1}, "frame": 7})

    assert left == right
    assert left.startswith("observation-")
    assert deterministic_identifier("encounter", {"frame": 7, "shape": {"x": 1, "y": 2}}) != left


def test_observation_layers_semantics_over_phase1_artifacts_and_node() -> None:
    provenance = ProvenanceRef(
        source_id="run-7/frame-12",
        provider="arc3.capture",
        action_tree_node="nodes/00012",
        sequence=12,
    )
    frame = ArtifactRef(
        artifact_id="frame-12",
        artifact_type="source_grid",
        uri="artifacts/frame-12.json",
        content_hash="sha256:abc",
        media_type="application/json",
        provenance=(provenance,),
    )
    first = Observation.create(
        source_modality="logical_grid",
        artifacts=(frame,),
        dimensions=(30, 30),
        coordinate_contract="row-major integer cells; origin top-left",
        candidate_object_ids=("candidate-red-square",),
        action_tree_node="nodes/00012",
        provenance=(provenance,),
    )
    second = Observation.create(
        source_modality="logical_grid",
        artifacts=(frame,),
        dimensions=(30, 30),
        coordinate_contract="row-major integer cells; origin top-left",
        candidate_object_ids=("candidate-red-square",),
        action_tree_node="nodes/00012",
        provenance=(provenance,),
    )

    assert first == second
    assert first.observation_id.startswith("observation-")
    assert first.artifacts[0].provenance[0].action_tree_node == "nodes/00012"
    assert first.schema_version == PHASE2_SCHEMA_VERSION
    with pytest.raises(FrozenInstanceError):
        first.source_modality = "image"  # type: ignore[misc]


def test_encounter_links_identity_instance_turtle_evidence_and_phase1_history() -> None:
    provenance = ProvenanceRef("run-7/frame-12", "grid_adapter", "nodes/00012")
    program_artifact = ArtifactRef(
        "turtle-red-square",
        "turtle_program",
        "artifacts/turtle-red-square.metta",
        provenance=(provenance,),
    )
    turtle = TurtleProgramRef(
        program_artifact,
        fit_score=0.98,
        distance=1.0,
        residual_score=0.02,
        description_length=18.0,
    )
    evidence = EvidenceRecord.create(
        subject_id="object-red-square",
        polarity=EvidencePolarity.SUPPORTS,
        source=provenance,
        detail={"matched": ["color", "topology"]},
        created_sequence=12,
    )
    encounter = EncounterRecord.create(
        observation_id="observation-12",
        action_tree_node="nodes/00012",
        object_identity_id="object-red-square",
        candidate_identity_id="candidate-red-square",
        instance=InstanceParameters(
            position=(4.0, 9.0),
            orientation=0.0,
            scale=(1.0, 1.0),
            appearance={"color": "red"},
            supported_transformations=("translation", "recolor"),
        ),
        matched_properties=("color", "topology"),
        changed_properties={"position": {"from": [3, 9], "to": [4, 9]}},
        turtle_programs=(turtle,),
        evidence_ids=(evidence.evidence_id,),
        confidence=0.86,
        provenance=(provenance,),
    )

    assert encounter.encounter_id == f"encounter-{encounter.deterministic_hash}"
    assert encounter.action_tree_node == "nodes/00012"
    assert encounter.turtle_programs[0].artifact.artifact_type == "turtle_program"
    assert encounter.evidence_ids == (evidence.evidence_id,)
    assert asdict(encounter)["instance"]["supported_transformations"] == (
        "translation",
        "recolor",
    )


def test_positive_and_negative_evidence_have_distinct_stable_ids() -> None:
    source = ProvenanceRef("comparison-9", "recognizer")
    positive = EvidenceRecord.create(
        subject_id="proposal-1",
        polarity=EvidencePolarity.SUPPORTS,
        source=source,
        detail={"fit": 0.95},
    )
    negative = EvidenceRecord.create(
        subject_id="proposal-1",
        polarity=EvidencePolarity.CONTRADICTS,
        source=source,
        detail={"fit": 0.95},
    )

    assert positive.evidence_id != negative.evidence_id
    assert positive.weight == negative.weight == 1.0
    assert positive.schema_version == negative.schema_version == PHASE2_SCHEMA_VERSION


def test_identity_proposals_accounts_and_reversible_decisions_are_reproducible() -> None:
    proposal = MatchProposal.create(
        candidate_id="candidate-1",
        stored_identity_id="object-1",
        matched_properties=("color", "topology"),
        changed_properties={"position": [2, 3]},
        allowed_transformations=("translation",),
        evidence_ids=("evidence-positive",),
    )
    account = RecognitionAccount.create(
        candidate_id="candidate-1",
        stored_identity_id="object-1",
        matched_properties=("color", "topology"),
        rival_proposal_ids=("proposal-rival",),
        supporting_evidence_ids=("evidence-positive",),
        contradicting_evidence_ids=("evidence-negative",),
        calibrated_confidence=0.74,
        decision_source="single_writer",
    )
    merge = MergeDecision.create(
        identity_ids=("object-2", "object-1"),
        resulting_identity_id="object-1",
        status=IdentityDecision.ACCEPTED,
        evidence_ids=("evidence-positive",),
    )
    split = SplitDecision.create(
        source_identity_id="object-1",
        resulting_identity_ids=("object-1a", "object-1b"),
        status=IdentityDecision.REVERSED,
        evidence_ids=("evidence-negative",),
    )

    assert proposal.proposal_id == MatchProposal.create(
        candidate_id="candidate-1",
        stored_identity_id="object-1",
        matched_properties=("color", "topology"),
        changed_properties={"position": [2, 3]},
        allowed_transformations=("translation",),
        evidence_ids=("evidence-positive",),
    ).proposal_id
    assert account.supporting_evidence_ids and account.contradicting_evidence_ids
    assert account.rival_proposal_ids == ("proposal-rival",)
    assert merge.decision_id.startswith("merge-decision-")
    assert split.status is IdentityDecision.REVERSED
