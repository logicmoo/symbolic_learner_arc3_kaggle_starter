from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "workbench" / "frontend" / "src"


def test_user_ui_preference_is_personal_and_browser_persisted():
    source = (FRONTEND / "lib" / "uiPreferences.ts").read_text(encoding="utf-8")
    assert "metta-workbench.user-ui-preferences.v1" in source
    assert "localStorage" in source
    assert "workbench:user-ui-preferences-changed" in source
    assert 'resourceSourceFileControlsPlacement: "above"' in source


def test_settings_page_exposes_resource_source_control_placement():
    source = (FRONTEND / "components" / "WorkspaceSettingsPanel.tsx").read_text(encoding="utf-8")
    assert "USER / UI SETTINGS" in source
    assert "workspace opening choices resolving through the workspace inheritance chain" in source
    assert "Resource Source save and load controls placement" in source
    assert "Above the editor text area" in source
    assert "Below the editor text area" in source


def test_resource_source_editor_places_controls_from_shared_preference():
    source = (FRONTEND / "components" / "ResourceSourceEditor.tsx").read_text(encoding="utf-8")
    assert "useUserUiPreferences" in source
    assert 'resourceSourceFileControlsPlacement === "above"' in source
    assert 'resourceSourceFileControlsPlacement === "below"' in source
    assert "renderedFileControls" in source
