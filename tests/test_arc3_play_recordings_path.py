from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
if str(SERVER) not in sys.path:
    sys.path.insert(0, str(SERVER))

import arc3_play_api


def test_games_container_and_write_dir_point_at_recordings() -> None:
    root = Path("/workspace")
    assert arc3_play_api._games_container(root) == root / "data" / "arc3_games" / "recordings"
    assert arc3_play_api._game_write_dir(root, "ar25") == root / "data" / "arc3_games" / "recordings" / "ar25"


def test_arc3_data_migration_merges_existing_canonical_importables(tmp_path: Path) -> None:
    legacy = tmp_path / "data" / "importables"
    canonical = tmp_path / "data" / "arc3_games" / "importables"
    legacy.mkdir(parents=True)
    canonical.mkdir(parents=True)
    (legacy / "same.json").write_text("same", encoding="utf-8")
    (canonical / "same.json").write_text("same", encoding="utf-8")
    (legacy / "legacy.json").write_text("legacy", encoding="utf-8")
    (legacy / "nested").mkdir()
    (legacy / "nested" / "entry.json").write_text("nested", encoding="utf-8")
    (canonical / "canonical.json").write_text("canonical", encoding="utf-8")

    arc3_play_api._migrate_arc3_games_root(tmp_path)

    assert not legacy.exists()
    assert sorted(path.name for path in canonical.iterdir()) == [
        "canonical.json",
        "legacy.json",
        "nested",
        "same.json",
    ]
    assert (canonical / "nested" / "entry.json").read_text(encoding="utf-8") == "nested"


def test_next_ranked_saved_dir_name_starts_at_001_when_none_exist(tmp_path: Path) -> None:
    container = tmp_path / "ar25"
    assert arc3_play_api._next_ranked_saved_dir_name(container) == "saved_001"


def test_next_ranked_saved_dir_name_continues_past_the_highest_existing_rank(tmp_path: Path) -> None:
    container = tmp_path / "ka59"
    container.mkdir()
    (container / "saved_001").mkdir()
    (container / "saved_002").mkdir()
    (container / "saved_014").mkdir()

    assert arc3_play_api._next_ranked_saved_dir_name(container) == "saved_015"


def test_next_ranked_saved_dir_name_pads_to_at_least_three_digits_beyond_999(tmp_path: Path) -> None:
    container = tmp_path / "big"
    container.mkdir()
    (container / "saved_999").mkdir()

    assert arc3_play_api._next_ranked_saved_dir_name(container) == "saved_1000"


def test_next_ranked_saved_dir_name_ignores_unranked_and_timestamped_siblings(tmp_path: Path) -> None:
    container = tmp_path / "mixed"
    container.mkdir()
    (container / "level_1").mkdir()  # bare, no rank suffix
    (container / "level_1_20260822-102222_1787394142910574000").mkdir()  # legacy timestamped
    (container / "saved_003").mkdir()  # the only one that counts

    assert arc3_play_api._next_ranked_saved_dir_name(container) == "saved_004"


def test_next_ranked_saved_dir_name_is_game_wide_not_per_level(tmp_path: Path) -> None:
    # Naming no longer encodes level at all -- rank is a single sequence
    # across the whole game, not scoped per level like the retired
    # level_<n>_<rank> naming was.
    container = tmp_path / "multi_level"
    container.mkdir()
    (container / "saved_005").mkdir()

    assert arc3_play_api._next_ranked_saved_dir_name(container) == "saved_006"


def test_next_ranked_saved_dir_name_continues_numbering_from_legacy_level_dirs(tmp_path: Path) -> None:
    # Workspaces that still have old level_<n>_<rank> dirs on disk (the
    # retired naming) should get strictly-increasing saved_<NNN> numbers,
    # not restart at 001 and collide.
    container = tmp_path / "legacy"
    container.mkdir()
    (container / "level_1_005").mkdir()
    (container / "level_2_009").mkdir()

    assert arc3_play_api._next_ranked_saved_dir_name(container) == "saved_010"


def test_import_instance_dir_name_uses_the_import_s_own_suggested_name(tmp_path: Path) -> None:
    container = tmp_path / "ar25"
    container.mkdir()
    assert arc3_play_api._import_instance_dir_name(container, "20260719-004809", 1) == "20260719-004809"


