import json
from pathlib import Path
from types import SimpleNamespace

from action_tree import ActionTreeStore
from object_memory import (
    ActionTreeSemanticReplay,
    EncounterRecord,
    EvidencePolarity,
    GridAdapter,
    InMemorySemanticBackend,
    InstanceParameters,
    PythonProvider,
    SemanticGridCaptureObserver,
    SingleWriter,
    SymbolicStore,
    SymbolicMemory,
)
from workbench.server.runtime import DEFAULT_GRID, analyze_grid


def test_semantic_capture_persists_and_links_observations_encounters_and_turtles(tmp_path: Path) -> None:
    tree = ActionTreeStore(tmp_path / "tree", "game", 1)
    initial = tree.create_initial(b"initial", {"state": "active"})
    observer = SemanticGridCaptureObserver(
        GridAdapter(analyze_grid, PythonProvider({})),
        grid_selector=lambda runner: runner.grid,
    )
    runner = SimpleNamespace(grid=DEFAULT_GRID)

    observer.on_state_captured(
        runner=runner,
        store=tree,
        node=initial,
        previous_node=None,
        action=None,
        data={},
    )
    child = tree.create_transition(initial, "RIGHT", {}, b"child", {"state": "active"})
    observer.on_state_captured(
        runner=runner,
        store=tree,
        node=child,
        previous_node=initial,
        action="RIGHT",
        data={},
    )

    initial_manifest = json.loads(initial.semantic_records_path.read_text(encoding="utf-8"))
    child_manifest = json.loads(child.semantic_records_path.read_text(encoding="utf-8"))
    assert [item["record_type"] for item in initial_manifest["records"]].count("observation") == 1
    assert [item["record_type"] for item in initial_manifest["records"]].count("encounter") == 2
    assert [item["record_type"] for item in initial_manifest["records"]].count("evidence") == 2
    assert [item["record_type"] for item in child_manifest["records"]].count("encounter") == 2
    assert len(tuple((initial.path / "semantic").glob("*.turtle.pl"))) == 2
    encounters = observer.symbolic_store.encounters.records()
    assert len(encounters) == 4
    assert encounters[2].previous_encounter_id == encounters[0].encounter_id
    assert encounters[3].previous_encounter_id == encounters[1].encounter_id
    assert all(encounter.evidence_ids for encounter in encounters)
    assert all(encounter.turtle_programs[0].fit_score == 1.0 for encounter in encounters)
    assert all(encounter.turtle_programs[0].residual_score == 0.0 for encounter in encounters)
    assert all(encounter.turtle_programs[0].description_length > 0 for encounter in encounters)
    assert encounters[0].instance.relationships == (
        {"target": "obj_red_1", "relation": "left_of"},
    )
    assert encounters[1].instance.relationships == (
        {"target": "obj_blue_1", "relation": "right_of"},
    )
    turtle_evidence = tuple(
        record
        for record in observer.symbolic_store.values("evidence")
        if str(record.detail.get("assessment", "")).startswith("turtle_")
        or record.detail.get("assessment") == "exact_turtle_reconstruction"
    )
    assert len(turtle_evidence) == 4
    assert all(record.polarity is EvidencePolarity.SUPPORTS for record in turtle_evidence)
    assert all(record.source.provider == "swi_prolog.turtle_dsl" for record in turtle_evidence)
    assert all(record.detail["assessment"] == "exact_turtle_reconstruction" for record in turtle_evidence)
    assert "## Semantic records" in child.readme_path.read_text(encoding="utf-8")
    replayed = ActionTreeSemanticReplay().replay(
        tree.level_root,
        SymbolicStore(InMemorySemanticBackend()),
    )
    assert len(replayed.encounters.records()) == 4
    assert len(replayed.values("evidence")) == len(observer.symbolic_store.values("evidence"))
    assert replayed.encounters.get(encounters[2].encounter_id).previous_encounter_id == (
        encounters[0].encounter_id
    )
    assert replayed.encounters.get(encounters[0].encounter_id).instance.relationships == (
        {"target": "obj_red_1", "relation": "left_of"},
    )


