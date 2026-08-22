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
    assert "Restart Level" in source
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
    # Ranked saved dirs: saved_<NNN>, game-wide, continuing from the highest
    # existing rank under data/Recordings/<game>/ (0-padded, 001-first).
    assert 'f"saved_{' in source
    assert "_next_ranked_saved_dir_name" in source
    assert "_RANKED_SAVED_DIR_RE" in source
    # Live recordings + imports all write under the canonical Recordings/
    # location, not the legacy data/<game>/ path.
    assert "_games_container" in source
    assert "_game_write_dir" in source
    assert '_game_write_dir(self.workspace_root, self.game_dir)' in source
    # Flat ordinal move dirs 0/ 1/ 2/ under the level dir.
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
    assert "MOVE-LISTS" in source
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


def test_play_page_embeds_b1b2_runner_stack_in_left_column() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    assert 'import { Arc3B1B2PipelinePage, type ModelChoice, type WorkspaceFileRecord } from "./Arc3B1B2PipelinePage";' in source
    assert "b1b2PageDefinition" in source
    assert "b1b2Models" in source
    assert "b1b2Files" in source
    assert "onB1B2PageDefinitionSaved" in source
    assert "b1b2CenterOnlyDefinition" in source
    assert "<Arc3B1B2PipelinePage" in source
    assert "arc3-play-b1b2-column" in source

    b1b2_source = (ROOT / "workbench/frontend/src/components/Arc3B1B2PipelinePage.tsx").read_text(encoding="utf-8")
    assert "export type ModelChoice" in b1b2_source
    assert "export type WorkspaceFileRecord" in b1b2_source
    assert "export type Props" in b1b2_source

    styles = STYLES.read_text(encoding="utf-8")
    assert ".arc3-play-b1b2-column" in styles

    workbench_source = WORKBENCH.read_text(encoding="utf-8")
    assert "b1b2PageDefinitionForPlay" in workbench_source
    assert "b1b2PageDefinition={b1b2PageDefinitionForPlay}" in workbench_source


def test_play_page_reads_deep_link_game_param() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    assert 'new URLSearchParams(window.location.search).get("game")' in source


def test_play_page_deep_link_auto_resumes_recording_or_savepoint() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # Guarded once-per-load so React StrictMode's dev-only double-invoke of
    # useEffect doesn't double-import/double-resume.
    assert "deepLinkHandledRef" in source
    assert "deepLinkHandledRef.current = true" in source
    # Sets the picker + Filter for the requested game before anything else.
    assert "setSelectedGameId(requested)" in source
    assert "setFilterGameId(requested)" in source
    # Prefers the last matching IMPORTABLES recording, auto-importing it.
    assert "matchingRecordings" in source
    assert '/arc3-play/import-recording' in source
    # Falls back to the most recent matching RESTART-POINT (savepoint).
    assert 'point.game_directory === requested' in source
    # Resumes a live session from whichever savepoint id was found.
    assert '"/api/arc3-play/sessions"' in source
    assert "savepointId" in source
    # The resumed session's timeline is populated (not dropped) so the user
    # lands on the ending state but can still slide the timeline back to
    # any earlier move, instead of only seeing the win/end frame.
    assert "applyResumedSession(payload.session as PlaySessionSnapshot)" in source


def test_play_page_resume_populates_scrubbable_timeline() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    assert "const applyResumedSession = useCallback((snap: PlaySessionSnapshot)" in source
    assert "setReplayScript(script.length > 0 ? script : null)" in source
    assert "setReplayPos(script.length)" in source
    # resumeSavepoint (the "Resume" button on a save-point) must use the
    # same helper, not silently clear the timeline.
    assert "applyResumedSession(payload.session as PlaySessionSnapshot);\n    });" in source


def test_play_page_recordings_section_can_be_refreshed() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    assert "refreshRecording" in source
    assert "arc3-play-section-actions" in source
    styles = STYLES.read_text(encoding="utf-8")
    assert ".arc3-play-section-actions" in styles


