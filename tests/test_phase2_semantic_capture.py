import json
from pathlib import Path
from types import SimpleNamespace

from action_tree import ActionTreeStore
from object_memory import GridAdapter, PythonProvider, SemanticGridCaptureObserver
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
