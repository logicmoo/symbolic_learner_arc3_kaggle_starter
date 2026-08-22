"""Reusable logic for merging a sibling ``arc-interactive`` checkout's ARC-AGI-3
game environment packages into ``workbench/server/environment_files``.

Shared by ``scripts/sync_arc_interactive_environments.py`` (CLI) and the
``POST /arc3-play/games/sync`` endpoint in ``arc3_play_api.py`` (in-app
"notice new games" action), so both stay in lockstep with a single copy of
the merge rules.

``workbench/server/environment_files/`` is intentionally gitignored (see
".gitignore": "Vendored framework + downloaded game source + agent
recordings") -- it is a local, per-machine cache of downloaded/authored game
packages, not repository source. ``../arc-interactive`` is a separate repo
holding a much larger hand-authored ARC-AGI-3 game suite (200+ games; see its
GAMES.md) alongside the same official arcprize competition games the
workbench already caches.

Layout on both sides is ``<game_stem>/<version_hash>/{<stem>.py,metadata.json}``
(confirmed uniform: every stem has exactly one .py + one metadata.json per
version dir). Merging is purely additive and collision-safe: version-hash
directories are copied only when that exact ``<stem>/<hash>`` pair does not
already exist at the destination, so re-running is idempotent and a stem
that exists in both repos under different hashes (e.g. the same official
game downloaded on different dates) ends up with multiple version dirs,
which the ``Arcade`` toolkit already tolerates.
"""
from __future__ import annotations

import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT.parent / "arc-interactive" / "environment_files"
DEFAULT_DEST = REPO_ROOT / "workbench" / "server" / "environment_files"


def is_well_formed_version_dir(path: Path) -> bool:
    """A version dir must hold exactly a ``metadata.json`` plus one ``.py`` file."""
    if not path.is_dir():
        return False
    if not (path / "metadata.json").is_file():
        return False
    return any(child.suffix == ".py" for child in path.iterdir() if child.is_file())


def plan_sync(source: Path, dest: Path, *, only: set[str] | None = None, exclude: set[str] = frozenset()) -> tuple[
    list[tuple[str, Path, Path]], list[tuple[str, Path]], list[tuple[str, Path]]
]:
    """Return (to_copy, already_present, malformed) for every stem/version dir."""
    to_copy: list[tuple[str, Path, Path]] = []
    already_present: list[tuple[str, Path]] = []
    malformed: list[tuple[str, Path]] = []

    if not source.is_dir():
        raise FileNotFoundError(f"source environments dir not found: {source}")

    for stem_dir in sorted(source.iterdir(), key=lambda path: path.name.lower()):
        if not stem_dir.is_dir():
            continue
        stem = stem_dir.name
        if only is not None and stem not in only:
            continue
        if stem in exclude:
            continue
        for version_dir in sorted(stem_dir.iterdir(), key=lambda path: path.name.lower()):
            if not version_dir.is_dir():
                continue
            if not is_well_formed_version_dir(version_dir):
                malformed.append((stem, version_dir))
                continue
            dest_version_dir = dest / stem / version_dir.name
            if dest_version_dir.exists():
                already_present.append((stem, version_dir))
                continue
            to_copy.append((stem, version_dir, dest_version_dir))

    return to_copy, already_present, malformed


def apply_sync(to_copy: list[tuple[str, Path, Path]]) -> None:
    for _stem, source_version_dir, dest_version_dir in to_copy:
        dest_version_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_version_dir, dest_version_dir)


def sync_summary(source: Path, dest: Path, *, only: set[str] | None = None, exclude: set[str] = frozenset()) -> dict:
    """Plan + apply in one call; returns a JSON-friendly summary dict.

    Used by the ``POST /arc3-play/games/sync`` endpoint. Never raises for a
    missing source dir (returns ``available: False`` instead) since the
    sibling ``arc-interactive`` checkout is optional -- not every machine or
    deployment running the workbench will have it beside this repo.
    """
    if not source.is_dir():
        return {
            "available": False,
            "source": str(source),
            "dest": str(dest),
            "copied": 0,
            "alreadyPresent": 0,
            "malformed": 0,
            "newStems": [],
        }
    to_copy, already_present, malformed = plan_sync(source, dest, only=only, exclude=exclude)
    apply_sync(to_copy)
    return {
        "available": True,
        "source": str(source),
        "dest": str(dest),
        "copied": len(to_copy),
        "alreadyPresent": len(already_present),
        "malformed": len(malformed),
        "newStems": sorted({stem for stem, _src, _dst in to_copy}),
    }