def test_semantic_capture_replays_level_history_after_observer_restart(tmp_path: Path) -> None:
    tree = ActionTreeStore(tmp_path / "tree", "game", 1)
    initial = tree.create_initial(b"initial", {"state": "active"})
    runner = SimpleNamespace(grid=DEFAULT_GRID)
    first_observer = SemanticGridCaptureObserver(
        GridAdapter(analyze_grid, PythonProvider({})),
        grid_selector=lambda active_runner: active_runner.grid,
    )
    first_observer.on_state_captured(
        runner=runner,
        store=tree,
        node=initial,
        previous_node=None,
        action=None,
        data={},
    )
    initial_encounters = first_observer.symbolic_store.encounters.records()
    initial_by_candidate = {
        encounter.candidate_identity_id: encounter.encounter_id
        for encounter in initial_encounters
    }

    child = tree.create_transition(initial, "RIGHT", {}, b"child", {"state": "active"})
    restarted_observer = SemanticGridCaptureObserver(
        GridAdapter(analyze_grid, PythonProvider({})),
        grid_selector=lambda active_runner: active_runner.grid,
    )
    restarted_observer.on_state_captured(
        runner=runner,
        store=tree,
        node=child,
        previous_node=initial,
        action="RIGHT",
        data={},
    )

    encounters = restarted_observer.symbolic_store.encounters.records()
    assert len(encounters) == 4
    later = encounters[2:]
    assert {
        encounter.previous_encounter_id for encounter in later
    } == set(initial_by_candidate.values())
    assert all(
        encounter.previous_encounter_id
        == initial_by_candidate[encounter.candidate_identity_id]
        for encounter in later
    )


def test_semantic_capture_links_unresolved_proposals_against_known_history(tmp_path: Path) -> None:
    tree = ActionTreeStore(tmp_path / "tree", "game", 1)
    initial = tree.create_initial(b"initial", {"state": "active"})
    semantic_store = SymbolicStore(InMemorySemanticBackend())
    semantic_store.put_encounter(
        EncounterRecord.create(
            observation_id="prior-observation",
            action_tree_node="prior-node",
            object_identity_id="known_shape",
            instance=InstanceParameters(
                position=(0.0, 0.0),
                appearance={"color": "blue", "shape": "rectangle"},
            ),
        )
    )
    observer = SemanticGridCaptureObserver(
        GridAdapter(analyze_grid, PythonProvider({})),
        grid_selector=lambda runner: runner.grid,
        symbolic_store=semantic_store,
    )

    observer.on_state_captured(
        runner=SimpleNamespace(grid=DEFAULT_GRID),
        store=tree,
        node=initial,
        previous_node=None,
        action=None,
        data={},
    )

    manifest = json.loads(initial.semantic_records_path.read_text(encoding="utf-8"))
    record_types = [item["record_type"] for item in manifest["records"]]
    assert record_types.count("match_proposal") == 2
    assert record_types.count("recognition_account") == 2
    assert record_types.count("evidence") > 0
    assert len(semantic_store.values("match_proposals")) == 2
    assert all(
        account.stored_identity_id is None
        for account in semantic_store.values("recognition_accounts")
    )
    readme = initial.readme_path.read_text(encoding="utf-8")
    assert "unresolved candidate" in readme
    assert "advisory similarity" in readme
    assert "evidence record(s)" in readme
    assert "rival(s)" in readme

    replayed = ActionTreeSemanticReplay().replay(
        tree.level_root,
        SymbolicStore(InMemorySemanticBackend()),
    )
    assert len(replayed.values("observations")) == 1
    assert len(replayed.values("encounters")) == 2
    assert len(replayed.values("match_proposals")) == 2
    assert len(replayed.values("recognition_accounts")) == 2
    assert len(replayed.values("evidence")) == record_types.count("evidence")
    assert replayed.encounters.deterministic_hash() == SymbolicStore(
        InMemorySemanticBackend()
    ).replay(replayed.snapshot()).encounters.deterministic_hash()


def test_live_capture_exposes_and_persists_explicit_registry_authorization(tmp_path: Path) -> None:
    tree = ActionTreeStore(tmp_path / "tree", "game", 1)
    initial = tree.create_initial(b"initial", {"state": "active"})
    initial.objects_path.write_text(
        "new_object_identity(known_shape, object, 'known shape').\n",
        encoding="utf-8",
    )
    tree.update_registry_from_objects(initial)
    semantic_store = SymbolicStore(InMemorySemanticBackend())
    semantic_store.put_encounter(
        EncounterRecord.create(
            observation_id="known-observation",
            action_tree_node="known-node",
            object_identity_id="known_shape",
            instance=InstanceParameters(
                appearance={"color": "blue", "shape": "rectangle"},
                supported_transformations=("translation",),
            ),
        )
    )
    memory = SymbolicMemory()
    writer = SingleWriter(memory)
    observer = SemanticGridCaptureObserver(
        GridAdapter(analyze_grid, PythonProvider({})),
        grid_selector=lambda runner: runner.grid,
        symbolic_store=semantic_store,
        identity_writer=writer,
    )

    observer.on_state_captured(
        runner=SimpleNamespace(grid=DEFAULT_GRID),
        store=tree,
        node=initial,
        previous_node=None,
        action=None,
        data={},
    )

    assert observer.authorization_options()["obj_blue_1"] == ("known_shape",)
    account = observer.authorize_candidate(
        candidate_id="obj_blue_1",
        selected_identity_id="known_shape",
        decision_id="human-selection-1",
    )
    assert account.stored_identity_id == "known_shape"
    assert account.decision_source == "explicit_registry_selection"
    assert memory.get("known_shape").payload == {
        "authority": "action_tree_registry"
    }
    assert "obj_blue_1" not in observer.authorization_options()
    assert memory.evidence_for("known_shape")
    history = tree.semantic_identity_decisions_path.read_text(encoding="utf-8")
    assert "human-selection-1" in history and "accepted" in history
    manifest = json.loads(initial.semantic_records_path.read_text(encoding="utf-8"))
    assert any(
        item["record_type"] == "recognition_account"
        and item["record_id"] == account.account_id
        for item in manifest["records"]
    )
    assert "explicit_registry_selection" in initial.readme_path.read_text(encoding="utf-8")