def test_import_instance_dir_name_suffixes_further_attempts_within_one_import(tmp_path: Path) -> None:
    container = tmp_path / "ar25"
    container.mkdir()
    assert arc3_play_api._import_instance_dir_name(container, "my_recording", 1) == "my_recording"
    assert arc3_play_api._import_instance_dir_name(container, "my_recording", 2) == "my_recording_attempt2"
    assert arc3_play_api._import_instance_dir_name(container, "my_recording", 3) == "my_recording_attempt3"


def test_import_instance_dir_name_dedupes_collisions_with_an_existing_directory(tmp_path: Path) -> None:
    container = tmp_path / "ar25"
    container.mkdir()
    (container / "my_recording").mkdir()

    assert arc3_play_api._import_instance_dir_name(container, "my_recording", 1) == "my_recording_2"


def test_game_dirs_for_prefers_new_location_but_includes_legacy(tmp_path: Path) -> None:
    root = tmp_path
    new_dir = root / "data" / "arc3_games" / "recordings" / "ar25"
    legacy_dir = root / "data" / "ar25"
    new_dir.mkdir(parents=True)
    legacy_dir.mkdir(parents=True)

    dirs = arc3_play_api._game_dirs_for(root, "ar25")

    assert dirs == [new_dir, legacy_dir]


def test_game_dirs_for_returns_only_existing_locations(tmp_path: Path) -> None:
    root = tmp_path
    legacy_dir = root / "data" / "ar25"
    legacy_dir.mkdir(parents=True)

    dirs = arc3_play_api._game_dirs_for(root, "ar25")

    assert dirs == [legacy_dir]
    assert arc3_play_api._game_dirs_for(root, "does-not-exist") == []


def test_all_game_dirs_combines_new_and_legacy_locations_excluding_non_game_dirs(tmp_path: Path) -> None:
    root = tmp_path
    (root / "data" / "arc3_games" / "recordings" / "ka59").mkdir(parents=True)
    (root / "data" / "arc3_games" / "recordings" / "g50t").mkdir(parents=True)
    (root / "data" / "ar25").mkdir(parents=True)
    (root / "data" / "importables").mkdir(parents=True)
    (root / "data" / "SILO_1").mkdir(parents=True)
    (root / "data" / "SILO_1" / "image.png").write_bytes(b"image")

    names = sorted(path.name for path in arc3_play_api._all_game_dirs(root))

    assert names == ["ar25", "g50t", "ka59"]
    assert (root / "data" / "arc3_games" / "curated" / "SILO_1").is_dir()


def test_all_game_dirs_lists_both_locations_for_a_game_present_in_each(tmp_path: Path) -> None:
    root = tmp_path
    (root / "data" / "arc3_games" / "recordings" / "ar25").mkdir(parents=True)
    (root / "data" / "ar25").mkdir(parents=True)

    dirs = arc3_play_api._all_game_dirs(root)

    # Deduplication is by physical path, not by game identity -- the new
    # Recordings/ar25 dir and the legacy data/ar25 dir are different paths
    # on disk, so both are listed (callers merge their savepoints/recordings
    # contents together).
    assert len(dirs) == 2
    names = sorted(path.name for path in dirs)
    assert names == ["ar25", "ar25"]


def _bare_session(workspace_root: Path, game_dir: str = "ar25") -> arc3_play_api.PlaySession:
    """A PlaySession with only the attributes set_recordings_path()/
    _recordings_container() need, bypassing __init__ (which requires the
    real arc_agi engine)."""
    session = object.__new__(arc3_play_api.PlaySession)
    session.workspace_root = workspace_root
    session.game_dir = game_dir
    session.recordings_root = None
    return session


def test_recordings_container_defaults_to_data_recordings_game(tmp_path: Path) -> None:
    session = _bare_session(tmp_path, "ar25")
    assert session._recordings_container() == tmp_path / "data" / "arc3_games" / "recordings" / "ar25"


def test_set_recordings_path_overrides_the_container(tmp_path: Path) -> None:
    session = _bare_session(tmp_path, "ar25")
    session.set_recordings_path("custom/recordings/spot")

    expected = tmp_path / "custom" / "recordings" / "spot"
    assert session._recordings_container() == expected
    assert expected.is_dir()  # created eagerly so writers can rely on it existing


def test_set_recordings_path_empty_or_none_resets_to_default(tmp_path: Path) -> None:
    session = _bare_session(tmp_path, "ar25")
    session.set_recordings_path("custom/spot")
    assert session.recordings_root is not None

    session.set_recordings_path("")
    assert session.recordings_root is None
    assert session._recordings_container() == tmp_path / "data" / "arc3_games" / "recordings" / "ar25"

    session.set_recordings_path("custom/spot")
    session.set_recordings_path(None)
    assert session.recordings_root is None


