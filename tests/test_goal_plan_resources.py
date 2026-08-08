from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
if str(SERVER) not in sys.path:
    sys.path.insert(0, str(SERVER))

from goal_plan_library import load_workspace_symbolic_records, symbolic_hierarchy
from resource_convention import canonical_resource_path


def _write(root: Path, workspace: str, directory: str, name: str, document: str) -> None:
    target = root / workspace / directory / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(document, encoding="utf-8")


def test_goal_resources_inherit_shared_and_allow_workspace_overrides(tmp_path: Path) -> None:
    _write(tmp_path, "shared", "goals", "learn.goal.json", '{"kind":"goal","id":"learn","label":"Shared"}')
    _write(tmp_path, "shared", "goals", "safe.goal_variant.json", '{"kind":"goal_variant","id":"safe","parents":["learn"]}')
    _write(tmp_path, "project", "goals", "learn.goal.json", '{"kind":"goal","id":"learn","label":"Override"}')
    records = load_workspace_symbolic_records(tmp_path / "project", "goal", workspaces_root=tmp_path)
    by_id = {record["document"]["id"]: record for record in records}
    assert by_id["learn"]["source"] == "workspace"
    assert by_id["learn"]["document"]["label"] == "Override"
    assert by_id["safe"]["source"] == "shared"
    hierarchy = symbolic_hierarchy(records, "goal")
    assert hierarchy["variantsBySpecification"]["learn"][0]["document"]["id"] == "safe"


def test_plan_variant_requires_parent_and_canonical_suffix(tmp_path: Path) -> None:
    _write(tmp_path, "shared", "plans", "broken.plan_variant.json", '{"kind":"plan_variant","id":"broken"}')
    records = load_workspace_symbolic_records(tmp_path / "shared", "plan", workspaces_root=tmp_path)
    assert "Variant requires parents" in records[0]["error"]
    path = canonical_resource_path(Path("plans/draft.json"), {"kind": "plan_variant", "id": "route.fast", "parents": ["route"]})
    assert path.as_posix() == "plans/route.fast.plan_variant.json"


def test_shared_workspace_contains_goal_and_plan_examples() -> None:
    shared = ROOT / "workbench" / "workspaces" / "shared"
    goals = load_workspace_symbolic_records(shared, "goal")
    plans = load_workspace_symbolic_records(shared, "plan")
    assert {record["document"]["kind"] for record in goals} == {"goal", "goal_variant"}
    assert {record["document"]["kind"] for record in plans} == {"plan", "plan_variant"}


def test_shared_workspace_contains_bidirectional_context_examples() -> None:
    shared = ROOT / "workbench" / "workspaces" / "shared"
    contexts = load_workspace_symbolic_records(shared, "context")
    by_id = {record["document"]["id"]: record["document"] for record in contexts}
    assert {document["kind"] for document in by_id.values()} == {"context", "context_variant"}
    assert by_id["arc3_analysis"]["children"] == ["arc3_analysis.default"]
    assert by_id["arc3_analysis.default"]["parents"] == ["arc3_analysis"]


def test_goal_plan_editor_preserves_rich_hierarchy_features() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "components" / "GoalPlanLibraryEditor.tsx").read_text(encoding="utf-8")
    for token in ("HierarchyResourceEditor", "PREFERRED VARIANT", "Split view", "+ Alternative", "+ Abstract", "raw-json-editor", "preferredChild"):
        assert token in source


def test_goal_plan_and_context_pages_load_their_shared_right_panel_docs() -> None:
    components = ROOT / "workbench" / "frontend" / "src" / "components"
    help_source = (components / "HelpDocumentTabs.tsx").read_text(encoding="utf-8")
    page_source = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    assert '{id:"goals",label:"Goals",path:"docs/goals.md"}' in help_source
    assert '{id:"plans",label:"Plans",path:"docs/plans.md"}' in help_source
    assert '{id:"contexts",label:"Contexts",path:"docs/contexts.md"}' in help_source
    assert 'ReactMarkdown' in help_source
    assert 'remarkGfm' in help_source
    assert '<pre className="mini-code relationship-markdown">' not in help_source
    assert 'view==="goals"?"goals":view==="plans"?"plans"' in page_source
    assert 'view==="goals"||view==="plans"' in page_source
    assert (ROOT / "workbench" / "workspaces" / "shared" / "docs" / "goals.md").is_file()
    assert (ROOT / "workbench" / "workspaces" / "shared" / "docs" / "plans.md").is_file()
    assert (ROOT / "workbench" / "workspaces" / "shared" / "docs" / "contexts.md").is_file()
