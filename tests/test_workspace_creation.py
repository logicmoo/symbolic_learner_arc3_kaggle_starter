from pathlib import Path

import pytest
from fastapi import HTTPException

import workspace_api


def test_create_workspace_copies_current_default_template(tmp_path: Path, monkeypatch) -> None:
    shared = tmp_path / "shared"
    default = tmp_path / "default"
    shared.mkdir()
    (default / "workflows").mkdir(parents=True)
    starter = default / "workflows" / "starter.workflow.json"
    starter.write_text('{"kind":"workflow","id":"starter","steps":[]}', encoding="utf-8")
    monkeypatch.setattr(workspace_api, "_workspace_roots", lambda: [tmp_path])

    result = workspace_api.create_workspace({"label": "Vision Lab"})

    created = tmp_path / "vision_lab"
    assert result["templateWorkspaceId"] == "default"
    assert result["workspace"]["id"] == "vision_lab"
    assert (created / "workflows" / starter.name).read_text(encoding="utf-8") == starter.read_text(encoding="utf-8")
    assert result["workspace"]["includes"] == [{"workspaceId": "shared", "includeInherited": True}]


def test_create_workspace_never_overwrites_an_existing_directory(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "shared").mkdir()
    (tmp_path / "default").mkdir()
    (tmp_path / "vision_lab").mkdir()
    marker = tmp_path / "vision_lab" / "keep.txt"
    marker.write_text("keep", encoding="utf-8")
    monkeypatch.setattr(workspace_api, "_workspace_roots", lambda: [tmp_path])

    with pytest.raises(HTTPException) as error:
        workspace_api.create_workspace({"label": "Vision Lab"})

    assert error.value.status_code == 409
    assert marker.read_text(encoding="utf-8") == "keep"


def test_create_workspace_can_copy_another_workspace(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "shared").mkdir()
    (tmp_path / "default").mkdir()
    source = tmp_path / "vision_library"
    (source / "models").mkdir(parents=True)
    (source / "models" / "vision.model.json").write_text('{"kind":"model","id":"vision"}', encoding="utf-8")
    (source / "workspace.json").write_text('{"label":"Vision Library","includes":[]}', encoding="utf-8")
    monkeypatch.setattr(workspace_api, "_workspace_roots", lambda: [tmp_path])

    result = workspace_api.create_workspace({"label": "Experiment", "templateWorkspaceId": "vision_library"})

    assert result["templateWorkspaceId"] == "vision_library"
    assert (tmp_path / "experiment" / "models" / "vision.model.json").is_file()
    assert result["workspace"]["includes"] == []


def test_workspace_picker_explains_template_and_library_roles() -> None:
    source = (Path(__file__).resolve().parents[1] / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    assert "Create A New Workspace" in source
    assert "Create Workspace" in source
    assert 'setNewWorkspaceTemplateId("default")' in source
    assert "Workspace template" in source
    assert 'request("/api/workspaces",{method:"POST"' in source
    assert "EDITABLE STARTER TEMPLATE" in source
    assert "Default is preselected" in source
    assert "independent copy" in source
