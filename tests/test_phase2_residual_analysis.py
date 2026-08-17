from object_memory import (
    InstanceMatcher,
    InstanceParameters,
    ResidualAnalyzer,
    ResidualDisposition,
)


def test_residual_analyzer_absorbs_declared_transformations() -> None:
    proposal = InstanceMatcher().compare(
        candidate_id="moved-ball",
        current=InstanceParameters(
            position=(2.0, 1.0),
            supported_transformations=("translation",),
        ),
        stored_identity_id="ball",
        stored=InstanceParameters(
            position=(1.0, 1.0),
            supported_transformations=("translation",),
        ),
    )

    assert ResidualAnalyzer().from_proposal(proposal) == ()


def test_residual_analyzer_preserves_unexplained_structure() -> None:
    proposal = InstanceMatcher().compare(
        candidate_id="changed-shape",
        current=InstanceParameters(appearance={"shape": "square"}),
        stored_identity_id="circle",
        stored=InstanceParameters(appearance={"shape": "circle"}),
    )

    residual = ResidualAnalyzer().from_proposal(proposal)[0]

    assert residual.disposition is ResidualDisposition.PROVISIONAL
    assert residual.structured is True
    assert residual.recurrence_count == 1
    assert residual.provenance == (proposal.proposal_id, "field:appearance.shape")