def test_set_recordings_path_rejects_paths_that_escape_the_workspace(tmp_path: Path) -> None:
    session = _bare_session(tmp_path, "ar25")
    try:
        session.set_recordings_path("../outside")
        raise AssertionError("expected ValueError for a path escaping the workspace root")
    except ValueError:
        pass
    assert session.recordings_root is None


def _write_recording_dir(game_root: Path, name: str, *, size: int, imported: bool) -> Path:
    directory = game_root / name
    directory.mkdir(parents=True)
    manifest: dict[str, object] = {"kind": "arc3_play_recording", "level_directory": None}
    if imported:
        manifest["imported_from"] = "data/arc3_games/importables/fake.json"
    (directory / "recording.json").write_text(json.dumps(manifest), encoding="utf-8")
    if size:
        (directory / "image.png").write_bytes(b"x" * size)
    return directory


def test_iter_recording_dirs_finds_any_directory_with_a_recording_json(tmp_path: Path) -> None:
    game_root = tmp_path / "ar25"
    _write_recording_dir(game_root, "saved_001", size=10, imported=False)
    _write_recording_dir(game_root, "my_import", size=10, imported=True)
    (game_root / "not_a_recording").mkdir()  # no recording.json -- excluded

    names = sorted(entry.name for entry in arc3_play_api._iter_recording_dirs(game_root))
    assert names == ["my_import", "saved_001"]


def test_ranked_recordings_by_size_only_includes_imports_biggest_first(tmp_path: Path) -> None:
    root = tmp_path
    game_root = root / "data" / "arc3_games" / "recordings" / "ar25"
    _write_recording_dir(game_root, "saved_001", size=999, imported=False)  # live-play, excluded
    small = _write_recording_dir(game_root, "small_import", size=10, imported=True)
    big = _write_recording_dir(game_root, "big_import", size=500, imported=True)

    ranked = arc3_play_api._ranked_recordings_by_size_in(root, game_root)

    assert [path for _size, path in ranked] == [big, small]


def test_sort_recordings_by_size_renames_with_size_rank_suffix_biggest_first(tmp_path: Path) -> None:
    root = tmp_path
    game_root = root / "data" / "arc3_games" / "recordings" / "ar25"
    _write_recording_dir(game_root, "saved_001", size=999, imported=False)
    _write_recording_dir(game_root, "small_import", size=10, imported=True)
    _write_recording_dir(game_root, "big_import", size=500, imported=True)

    renamed = arc3_play_api._sort_recordings_by_size_in(root, game_root)

    assert sorted(p.name for p in game_root.iterdir()) == [
        "big_import_size_0001",
        "saved_001",  # untouched -- live play, never renamed
        "small_import_size_0002",
    ]
    assert ("data/arc3_games/recordings/ar25/big_import", "data/arc3_games/recordings/ar25/big_import_size_0001") in renamed
    assert ("data/arc3_games/recordings/ar25/small_import", "data/arc3_games/recordings/ar25/small_import_size_0002") in renamed


def test_sort_recordings_by_size_is_idempotent_after_new_imports_land(tmp_path: Path) -> None:
    root = tmp_path
    game_root = root / "data" / "arc3_games" / "recordings" / "ar25"
    _write_recording_dir(game_root, "small_import", size=10, imported=True)
    _write_recording_dir(game_root, "big_import", size=500, imported=True)
    arc3_play_api._sort_recordings_by_size_in(root, game_root)

    # A new, even bigger import lands after the first sort pass.
    _write_recording_dir(game_root, "huge_import", size=1000, imported=True)
    arc3_play_api._sort_recordings_by_size_in(root, game_root)

    names = sorted(p.name for p in game_root.iterdir())
    assert names == ["big_import_size_0002", "huge_import_size_0001", "small_import_size_0003"]


def test_strip_size_suffix_undoes_a_previous_size_rank_rename() -> None:
    assert arc3_play_api._strip_size_suffix("my_import_size_0002") == "my_import"
    assert arc3_play_api._strip_size_suffix("saved_001") == "saved_001"


