from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "workbench" / "frontend" / "src" / "components" / "LlmModelsEditor.tsx"
GENERIC_SOURCE = ROOT / "workbench" / "frontend" / "src" / "components" / "ResourceSourceEditor.tsx"
FILE_CONTROLS = ROOT / "workbench" / "frontend" / "src" / "components" / "WorkspaceResourceFileControls.tsx"


def test_new_backend_is_immediately_savable() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    assert "document,isNew:true" in source
    assert "dirty:Boolean(record.isNew)" in source
    assert "dirty:doc.dirty" in source
    assert "onSave:location=>saveDoc(doc,location)" in source


def test_model_resource_save_uses_shared_resource_file_controls() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    generic_source = GENERIC_SOURCE.read_text(encoding="utf-8")
    controls = FILE_CONTROLS.read_text(encoding="utf-8")
    assert "fileControls" in generic_source
    assert "WorkspaceResourceFileControls" in generic_source
    assert 'aria-label="Resource workspace"' in controls
    assert 'aria-label="Workspace-relative file path"' in controls
    assert '>Save To Workspace</button>' in controls
    assert '>Save To Other Workspace…</button>' in controls
    assert '>Reload From Origin</button>' in controls
    assert '>Load From Workspace…</button>' in controls
    assert "effectiveIncludes" in controls
    assert "Other libraries" in controls
    assert "Other workspaces" in controls
    assert "originWorkspaceId:doc.record.workspaceId||workspaceId" in source
    assert "targetWorkspaceId=location?.workspaceId||workspaceId" in source
    assert "/workbench/workspaces/${encodeURIComponent(targetWorkspaceId)}/file" in source
    assert "design/backends" in source
    assert "design/models" in source
    assert "design/systems" in source


def test_generic_control_orders_current_inherited_and_other_workspaces() -> None:
    controls = FILE_CONTROLS.read_text(encoding="utf-8")
    assert "currentWorkspaceId" in controls
    assert "inheritedIds" in controls
    assert "const libraries" in controls
    assert "const projects" in controls
    assert "Other locations" in controls


def test_backend_uses_derived_aggregate_editor_modes() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    assert '"file"|"resource"|"actions"|"runner"' in source
    assert '>File</button>' in source
    assert '>Resource &amp; Inheritance</button>' in source
    assert '>Backend Actions</button>' in source
    assert '>Universal Execution Runner</button>' in source
    assert "BackendConfigForm" in source
    assert "RESOLVED / INHERITED RESOURCE" in source
    assert 'operationIds={["backend_inspect","backend_check_readiness","resource_validate"]}' in source


def test_focused_model_resource_is_addressable_with_edit_query_parameter() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    assert 'parameters.get("edit")||parameters.get("resource")' in source
    assert 'url.searchParams.set("edit",focusedId)' in source
    assert 'window.history.replaceState({},"",url)' in source


def test_backend_resource_view_reveals_clear_edit_source_actions() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    assert 'backend-edit-source' in source
    assert 'backendEditorDisplayMode==="tabs"&&backendEditorMode==="file"?"Editing File":"Edit File"' in source


def test_backend_aggregate_is_semantically_a_tabbed_editor() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    assert 'role="tablist"' in source
    assert 'className="backend-tabs-label">EDITORS' in source
    assert source.count('role="tab" aria-selected=') == 4


def test_shared_file_controls_distinguish_storage_channels_and_reload_scope() -> None:
    controls = FILE_CONTROLS.read_text(encoding="utf-8")
    assert "WORKSPACE RESOURCE" in controls
    assert "Save To Workspace" in controls
    assert "Load From Workspace…" in controls
    assert "Reload From Origin" in controls
    assert "LOCAL DISK · NATIVE FILE" in controls
    assert "Reload Local File" in controls
    assert "CLIENT TRANSFER" in controls
    assert ">Upload<input" in controls
    assert ">Download</button>" in controls


def test_backend_resource_tab_exposes_enablement_action() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    assert 'className="backend-resource-status"' in source
    assert 'resourceEnabled?"Disable Backend":"Enable Backend"' in source
    assert 'setResourceEnabled(doc,document,!resourceEnabled)' in source


def test_backend_views_use_super_control_display_and_tab_set_controls() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    assert 'type ModelEditorDisplayMode="tabs"|"stacked"|"single"|"split-v"|"split-h"' in source
    assert 'aria-label="Model Super Control display mode"' in source
    assert 'aria-label="Model Super Control tab set"' in source
    assert '>ALL</button>' in source
    assert '>CTX</button>' in source
    assert "backend-view-mode" not in source
    assert ">↕ Stack</button>" not in source
    assert ">▣ Tabs</button>" not in source


def test_resource_and_inheritance_are_one_tab_with_restricted_reload_controls() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    controls = FILE_CONTROLS.read_text(encoding="utf-8")

    assert "Resource &amp; Inheritance" in source
    assert '>Inheritance</button>' not in source
    assert 'allowLoadDifferent:false' in source
    assert "Edit parent ·" in source
    assert "Reload From Origin" in controls
    assert "allowLoadDifferent &&" in controls
