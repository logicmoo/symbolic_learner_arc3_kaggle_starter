from object_memory import (
    CorrespondenceEvidenceBuilder,
    EvidencePolarity,
    InstanceMatcher,
    InstanceParameters,
    ProvenanceRef,
)


def _hollow(position: tuple[float, float]) -> InstanceParameters:
    return InstanceParameters(
        position=position,
        appearance={"color": "gray", "shape": "hollow_square"},
        supported_transformations=("translation",),
        geometry={
            "width": 3,
            "height": 3,
            "boundary_cells": (
                (0.0, 0.0),
                (1.0, 0.0),
                (2.0, 0.0),
                (0.0, 1.0),
                (2.0, 1.0),
                (0.0, 2.0),
                (1.0, 2.0),
                (2.0, 2.0),
            ),
            "line_thickness": 1,
        },
        topology={
            "connected_components": 1,
            "hole_count": 1,
            "holes": (((1.0, 1.0),),),
        },
    )


def test_translated_hollow_object_retains_geometry_and_topology_evidence() -> None:
    proposal = InstanceMatcher().compare(
        candidate_id="translated-hollow",
        current=_hollow((8.0, 5.0)),
        stored_identity_id="hollow_square",
        stored=_hollow((1.0, 1.0)),
    )
    evidence = CorrespondenceEvidenceBuilder().build(
        proposal,
        source=ProvenanceRef("encounter", "topology_matcher"),
    )

    assert "translation" in proposal.allowed_transformations
    assert "geometry" in proposal.matched_properties
    assert "topology" in proposal.matched_properties
    by_property = {item.detail["property"]: item for item in evidence}
    assert by_property["geometry"].polarity is EvidencePolarity.SUPPORTS
    assert by_property["topology"].polarity is EvidencePolarity.SUPPORTS
