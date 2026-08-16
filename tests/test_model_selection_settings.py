from __future__ import annotations

from pathlib import Path

import model_selection_settings


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
