"""CLI wrapper around ``python/arc_interactive_sync.py``: copy ARC-AGI-3 game
environment packages from a sibling ``arc-interactive`` checkout into
``workbench/server/environment_files``, so the workbench's ARC3 Play &
Record engine (``arc_agi.Arcade(environments_dir=...)``, which resolves
relative to the running server's CWD) discovers them.

See ``python/arc_interactive_sync.py`` for the shared merge logic and full
rationale (also reused by the in-app ``POST /arc3-play/games/sync`` action).

Usage:
    python scripts/sync_arc_interactive_environments.py [--apply]
        [--source PATH] [--dest PATH] [--only stem,stem,...] [--exclude stem,stem,...]

Without --apply it only prints the plan (dry run).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
_PYTHON_ROOT = REPO_ROOT / "python"
if str(_PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(_PYTHON_ROOT))

from arc_interactive_sync import DEFAULT_DEST, DEFAULT_SOURCE, apply_sync, plan_sync  # noqa: E402


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
