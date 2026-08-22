from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
if str(SERVER) not in sys.path:
    sys.path.insert(0, str(SERVER))

import arc3_play_api


def test_games_container_and_write_dir_point_at_recordings() -> None:
    root = Path("/workspace")
    assert arc3_play_api._games_container(root) == root / "data" / "Recordings"
    assert arc3_play_api._game_write_dir(root, "ar25") == root / "data" / "Recordings" / "ar25"


def test_next_ranked_level_dir_name_starts_at_001_when_none_exist(tmp_path: Path) -> None:
    container = tmp_path / "ar25"
    assert arc3_play_api._next_ranked_level_dir_name(container, "1") == "level_1_001"


def test_next_ranked_level_dir_name_continues_past_the_highest_existing_rank(tmp_path: Path) -> None:
    container = tmp_path / "ka59"
    container.mkdir()
    (container / "level_1_001").mkdir()
    (container / "level_1_002").mkdir()
    (container / "level_1_014").mkdir()

    assert arc3_play_api._next_ranked_level_dir_name(container, "1") == "level_1_015"


def test_next_ranked_level_dir_name_pads_to_at_least_three_digits_beyond_999(tmp_path: Path) -> None:
    container = tmp_path / "big"
    container.mkdir()
    (container / "level_1_999").mkdir()

    assert arc3_play_api._next_ranked_level_dir_name(container, "1") == "level_1_1000"


def test_next_ranked_level_dir_name_ignores_unranked_and_timestamped_siblings(tmp_path: Path) -> None:
    container = tmp_path / "mixed"
    container.mkdir()
    (container / "level_1").mkdir()  # bare, no rank suffix
    (container / "level_1_20260822-102222_1787394142910574000").mkdir()  # legacy timestamped
    (container / "level_1_003").mkdir()  # the only one that counts

    assert arc3_play_api._next_ranked_level_dir_name(container, "1") == "level_1_004"


def test_next_ranked_level_dir_name_tracks_each_level_independently(tmp_path: Path) -> None:
    container = tmp_path / "multi_level"
    container.mkdir()
    (container / "level_1_005").mkdir()
    (container / "level_2_001").mkdir()

    assert arc3_play_api._next_ranked_level_dir_name(container, "1") == "level_1_006"
    assert arc3_play_api._next_ranked_level_dir_name(container, "2") == "level_2_002"
    assert arc3_play_api._next_ranked_level_dir_name(container, "3") == "level_3_001"


def test_game_dirs_for_prefers_new_location_but_includes_legacy(tmp_path: Path) -> None:
    root = tmp_path
    new_dir = root / "data" / "Recordings" / "ar25"
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
    (root / "data" / "Recordings" / "ka59").mkdir(parents=True)
    (root / "data" / "Recordings" / "g50t").mkdir(parents=True)
    (root / "data" / "ar25").mkdir(parents=True)
    (root / "data" / "importables").mkdir(parents=True)
    (root / "data" / "SILO_1").mkdir(parents=True)

    names = sorted(path.name for path in arc3_play_api._all_game_dirs(root))

    # "Recordings" itself and "importables"/"SILO_1"-style siblings are not
    # treated as games; SILO_1 isn't in the exclusion set so it's included
    # (matches _DATA_ROOT_NON_GAME_DIRS exactly: recordings + importables).
    assert names == ["SILO_1", "ar25", "g50t", "ka59"]


def test_all_game_dirs_lists_both_locations_for_a_game_present_in_each(tmp_path: Path) -> None:
    root = tmp_path
    (root / "data" / "Recordings" / "ar25").mkdir(parents=True)
    (root / "data" / "ar25").mkdir(parents=True)

    dirs = arc3_play_api._all_game_dirs(root)

    # Deduplication is by physical path, not by game identity -- the new
    # Recordings/ar25 dir and the legacy data/ar25 dir are different paths
    # on disk, so both are listed (callers merge their savepoints/recordings
    # contents together).
    assert len(dirs) == 2
    names = sorted(path.name for path in dirs)
    assert names == ["ar25", "ar25"]
