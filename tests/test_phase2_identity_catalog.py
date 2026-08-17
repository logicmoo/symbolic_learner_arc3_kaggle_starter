from object_memory import (
    EncounterRecord,
    InMemorySemanticBackend,
    InstanceParameters,
    RecognitionSession,
    SemanticIdentityCatalog,
    SymbolicStore,
)
from action_tree import ActionTreeStore


def test_identity_catalog_round_trips_best_form_into_a_new_example() -> None:
    source = SymbolicStore(InMemorySemanticBackend())
    source.put_encounter(
        EncounterRecord.create(
            observation_id="example-a",
            action_tree_node="example-a/node-1",
            object_identity_id="blue_hook",
            instance=InstanceParameters(
                position=(1.0, 2.0),
                appearance={"color": "blue", "shape": "hook"},
                geometry={"cells": ((0, 0), (0, 1), (1, 1))},
            ),
        )
    )
    catalog = SemanticIdentityCatalog.from_store(source, source="example-a")
    restored = SemanticIdentityCatalog.from_json(catalog.to_json())
    destination = SymbolicStore(InMemorySemanticBackend())

    imported = restored.import_into(destination)

    assert len(imported) == 1
    assert imported[0].object_identity_id == "blue_hook"
    assert imported[0].instance == source.encounters.records()[0].instance
    assert imported[0].provenance[0].provider == "semantic_identity_catalog"


def test_imported_identity_is_proposed_but_not_auto_authorized() -> None:
    source = SymbolicStore(InMemorySemanticBackend())
    source.put_encounter(
        EncounterRecord.create(
            observation_id="example-a",
            action_tree_node="example-a/node-1",
            object_identity_id="red_ball",
            instance=InstanceParameters(appearance={"color": "red", "shape": "ball"}),
        )
    )
    destination = SymbolicStore(InMemorySemanticBackend())
    SemanticIdentityCatalog.from_store(source, source="example-a").import_into(destination)
    candidate = destination.put_encounter(
        EncounterRecord.create(
            observation_id="example-b",
            action_tree_node="example-b/node-1",
            candidate_identity_id="candidate-red",
            instance=InstanceParameters(appearance={"color": "red", "shape": "ball"}),
        )
    )

    proposals = RecognitionSession(destination).propose(candidate.encounter_id)
    account = RecognitionSession(destination).unresolved_account("candidate-red")

    assert [item.stored_identity_id for item in proposals] == ["red_ball"]
    assert proposals[0].similarity == 1.0
    assert account is not None
    assert account.stored_identity_id is None
    assert account.decision_source == "unresolved"


def test_identity_catalog_installs_exact_friendly_fact_and_rejects_conflict(
    tmp_path,
) -> None:
    source = SymbolicStore(InMemorySemanticBackend())
    source.put_encounter(
        EncounterRecord.create(
            observation_id="example-a",
            action_tree_node="example-a/node-1",
            object_identity_id="blue_hook",
            instance=InstanceParameters(appearance={"color": "blue"}),
        )
    )
    fact = "object_identity(blue_hook, object, 'Blue hook')."
    catalog = SemanticIdentityCatalog.from_store(
        source,
        source="example-a",
        registry={"blue_hook": fact},
    )
    destination = ActionTreeStore(tmp_path, "game-b", 1)

    installed = catalog.install_registry(destination)

    assert installed == {"blue_hook": fact}
    assert destination.registry_identities() == {"blue_hook": fact}
    destination.write_registry(
        {"blue_hook": "object_identity(blue_hook, hazard, 'Wrong type')."}
    )
    try:
        catalog.install_registry(destination)
    except ValueError as exc:
        assert "Registry identity conflict" in str(exc)
    else:
        raise AssertionError("conflicting cross-example identity must be rejected")
