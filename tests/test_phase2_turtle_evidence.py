from object_memory import (
    EvidencePolarity,
    FitResult,
    ProvenanceRef,
    TurtleReconstructionEvidenceBuilder,
)


def test_exact_turtle_reconstruction_supports_identity() -> None:
    evidence = TurtleReconstructionEvidenceBuilder().build(
        identity_id="blue_hook",
        fit=FitResult({"rendered_cells": 7}, residual=0.0),
        source=ProvenanceRef("encounter", "turtle_reconstruction"),
        artifact_id="turtle-blue",
    )

    assert evidence.polarity is EvidencePolarity.SUPPORTS
    assert evidence.detail["assessment"] == "exact_turtle_reconstruction"
    assert evidence.detail["artifact_id"] == "turtle-blue"


def test_turtle_reconstruction_residual_contradicts_identity() -> None:
    evidence = TurtleReconstructionEvidenceBuilder().build(
        identity_id="blue_hook",
        fit=FitResult({"rendered_cells": 6}, residual=0.25),
        source=ProvenanceRef("encounter", "turtle_reconstruction"),
    )

    assert evidence.polarity is EvidencePolarity.CONTRADICTS
    assert evidence.detail["assessment"] == "turtle_residual"
    assert evidence.detail["residual"] == 0.25