def test_play_page_has_movelist_recording_cross_import_actions() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # RECORDINGS panel: full import + materializing Recordings from move-lists.
    assert "importAllImportables(sortedRecordings)" in source
    assert "importAllMovelistsAsRecordings" in source
    assert "/api/arc3-play/recordings/materialize-movelists" in source
    # MOVE-LISTS panel: lightweight (move-list only) import + deriving
    # move-lists from existing Recordings.
    assert "importAllImportablesAsMovelists(sortedRecordings)" in source
    assert "/api/arc3-play/import-movelist" in source
    assert "importAllRecordingsMoves" in source
    assert "/api/arc3-play/recordings/import-movelists" in source


def test_play_page_recordings_path_can_be_set_from_the_right_panel() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    assert "RECORDINGS PATH" in source
    assert "recordingsPathDraft" in source
    assert "setRecordingsPath" in source
    assert "/recordings-path" in source
    assert "Reset to default" in source
    assert "recordingsPathIsDefault" in source
    styles = STYLES.read_text(encoding="utf-8")
    assert ".arc3-play-recordings-path" in styles

    api_source = API.read_text(encoding="utf-8")
    assert '"/sessions/{session_id}/recordings-path"' in api_source
    assert "def set_recordings_path" in api_source
    assert "def _recordings_container" in api_source
    assert "recordingsPath" in api_source
    assert "recordingsPathIsDefault" in api_source


def test_games_gallery_page_exists_and_is_wired_into_navigation() -> None:
    gallery_component = (ROOT / "workbench/frontend/src/components/Arc3GamesGalleryPage.tsx").read_text(encoding="utf-8")
    assert "export function Arc3GamesGalleryPage(" in gallery_component
    assert "/api/arc3-play/games" in gallery_component
    assert "/preview" in gallery_component
    assert "/api/arc3-play/games/sync" in gallery_component
    assert "onPlayGame" in gallery_component
    assert 'type="search"' in gallery_component
    assert "Sync from arc-interactive" in gallery_component
    # Double-clicking a card (not just the Play & Record button) should also
    # jump straight into Play & Record for that game.
    assert "onDoubleClick={onPlayGame ? () => onPlayGame(shortId) : undefined}" in gallery_component

    gallery_styles = (ROOT / "workbench/frontend/src/styles/arc3_games_gallery.css").read_text(encoding="utf-8")
    assert ".arc3-gallery-grid" in gallery_styles
    assert ".arc3-gallery-thumb" in gallery_styles

    gallery_page_json = (
        ROOT / "workbench/workspaces/arc3_random_player/design/workflow_pages/arc3_games_gallery.workflow_page.json"
    ).read_text(encoding="utf-8")
    assert '"id": "arc3.games_gallery"' in gallery_page_json
    assert '"routeView": "arc3GamesGallery"' in gallery_page_json
    assert '"renderer": "arc3_games_gallery"' in gallery_page_json

    workbench_source = WORKBENCH.read_text(encoding="utf-8")
    assert 'import("../components/Arc3GamesGalleryPage")' in workbench_source
    assert "default: module.Arc3GamesGalleryPage," in workbench_source
    assert '"arc3GamesGallery"' in workbench_source
    assert 'workflowPageForView.renderer === "arc3_games_gallery"' in workbench_source
    assert "<Arc3GamesGalleryPage" in workbench_source
    assert "onPlayGame={(gameShortId) => {" in workbench_source


def test_arc3_play_api_serves_per_game_preview_images_and_sync_action() -> None:
    source = API.read_text(encoding="utf-8")
    assert '"/games/{game_id}/preview"' in source
    assert '"/games/sync"' in source
    assert "_THUMBNAIL_CACHE_DIR" in source
    assert "def _thumbnail_path" in source
    assert "def _render_game_preview_png" in source
    assert "extract_latest_frame" in source
    assert "frame_to_png_bytes" in source
    assert "from arc_interactive_sync import" in source
    assert "sync_summary" in source