def test_semantic_capture_rehydrates_calibrated_identity_after_restart(
    tmp_path: Path,
) -> None:
    tree = ActionTreeStore(tmp_path / "tree", "game", 1)
    initial = tree.create_initial(b"initial", {"state": "active"})
    initial.objects_path.write_text(
        "new_object_identity(known_shape, object, 'known shape').\n",
        encoding="utf-8",
    )
    tree.update_registry_from_objects(initial)
    semantic_store = SymbolicStore(InMemorySemanticBackend())
    semantic_store.put_encounter(
        EncounterRecord.create(
            observation_id="known-observation",
            action_tree_node="known-node",
            object_identity_id="known_shape",
            instance=InstanceParameters(
                appearance={"color": "blue", "shape": "rectangle"},
                supported_transformations=("translation",),
            ),
        )
    )
    first_memory = SymbolicMemory()
    first = SemanticGridCaptureObserver(
        GridAdapter(analyze_grid, PythonProvider({})),
        grid_selector=lambda runner: runner.grid,
        symbolic_store=semantic_store,
        identity_writer=SingleWriter(first_memory),
    )
    first.on_state_captured(
        runner=SimpleNamespace(grid=DEFAULT_GRID),
        store=tree,
        node=initial,
        previous_node=None,
        action=None,
        data={},
    )
    account = first.authorize_candidate(
        candidate_id="obj_blue_1",
        selected_identity_id="known_shape",
        decision_id="before-restart",
    )
    assert account.calibrated_confidence > 0.0

    restarted_memory = SymbolicMemory()
    restarted = SemanticGridCaptureObserver(
        GridAdapter(analyze_grid, PythonProvider({})),
        grid_selector=lambda runner: runner.grid,
        identity_writer=SingleWriter(restarted_memory),
    )
    restarted._load_level_history(tree)

    restored = restarted_memory.get("known_shape")
    assert restored is not None
    assert restored.confidence == account.calibrated_confidence
    assert {
        item.evidence_id for item in restarted_memory.evidence_for("known_shape")
    } == set(account.supporting_evidence_ids + account.contradicting_evidence_ids)


def test_semantic_capture_hands_real_state_and_transition_to_learner(
    tmp_path: Path,
) -> None:
    class RecordingLearner:
        def __init__(self) -> None:
            self.states = []
            self.transitions = []

        def consume_state(self, payload):
            self.states.append(payload)
            return {"kind": "state", "state_id": payload.state_id}

        def consume_transition(self, before, action, after):
            self.transitions.append((before, action, after))
            return {
                "kind": "transition",
                "before": before.state_id,
                "after": after.state_id,
            }

    tree = ActionTreeStore(tmp_path / "tree", "game", 1)
    initial = tree.create_initial(b"initial", {"state": "active"})
    learner = RecordingLearner()
    observer = SemanticGridCaptureObserver(
        GridAdapter(analyze_grid, PythonProvider({})),
        grid_selector=lambda runner: runner.grid,
        learner_plugin=learner,
    )
    runner = SimpleNamespace(grid=DEFAULT_GRID)
    observer.on_state_captured(
        runner=runner,
        store=tree,
        node=initial,
        previous_node=None,
        action=None,
        data={},
    )
    child = tree.create_transition(initial, "RIGHT", {}, b"child", {"state": "active"})
    observer.on_state_captured(
        runner=runner,
        store=tree,
        node=child,
        previous_node=initial,
        action="RIGHT",
        data={"speed": 1},
    )

    assert len(learner.states) == 1
    assert len(learner.transitions) == 1
    before, action, after = learner.transitions[0]
    assert before.observation_id == learner.states[0].observation_id
    assert action == {"action": "RIGHT", "data": {"speed": 1}}
    assert after.observation_id != before.observation_id
    assert after.objects and after.artifacts
    manifest = json.loads(child.semantic_records_path.read_text(encoding="utf-8"))
    learner_links = [
        item for item in manifest["records"] if item["record_type"] == "learner_result"
    ]
    assert len(learner_links) == 1
    assert (child.path / learner_links[0]["artifact"]).is_file()
