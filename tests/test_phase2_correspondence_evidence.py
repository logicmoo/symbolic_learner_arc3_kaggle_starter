from omega_vision import (
    CorrespondenceEvidenceBuilder,
    EvidencePolarity,
    InstanceMatcher,
    InstanceParameters,
    ProvenanceRef,
)


def test_correspondence_evidence_signs_matches_and_explained_changes() -> None:
    proposal = InstanceMatcher().compare(
        candidate_id="candidate",
        current=InstanceParameters(
            position=(2.0, 1.0),
            appearance={"color": "red", "shape": "circle"},
            supported_transformations=("translation",),
        ),
        stored_identity_id="red_ball",
        stored=InstanceParameters(
            position=(1.0, 1.0),
            appearance={"color": "red", "shape": "circle"},
            supported_transformations=("translation",),
        ),
    )

    evidence = CorrespondenceEvidenceBuilder().build(
        proposal,
        source=ProvenanceRef("encounter", "property_matcher"),
    )

    by_property = {item.detail["property"]: item for item in evidence}
    assert by_property["position"].polarity is EvidencePolarity.SUPPORTS
    assert by_property["position"].detail["assessment"] == "allowed_transformation"
    assert by_property["appearance.color"].polarity is EvidencePolarity.SUPPORTS
    assert by_property["appearance.color"].detail["assessment"] == "exact_match"


def test_correspondence_evidence_marks_unexplained_changes_as_contradictions() -> None:
    proposal = InstanceMatcher().compare(
        candidate_id="candidate",
        current=InstanceParameters(appearance={"shape": "square"}),
        stored_identity_id="circle",
        stored=InstanceParameters(appearance={"shape": "circle"}),
    )

    evidence = CorrespondenceEvidenceBuilder().build(
        proposal,
        source=ProvenanceRef("encounter", "property_matcher"),
    )

    shape = next(item for item in evidence if item.detail["property"] == "appearance.shape")
    assert shape.polarity is EvidencePolarity.CONTRADICTS
    assert shape.detail["assessment"] == "unexplained_change"
    assert all("similarity" not in item.detail for item in evidence)
