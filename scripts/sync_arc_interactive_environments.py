"""Copy ARC-AGI-3 game environment packages from a sibling ``arc-interactive``
checkout into ``workbench/server/environment_files``, so the workbench's
ARC3 Play & Record engine (``arc_agi.Arcade(environments_dir=...)``, which
resolves relative to the running server's CWD) discovers them.

``workbench/server/environment_files/`` is intentionally gitignored (see
".gitignore": "Vendored framework + downloaded game source + agent
recordings") -- it is a local, per-machine cache of downloaded/authored game
packages, not repository source. ``../arc-interactive`` is a separate repo
holding a much larger hand-authored ARC-AGI-3 game suite (200+ games; see its
GAMES.md) alongside the same official arcprize competition games the
workbench already caches. This script merges the former into the latter.

Layout on both sides is ``<game_stem>/<version_hash>/{<stem>.py,metadata.json}``
(confirmed uniform: every stem has exactly one .py + one metadata.json per
version dir). Merging is purely additive and collision-safe: version-hash
directories are copied only when that exact ``<stem>/<hash>`` pair does not
already exist at the destination, so re-running is idempotent and a stem
that exists in both repos under different hashes (e.g. the same official
game downloaded on different dates) ends up with multiple version dirs,
which the ``Arcade`` toolkit already tolerates (some workbench games already
have this).

Usage:
    python scripts/sync_arc_interactive_environments.py [--apply]
        [--source PATH] [--dest PATH] [--only stem,stem,...] [--exclude stem,stem,...]

Without --apply it only prints the plan (dry run).
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT.parent / "arc-interactive" / "environment_files"
DEFAULT_DEST = REPO_ROOT / "workbench" / "server" / "environment_files"


def _is_well_formed_version_dir(path: Path) -> bool:
    """A version dir must hold exactly a ``metadata.json`` plus one ``.py`` file."""
    if not path.is_dir():
        return False
    if not (path / "metadata.json").is_file():
        return False
    return any(child.suffix == ".py" for child in path.iterdir() if child.is_file())


def plan_sync(source: Path, dest: Path, *, only: set[str] | None, exclude: set[str]) -> tuple[
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
            if not _is_well_formed_version_dir(version_dir):
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="arc-interactive environment_files dir")
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST, help="workbench environment_files dir")
    parser.add_argument("--only", type=str, default="", help="comma-separated allowlist of game stems")
    parser.add_argument("--exclude", type=str, default="", help="comma-separated denylist of game stems")
    parser.add_argument("--apply", action="store_true", help="actually copy files (default: dry run)")
    args = parser.parse_args()

    only = {stem.strip() for stem in args.only.split(",") if stem.strip()} or None
    exclude = {stem.strip() for stem in args.exclude.split(",") if stem.strip()}

    source = args.source.expanduser().resolve()
    dest = args.dest.expanduser().resolve()

    try:
        to_copy, already_present, malformed = plan_sync(source, dest, only=only, exclude=exclude)
    except FileNotFoundError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    new_stems = sorted({stem for stem, _src, _dst in to_copy})
    print(f"Source: {source}")
    print(f"Dest:   {dest}")
    print(f"Version dirs already present at dest: {len(already_present)}")
    print(f"Version dirs to copy:                 {len(to_copy)}  ({len(new_stems)} distinct game stem(s))")
    if malformed:
        print(f"Skipped malformed source dirs:         {len(malformed)}")
        for stem, path in malformed:
            print(f"  ! {stem}: {path}")

    if to_copy:
        print("\nGame stems that will gain a new version dir:")
        for stem in new_stems:
            versions = [src.name for s, src, _dst in to_copy if s == stem]
            print(f"  {stem}: {', '.join(versions)}")

    if not args.apply:
        print("\nDry run only -- re-run with --apply to copy these files.")
        return 0

    apply_sync(to_copy)
    print(f"\nCopied {len(to_copy)} version dir(s) into {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
