from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

try:
    from _runtime import configure_runtime_home
except ModuleNotFoundError:  # Imported as scripts.phase2_object_memory_demo in tests.
    from scripts._runtime import configure_runtime_home

configure_runtime_home(__file__)

from action_tree import ActionTreeStore
from object_memory import (
    ActionTreeSemanticReplay,
    EncounterRecord,
    GridAdapter,
    InMemorySemanticBackend,
    InstanceParameters,
    PythonProvider,
    SemanticGridCaptureObserver,
    SingleWriter,
    SymbolicMemory,
    SymbolicStore,
)
from workbench.server.runtime import DEFAULT_GRID, analyze_grid


AFTER_GRID = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 2, 0, 0],
    [0, 0, 1, 0, 1, 2, 0, 0],
    [0, 0, 1, 1, 1, 2, 2, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]


def _capture(
    observer: SemanticGridCaptureObserver,
    tree: ActionTreeStore,
    node: Any,
    *,
    previous_node: Any = None,
    action: str | None = None,
    grid: Any = DEFAULT_GRID,
) -> None:
    observer.on_state_captured(
        runner=SimpleNamespace(grid=grid),
        store=tree,
        node=node,
        previous_node=previous_node,
        action=action,
        data={},
    )


def run_demo(output_root: Path) -> dict[str, Any]:
    """Run the deterministic Phase 2 path and return its inspectable evidence."""

    output_root = output_root.expanduser().resolve()
    tree = ActionTreeStore(output_root / "action_trees", "phase2_demo", 1)
    initial = tree.create_initial(b"phase2-demo-initial", {"state": "active"})
    initial.objects_path.write_text(
        "new_object_identity(known_shape, object, 'known shape').\n",
        encoding="utf-8",
    )
    tree.update_registry_from_objects(initial)

    semantic_store = SymbolicStore(InMemorySemanticBackend())
    semantic_store.put_encounter(
        EncounterRecord.create(
            observation_id="fixture-known-observation",
            action_tree_node="fixture-known-node",
            object_identity_id="known_shape",
            instance=InstanceParameters(
                appearance={"color": "blue", "shape": "rectangle"},
                supported_transformations=("translation", "recolor"),
            ),
        )
    )
    memory = SymbolicMemory()
    observer = SemanticGridCaptureObserver(
        GridAdapter(analyze_grid, PythonProvider({})),
        grid_selector=lambda runner: runner.grid,
        symbolic_store=semantic_store,
        identity_writer=SingleWriter(memory),
    )

    _capture(observer, tree, initial)
    first_candidate = next(
        candidate_id
        for candidate_id, identities in observer.authorization_options().items()
        if "known_shape" in identities
    )
    observer.authorize_candidate(
        candidate_id=first_candidate,
        selected_identity_id="known_shape",
        decision_id="phase2-demo-initial-authorization",
    )

    child = tree.create_transition(
        initial,
        "RIGHT",
        {},
        b"phase2-demo-after",
        {"state": "active"},
    )
    _capture(
        observer,
        tree,
        child,
        previous_node=initial,
        action="RIGHT",
        grid=AFTER_GRID,
    )
    second_options = observer.authorization_options()
    if first_candidate in second_options and "known_shape" in second_options[first_candidate]:
        observer.authorize_candidate(
            candidate_id=first_candidate,
            selected_identity_id="known_shape",
            decision_id="phase2-demo-later-authorization",
        )

    replayed = ActionTreeSemanticReplay().replay(
        tree.level_root,
        SymbolicStore(InMemorySemanticBackend()),
    )
    encounters = replayed.encounters.records()
    reconstruction_fits = tuple(
        turtle.fit_score
        for encounter in encounters
        for turtle in encounter.turtle_programs
        if turtle.fit_score is not None
    )
    resolved_accounts = tuple(
        account
        for account in replayed.values("recognition_accounts")
        if account.stored_identity_id is not None
    )
    summary = {
        "action_tree": str(tree.level_root),
        "observations": len(replayed.values("observations")),
        "encounters": len(encounters),
        "turtle_programs": sum(len(item.turtle_programs) for item in encounters),
        "exact_reconstructions": sum(score == 1.0 for score in reconstruction_fits),
        "match_proposals": len(replayed.values("match_proposals")),
        "evidence_records": len(replayed.values("evidence")),
        "resolved_accounts": len(resolved_accounts),
        "recognized_identity": (
            resolved_accounts[-1].stored_identity_id if resolved_accounts else None
        ),
        "object_changes": sorted(
            {change.kind for change in replayed.values("object_changes")}
        ),
        "replay_hash": replayed.encounters.deterministic_hash(),
    }
    summary_path = output_root / "phase2_demo_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summary["summary"] = str(summary_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the reproducible Phase 2 object-memory demonstration."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("runtime") / "phase2_object_memory_demo",
    )
    args = parser.parse_args()
    print(json.dumps(run_demo(args.output), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
