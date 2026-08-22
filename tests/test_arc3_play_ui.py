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
    assert "START SESSION" in source
    assert "playing from here" in source
    assert "auto save (switched to" in source
    assert "Duplicate" in source
    assert "Delete" in source
    assert "auto-CLICK" in source
    assert "RECORDINGS" in source
    assert "importRecording" in source
    assert "arc3-play-col-resizer" in source
    assert "take-back-move" in source
    assert "step one move" in source
    assert "Watch replay" in source
    assert "replayPlaying" in source
    assert "arc3-play-timeline" in source
    assert "chapterStarts" in source
    assert "seekReplay" in source
    assert "dedupeSavepoints" in source
    assert "dedupeRecordings" in source
    assert "MOVE AS SETUP" in source
    assert "loadMoveScan" in source
    assert "Rescan" in source
    assert "data/importables" in source
    api_source = API.read_text(encoding="utf-8")
    assert "delete_savepoint" in api_source
    assert "duplicate_savepoint" in api_source
    assert "auto save (latest)" in api_source
    assert "_autosave" in api_source
    assert "import_recording" in api_source
    assert "list_recordings" in api_source
    assert "dedupe_savepoints" in api_source
    assert "dedupe_recordings" in api_source
    assert "_purge_prior_import" in api_source
    assert "_scan_setup_dir" in api_source
    assert "_import_release_run" in api_source
    assert "release-runs" in api_source
    assert "_parse_transcript_actions" in api_source
    assert "_load_trace_playbook_snapshots" in api_source
    assert "commentary.md" in api_source
    assert "vision_prime.md" in api_source
    assert '"scan": _scan_setup_dir(directory, self.workspace_root)' in api_source
    assert '"scan": _scan_setup_dir(directory, root)' in api_source
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


def test_play_page_right_column_panels_cleanup() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # Panels renamed + independently collapsible.
    assert "RESTART-POINTS" in source
    assert "IMPORTABLES" in source
    assert "arc3-play-collapse-toggle" in source
    assert "toggleSection" in source
    assert "collapsedSections" in source
    # Header game picker replaces the old left-column ARC3 GAMES list.
    assert "arc3-play-game-picker" in source
    assert "selectedGameId" in source
    assert '"Filter: ON" : "Filter"' in source
    assert "Start new game" in source
    assert "filterGameId" in source
    assert "filteredSavepoints" in source
    assert "sortedRecordings" in source
    # Per-move expand/collapse "Move as Setup" disclosure.
    assert "arc3-play-move-expand" in source
    assert "toggleMoveExpand" in source
    assert "scanMoveDir" in source
    styles = STYLES.read_text(encoding="utf-8")
    assert ".arc3-play-game-picker" in styles
    assert ".arc3-play-collapse-toggle" in styles
    assert ".arc3-play-move-expand" in styles


def test_play_page_moves_ordered_numerically_and_importables_sorted() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # Moves are sorted by (level order, numeric index) before being reversed
    # for "newest first" display, instead of relying on raw array order.
    assert "movesNumeric" in source
    assert "levelDirRank" in source
    assert "a.index - b.index" in source
    # IMPORTABLES list is sorted by game then name, not left in scan order.
    assert "sortedRecordings" in source
    assert "localeCompare" in source


def test_play_router_is_mounted() -> None:
    source = APP.read_text(encoding="utf-8")
    assert "from arc3_play_api import router as arc3_play_router" in source
    assert 'app.include_router(arc3_play_router, prefix="/api")' in source
