from object_memory import (
    CorrespondenceEvidenceBuilder,
    EncounterRecord,
    EvidencePolarity,
    InMemorySemanticBackend,
    InstanceMatcher,
    InstanceParameters,
    ProvenanceRef,
    RecognitionSession,
    SymbolicStore,
)


def test_partial_visibility_and_noise_are_explicit_supported_transformations() -> None:
    stored = InstanceParameters(
        appearance={"color": "red", "shape": "circle", "texture": "solid"},
        supported_transformations=("partial_visibility", "noise", "reflection"),
    )
    current = InstanceParameters(
        appearance={"color": "red", "shape": "circle"},
        supported_transformations=("partial_visibility", "noise", "reflection"),
        reflection="horizontal",
        visibility=0.7,
        noise_score=0.1,
    )

    proposal = InstanceMatcher().compare(
        candidate_id="partial-red",
        current=current,
        stored_identity_id="red_ball",
        stored=stored,
    )
    evidence = CorrespondenceEvidenceBuilder().build(
        proposal,
        source=ProvenanceRef("encounter", "degradation_matcher"),
    )

    assert {"partial_visibility", "noise", "reflection"}.issubset(
        proposal.allowed_transformations
    )
    by_property = {item.detail["property"]: item for item in evidence}
    assert by_property["appearance.texture"].polarity is EvidencePolarity.SUPPORTS
    assert by_property["visibility"].polarity is EvidencePolarity.SUPPORTS
    assert by_property["noise_score"].polarity is EvidencePolarity.SUPPORTS
    assert by_property["reflection"].polarity is EvidencePolarity.SUPPORTS


def test_partial_encounter_does_not_replace_complete_stored_form() -> None:
    store = SymbolicStore(InMemorySemanticBackend())
    complete = InstanceParameters(
        position=(1.0, 1.0),
        appearance={"color": "blue", "shape": "hook", "texture": "solid"},
        visibility=1.0,
        noise_score=0.0,
    )
    store.put_encounter(
        EncounterRecord.create(
            observation_id="complete",
            action_tree_node="node-complete",
            object_identity_id="blue_hook",
            instance=complete,
        )
    )
    store.put_encounter(
        EncounterRecord.create(
            observation_id="partial",
            action_tree_node="node-partial",
            object_identity_id="blue_hook",
            instance=InstanceParameters(
                position=(4.0, 2.0),
                appearance={"color": "blue"},
                visibility=0.4,
                noise_score=0.2,
                supported_transformations=("translation", "partial_visibility", "noise"),
            ),
        )
    )

    retained = RecognitionSession(store).latest_known_instances()["blue_hook"]

    assert retained.position == (4.0, 2.0)
    assert retained.appearance == complete.appearance
    assert retained.visibility == 1.0
    assert retained.noise_score == 0.0
    assert set(retained.supported_transformations) == {
        "translation",
        "partial_visibility",
        "noise",
    }
