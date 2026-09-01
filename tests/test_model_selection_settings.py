from __future__ import annotations

import asyncio
from pathlib import Path

import model_selection_settings
import system_control_api


def test_workspace_override_wins_over_forced_system_and_operation_model(
    tmp_path: Path,
    monkeypatch,
) -> None:
    system_path = tmp_path / "shared" / "policies" / "system.model_runtime_policy.json"
    monkeypatch.setattr(model_selection_settings, "SYSTEM_POLICY_PATH", system_path)
    workspace = tmp_path / "project"

    model_selection_settings.write_system_model_selection({
        "fallbackModelId": "global-model",
        "pervasive": True,
    })
    model_selection_settings.write_workspace_model_selection(workspace, {
        "overrideModelId": "workspace-model",
    })

    selected, source = model_selection_settings.effective_model_selection(
        workspace,
        {"models": ["operation-model"], "strategy": "single"},
    )
    assert selected == {"models": ["workspace-model"], "strategy": "workspace_override"}
    assert source == "workspace_override"


def test_system_model_can_be_forced_or_used_only_as_fallback(
    tmp_path: Path,
    monkeypatch,
) -> None:
    system_path = tmp_path / "shared" / "policies" / "system.model_runtime_policy.json"
    monkeypatch.setattr(model_selection_settings, "SYSTEM_POLICY_PATH", system_path)
    workspace = tmp_path / "project"
    requested = {"models": ["operation-model"], "strategy": "single"}

    model_selection_settings.write_system_model_selection({
        "fallbackModelId": "global-model",
        "pervasive": True,
    })
    selected, source = model_selection_settings.effective_model_selection(workspace, requested)
    assert selected == {"models": ["global-model"], "strategy": "system_forced"}
    assert source == "system_forced"

    model_selection_settings.write_system_model_selection({
        "fallbackModelId": "global-model",
        "pervasive": False,
    })
    assert model_selection_settings.effective_model_selection(workspace, requested) == (requested, "operation")
    assert model_selection_settings.effective_model_selection(workspace, {}) == (
        {"models": ["global-model"], "strategy": "system_fallback"},
        "system_fallback",
    )


def test_settings_and_workspace_overview_expose_model_selection_controls() -> None:
    source = Path("workbench/frontend/src/components/WorkspaceSettingsPanel.tsx").read_text(encoding="utf-8")
    assert "Global fallback and pervasive model" in source
    assert "Pervasive — always use this model" in source
    assert 'aria-label="Pervasive model selection"' in source
    assert "Workspace model override" in source
    assert "A workspace override has the highest priority" in source
    assert 'aria-label={mode==="settings"?"Global fallback model":"Workspace model override"}' in source


def test_workspace_selection_can_skip_model_enumeration(
    tmp_path: Path,
    monkeypatch,
) -> None:
    workspace_root = tmp_path / "workspaces" / "project"
    workspace_root.mkdir(parents=True)
    monkeypatch.setattr(system_control_api, "WORKSPACES_ROOT", tmp_path / "workspaces")
    monkeypatch.setattr(system_control_api, "workspace_model_selection", lambda _root: {"overrideModelId": "inherited-model"})
    monkeypatch.setattr(system_control_api, "system_model_selection", lambda: {"fallbackModelId": "fallback-model"})
    monkeypatch.setattr(
        system_control_api,
        "effective_model_selection",
        lambda _root, _requested: ({"models": ["inherited-model"], "strategy": "workspace_override"}, "workspace_override"),
    )
    monkeypatch.setattr(
        system_control_api,
        "_model_choices",
        lambda _root: (_ for _ in ()).throw(AssertionError("model enumeration should be skipped")),
    )

    payload = asyncio.run(
        system_control_api.get_workspace_model_selection("project", include_models=False)
    )

    assert payload["effective"] == {"models": ["inherited-model"], "strategy": "workspace_override"}
    assert payload["source"] == "workspace_override"
    assert payload["models"] == []


def test_model_choices_identify_and_order_inherited_workspace_layers(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(system_control_api, "resolve_model_records", lambda _root: [
        {"source": "shared", "workspaceId": "shared_library_system", "document": {"id": "shared-model", "label": "A shared"}, "resolved": {"enabled": True, "backendId": "shared"}},
        {"source": "workspace", "workspaceId": "project", "document": {"id": "local-model", "label": "Z local"}, "resolved": {"enabled": True, "backendId": "local"}},
        {"source": "included", "workspaceId": "team-library", "document": {"id": "team-model", "label": "B team"}, "resolved": {"enabled": True, "backendId": "team"}},
        {"source": "shared", "workspaceId": "shared_library_system", "document": {"id": "disabled-vision", "label": "Vision", "capabilities": {"vision": True}}, "resolved": {"enabled": False, "backendId": "vision"}},
    ])

    choices = system_control_api._model_choices(tmp_path / "project")

    assert [choice["id"] for choice in choices] == ["local-model", "team-model", "shared-model"]
    assert choices[0]["inherited"] is False
    assert choices[1]["inherited"] is True
    assert choices[1]["workspaceId"] == "team-library"
    all_choices = system_control_api._model_choices(tmp_path / "project", include_disabled=True)
    disabled = next(choice for choice in all_choices if choice["id"] == "disabled-vision")
    assert disabled["enabled"] is False
    assert disabled["capabilities"] == {"vision": True}
