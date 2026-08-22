from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import sync_arc_interactive_environments as sync_mod  # noqa: E402


def _make_version_dir(root: Path, stem: str, version: str, *, well_formed: bool = True) -> Path:
    version_dir = root / stem / version
    version_dir.mkdir(parents=True)
    if well_formed:
        (version_dir / "metadata.json").write_text('{"game_id": "%s-%s"}' % (stem, version), encoding="utf-8")
        (version_dir / f"{stem}.py").write_text("# game source\n", encoding="utf-8")
    else:
        # Missing metadata.json -> malformed.
        (version_dir / f"{stem}.py").write_text("# game source\n", encoding="utf-8")
    return version_dir


def test_plan_sync_copies_new_version_dirs_and_skips_existing(tmp_path: Path) -> None:
    source = tmp_path / "source"
    dest = tmp_path / "dest"
    _make_version_dir(source, "ez01", "63be02fb")
    _make_version_dir(source, "ft09", "9ab2447a")
    # Destination already has ft09 under a DIFFERENT hash -- must not collide,
    # and the source's own ft09 hash is not yet present, so it should copy.
    _make_version_dir(dest, "ft09", "0d8bbf25")

    to_copy, already_present, malformed = sync_mod.plan_sync(source, dest, only=None, exclude=set())

    copied_pairs = {(stem, src.name) for stem, src, _dst in to_copy}
    assert copied_pairs == {("ez01", "63be02fb"), ("ft09", "9ab2447a")}
    assert already_present == []
    assert malformed == []


def test_plan_sync_is_idempotent_after_apply(tmp_path: Path) -> None:
    source = tmp_path / "source"
    dest = tmp_path / "dest"
    _make_version_dir(source, "ez01", "63be02fb")

    to_copy, _already_present, _malformed = sync_mod.plan_sync(source, dest, only=None, exclude=set())
    assert len(to_copy) == 1
    sync_mod.apply_sync(to_copy)
    assert (dest / "ez01" / "63be02fb" / "metadata.json").is_file()
    assert (dest / "ez01" / "63be02fb" / "ez01.py").is_file()

    to_copy_again, already_present_again, _malformed = sync_mod.plan_sync(source, dest, only=None, exclude=set())
    assert to_copy_again == []
    assert [(stem, path.name) for stem, path in already_present_again] == [("ez01", "63be02fb")]


def test_plan_sync_skips_malformed_version_dirs(tmp_path: Path) -> None:
    source = tmp_path / "source"
    dest = tmp_path / "dest"
    _make_version_dir(source, "broken", "v1", well_formed=False)

    to_copy, already_present, malformed = sync_mod.plan_sync(source, dest, only=None, exclude=set())

    assert to_copy == []
    assert already_present == []
    assert [(stem, path.name) for stem, path in malformed] == [("broken", "v1")]


def test_plan_sync_honors_only_and_exclude_filters(tmp_path: Path) -> None:
    source = tmp_path / "source"
    dest = tmp_path / "dest"
    _make_version_dir(source, "ez01", "63be02fb")
    _make_version_dir(source, "ez02", "63be02fb")
    _make_version_dir(source, "ez03", "63be02fb")

    only_result, _already, _malformed = sync_mod.plan_sync(source, dest, only={"ez01", "ez02"}, exclude=set())
    assert {stem for stem, _src, _dst in only_result} == {"ez01", "ez02"}

    exclude_result, _already, _malformed = sync_mod.plan_sync(source, dest, only=None, exclude={"ez02"})
    assert {stem for stem, _src, _dst in exclude_result} == {"ez01", "ez03"}


def test_plan_sync_raises_for_missing_source(tmp_path: Path) -> None:
    missing_source = tmp_path / "does-not-exist"
    dest = tmp_path / "dest"
    try:
        sync_mod.plan_sync(missing_source, dest, only=None, exclude=set())
        raise AssertionError("expected FileNotFoundError")
    except FileNotFoundError:
        pass


def test_sync_script_defaults_point_at_sibling_arc_interactive_repo() -> None:
    assert sync_mod.DEFAULT_SOURCE == ROOT.parent / "arc-interactive" / "environment_files"
    assert sync_mod.DEFAULT_DEST == ROOT / "workbench" / "server" / "environment_files"
