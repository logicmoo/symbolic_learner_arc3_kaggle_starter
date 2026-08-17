import json
from pathlib import Path
from types import SimpleNamespace

from action_tree import ActionTreeStore
from object_memory import (
    ActionTreeSemanticReplay,
    GridAdapter,
    InMemorySemanticBackend,
    PythonProvider,
    SemanticGridCaptureObserver,
    SymbolicStore,
)
from workbench.server.runtime import analyze_grid


def test_live_capture_persists_evidence_backed_transition_changes(tmp_path: Path) -> None:
    before = [
        [0, 2, 2, 0, 3],
        [0, 2, 2, 0, 3],
        [0, 0, 0, 0, 0],
    ]
    after = [
        [0, 0, 0, 3, 3],
        [0, 2, 2, 0, 0],
        [0, 2, 2, 0, 0],
    ]
    tree = ActionTreeStore(tmp_path / "tree", "game", 1)
    initial = tree.create_initial(b"initial", {"state": "active"})
    observer = SemanticGridCaptureObserver(
        GridAdapter(analyze_grid, PythonProvider({})),
        grid_selector=lambda runner: runner.grid,
    )
    observer.on_state_captured(
        runner=SimpleNamespace(grid=before),
        store=tree,
        node=initial,
        previous_node=None,
        action=None,
        data={},
    )
    child = tree.create_transition(initial, "RIGHT", {}, b"after", {"state": "active"})
    observer.on_state_captured(
        runner=SimpleNamespace(grid=after),
        store=tree,
        node=child,
        previous_node=initial,
        action="RIGHT",
        data={},
    )

    manifest = json.loads(child.semantic_records_path.read_text(encoding="utf-8"))
    record_types = [item["record_type"] for item in manifest["records"]]
    assert record_types.count("object_change") >= 2
    changes = observer.symbolic_store.values("object_changes")
    assert {item.kind for item in changes} >= {"moved"}
    assert all(item.evidence_ids for item in changes if item.kind == "moved")
    residuals = observer.symbolic_store.values("residuals")
    assert residuals
    assert record_types.count("residual") == len(residuals)
    readme = child.readme_path.read_text(encoding="utf-8")
    assert "`moved` from" in readme
    assert "`provisional` residual" in readme

    replayed = ActionTreeSemanticReplay().replay(
        tree.level_root,
        SymbolicStore(InMemorySemanticBackend()),
    )
    assert {item.change_id: item for item in replayed.values("object_changes")} == {
        item.change_id: item for item in changes
    }
    assert replayed.values("residuals") == residuals