def test_savepoint_from_recording_derives_a_move_list_from_a_recording_json(tmp_path: Path) -> None:
    root = tmp_path
    game_root = root / "data" / "arc3_games" / "recordings" / "ar25"
    entry = game_root / "saved_001"
    entry.mkdir(parents=True)
    manifest = {
        "kind": "arc3_play_recording",
        "game_id": "ar25",
        "level": "2",
        "moves": [
            {"action": "ACTION1", "data": {}, "directory": "data/arc3_games/recordings/ar25/saved_001/0", "level": "1", "state": "NOT_FINISHED"},
            {"action": "ACTION2", "data": {"x": 3, "y": 4}, "directory": "data/arc3_games/recordings/ar25/saved_001/1", "level": "2", "state": "WIN"},
        ],
    }
    (entry / "recording.json").write_text(json.dumps(manifest), encoding="utf-8")

    savepoint = arc3_play_api._savepoint_from_recording(root, "ar25", entry)

    assert savepoint is not None
    assert savepoint["level_directory"] == "data/arc3_games/recordings/ar25/saved_001"
    assert savepoint["state"] == "WIN"
    assert savepoint["move_index"] == 1
    assert savepoint["replay_log"] == [
        {"op": "step", "action": "ACTION1", "data": {}, "directory": "data/arc3_games/recordings/ar25/saved_001/0", "level": "1"},
        {"op": "step", "action": "ACTION2", "data": {"x": 3, "y": 4}, "directory": "data/arc3_games/recordings/ar25/saved_001/1", "level": "2"},
    ]


def test_savepoint_from_recording_returns_none_for_a_manifest_with_no_moves(tmp_path: Path) -> None:
    root = tmp_path
    game_root = root / "data" / "arc3_games" / "recordings" / "ar25"
    entry = game_root / "saved_001"
    entry.mkdir(parents=True)
    (entry / "recording.json").write_text(json.dumps({"moves": []}), encoding="utf-8")

    assert arc3_play_api._savepoint_from_recording(root, "ar25", entry) is None


def test_import_movelists_from_recordings_skips_dirs_that_already_have_one(tmp_path: Path) -> None:
    root = tmp_path
    game_root = root / "data" / "arc3_games" / "recordings" / "ar25"
    entry = game_root / "saved_001"
    entry.mkdir(parents=True)
    manifest = {"moves": [{"action": "ACTION1", "data": {}, "directory": "x/0", "level": "1", "state": "NOT_FINISHED"}]}
    (entry / "recording.json").write_text(json.dumps(manifest), encoding="utf-8")

    created_first = arc3_play_api._import_movelists_from_recordings_in(root, game_root)
    assert created_first == 1
    savepoints = json.loads((game_root / "savepoints.json").read_text(encoding="utf-8"))
    assert len(savepoints) == 1
    assert savepoints[0]["level_directory"] == "data/arc3_games/recordings/ar25/saved_001"

    # Re-running doesn't create a duplicate for the same Recording dir.
    created_second = arc3_play_api._import_movelists_from_recordings_in(root, game_root)
    assert created_second == 0
    savepoints_after = json.loads((game_root / "savepoints.json").read_text(encoding="utf-8"))
    assert len(savepoints_after) == 1


def test_clear_recordings_deletes_every_recording_dir_for_a_game(tmp_path: Path, monkeypatch) -> None:
    import workspace_api

    monkeypatch.setattr(workspace_api, "_workspace_roots", lambda: [tmp_path.parent])
    root = tmp_path
    game_root = root / "data" / "arc3_games" / "recordings" / "ar25"
    _write_recording_dir(game_root, "saved_001", size=10, imported=False)
    _write_recording_dir(game_root, "my_import", size=10, imported=True)
    other_game_root = root / "data" / "arc3_games" / "recordings" / "ka59"
    _write_recording_dir(other_game_root, "saved_001", size=10, imported=False)

    result = arc3_play_api.clear_recordings(workspaceId=root.name, gameId="ar25")

    assert result["count"] == 2
    assert not game_root.exists() or not list(game_root.iterdir())
    # A different game is untouched.
    assert (other_game_root / "saved_001").is_dir()


def test_clear_savepoints_empties_savepoints_json_for_a_game(tmp_path: Path, monkeypatch) -> None:
    import workspace_api

    monkeypatch.setattr(workspace_api, "_workspace_roots", lambda: [tmp_path.parent])
    root = tmp_path
    game_root = root / "data" / "arc3_games" / "recordings" / "ar25"
    game_root.mkdir(parents=True)
    (game_root / "savepoints.json").write_text(
        json.dumps([{"id": "a"}, {"id": "b"}]),
        encoding="utf-8",
    )

    result = arc3_play_api.clear_savepoints(workspaceId=root.name, gameId="ar25")

    assert result["count"] == 2
    assert json.loads((game_root / "savepoints.json").read_text(encoding="utf-8")) == []
