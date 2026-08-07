import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
sys.path.insert(0, str(SERVER))

from policy_library import load_workspace_policy_records, policy_hierarchy  # noqa: E402


def test_shared_policy_directory_loads_real_resources() -> None:
    shared = ROOT / "workbench" / "workspaces" / "shared"
    records = load_workspace_policy_records(shared)
    hierarchy = policy_hierarchy(records)
    assert len(records) == 10
    assert {row["document"]["kind"] for row in records} >= {"model_policy", "model_policy_variant", "vendor_policy", "benchmark_policy"}
    assert len(hierarchy["variantsByParent"]["default_model_runtime"]) == 2


def test_workspace_policy_overrides_shared_id(tmp_path: Path) -> None:
    shared = tmp_path / "shared" / "policies"
    local = tmp_path / "demo" / "policies"
    shared.mkdir(parents=True); local.mkdir(parents=True)
    base = {"kind":"model_policy","id":"policy","label":"Shared","enabled":True}
    (shared / "policy.model_policy.json").write_text(json.dumps(base), encoding="utf-8")
    (local / "policy.model_policy.json").write_text(json.dumps({**base,"label":"Workspace"}), encoding="utf-8")
    records = load_workspace_policy_records(tmp_path / "demo", workspaces_root=tmp_path)
    assert records[0]["source"] == "workspace"
    assert records[0]["document"]["label"] == "Workspace"


def test_design_policy_navigation_uses_rich_editor() -> None:
    page = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    editor = (ROOT / "workbench" / "frontend" / "src" / "components" / "PolicyLibraryEditor.tsx").read_text(encoding="utf-8")
    assert 'label:"Policy",view:"policies"' in page
    assert 'view==="policies"&&<PolicyLibraryEditor' in page
    for token in ("HierarchyResourceEditor", "Split view", "raw-json-editor", "ENABLED", "/policies"):
        assert token in editor
