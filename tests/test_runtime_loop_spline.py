from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx"
STYLES = ROOT / "workbench" / "frontend" / "src" / "styles" / "workbench.css"


def test_runtime_topology_projects_declared_while_edges_and_persisted_iterations() -> None:
    source = HISTORY.read_text(encoding="utf-8")

    assert "declaredWhileEdges" in source
    assert 'event.kind !== "loop.iteration"' in source
    assert "executedIterations" in source
    assert "WHILE · {edge.executedIterations}/{edge.maxIterations}" in source
    assert "loop.targetStepId || step.id" in source


def test_declared_and_inferred_loop_edges_are_visually_distinct() -> None:
    styles = STYLES.read_text(encoding="utf-8")

    assert ".run-topology-loop-edge.declared" in styles
    assert ".run-topology-loop-label.declared" in styles


def test_chronology_has_connected_accessible_step_event_nodes() -> None:
    source = HISTORY.read_text(encoding="utf-8")
    styles = STYLES.read_text(encoding="utf-8")

    assert "chronologyPoints.slice(1)" in source
    assert 'className="run-chronology-edge"' in source
    assert 'role={selectable ? "button" : undefined}' in source
    assert "setMemoryStepId(event.stepId)" in source
    assert 'event.stepId === focalStepId ? "selected"' in source
    assert ".run-chronology-node.selected circle" in styles
