from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "workbench/frontend/src/components/Arc3PlayPage.tsx"
STYLES = ROOT / "workbench/frontend/src/styles/arc3_play.css"
WORKBENCH = ROOT / "workbench/frontend/src/pages/FilesystemWorkbenchPage.tsx"
PAGE = ROOT / "workbench/workspaces/arc3_random_player/design/workflow_pages/arc3_play.workflow_page.json"
API = ROOT / "workbench/server/arc3_play_api.py"
APP = ROOT / "workbench/server/app.py"


def test_play_page_uses_dedicated_renderer() -> None:
    source = PAGE.read_text(encoding="utf-8")
    assert '"routeView": "arc3Play"' in source
    assert '"renderer": "arc3_play"' in source


def test_play_renderer_is_wired_in_workbench() -> None:
    source = WORKBENCH.read_text(encoding="utf-8")
    assert 'workflowPageForView.renderer === "arc3_play"' in source
    assert 'import("../components/Arc3PlayPage")' in source
    assert "default: module.Arc3PlayPage," in source
    assert "<Arc3PlayPage" in source
    assert '"arc3Play"' in source  # View union + WORKBENCH_VIEWS entry


def test_play_component_has_recorder_contract() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    assert "export function Arc3PlayPage(" in source
    assert "/arc3-play/games" in source
    assert "/arc3-play/sessions" in source
    assert "levelDir" in source
    assert "New attempt" in source
    assert "Restart game" in source
    assert "Rewind {count} move" in source
    assert "arc3-play-rewind-menu" in source
    assert "back to level start" in source
    assert "will-undo" in source
    assert "rewind-target" in source
    assert "Click to rewind here" in source
    assert "actionShort" in source
    assert "Fork" in source
    assert "Resume" in source
    assert "End session" in source
    styles = STYLES.read_text(encoding="utf-8")
    assert ".arc3-play" in styles


def test_play_api_records_flat_move_dirs() -> None:
    source = API.read_text(encoding="utf-8")
    # Stamped level dirs: level_<n>_<datetime>_<epoch ns> so parallel threads never collide.
    assert 'f"level_{' in source
    assert "time.time_ns()" in source
    # Flat ordinal move dirs 0/ 1/ 2/ under the stamped level dir.
    assert "self.level_dir / str(ordinal)" in source
    assert "recording.json" in source
    assert "image.png" in source
    assert "state.json" in source
    # Runner's own action tree stays out of data/.
    assert "play_action_trees" in source


def test_play_api_supports_undo_and_restart() -> None:
    source = API.read_text(encoding="utf-8")
    # Artificial undo: reset the level and deterministically replay all
    # moves except the last, rewinding into the previous move dir.
    assert '"/sessions/{session_id}/undo"' in source
    assert "replay_verified" in source
    assert "shutil.rmtree" in source
    # Full game restart back to level 1.
    assert '"/sessions/{session_id}/restart"' in source
    assert "restart_game" in source


def test_play_api_supports_fork_savepoints() -> None:
    source = API.read_text(encoding="utf-8")
    # Fork = non-disruptive save-point in the per-game log, replayable later.
    assert '"/sessions/{session_id}/fork"' in source
    assert '"/savepoints"' in source
    assert "savepoints.json" in source
    assert "replay_log" in source
    assert "def replay_recipe" in source
    assert "savepointId" in source


def test_play_router_is_mounted() -> None:
    source = APP.read_text(encoding="utf-8")
    assert "from arc3_play_api import router as arc3_play_router" in source
    assert 'app.include_router(arc3_play_router, prefix="/api")' in source
