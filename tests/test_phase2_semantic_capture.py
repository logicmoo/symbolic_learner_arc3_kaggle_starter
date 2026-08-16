import json
from pathlib import Path
from types import SimpleNamespace

from action_tree import ActionTreeStore
from object_memory import (
    EncounterRecord,
    GridAdapter,
    InMemorySemanticBackend,
    InstanceParameters,
    PythonProvider,
    SemanticGridCaptureObserver,
    SymbolicStore,
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
    assert [item["record_type"] for item in child_manifest["records"]].count("encounter") == 2
    assert len(tuple((initial.path / "semantic").glob("*.turtle.pl"))) == 2
    encounters = observer.symbolic_store.encounters.records()
    assert len(encounters) == 4
    assert encounters[2].previous_encounter_id == encounters[0].encounter_id
    assert encounters[3].previous_encounter_id == encounters[1].encounter_id
    assert "## Semantic records" in child.readme_path.read_text(encoding="utf-8")


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
