"""One-time housekeeping: rename data/<game>/level_<n>_<stamp>_<ns>/ (or
data/Recordings/<game>/level_<n>_<stamp>_<ns>/, whichever actually holds the
game dirs) to level_<n>_<NNN>/, ranked by on-disk size within each
(game, level) group -- the biggest gets _001.

Rewrites every reference to a renamed directory in that game's
savepoints.json (level_directory, replay_log[].directory) and each renamed
dir's own recording.json (level_directory), handling BOTH the current disk
location and the older pre-reorg "data/<game>/..." path shape some savepoints
may still reference, so a stale-reference savepoint gets repaired too.

Usage: python scripts/rename_level_dirs_by_size.py <workspace_data_dir> [--apply]
Without --apply it only prints the plan (dry run).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

LEVEL_RE = re.compile(r"^level_(?P<level>[^_]+)_(?P<stamp>\d{8}-\d{6})_(?P<ns>\d+)$")
RANKED_RE = re.compile(r"^level_(?P<level>[^_]+)_(?P<rank>\d{3})$")


def dir_size(path: Path) -> int:
    total = 0
    for entry in path.rglob("*"):
        if entry.is_file():
            try:
                total += entry.stat().st_size
            except OSError:
                pass
    return total


def _games_container(data_root: Path) -> Path:
    """Where the per-game directories actually live: data/Recordings/ if
    present (post-reorg), else data/ directly."""
    recordings = data_root / "Recordings"
    return recordings if recordings.is_dir() else data_root


def build_plan(data_root: Path) -> dict[str, str]:
    """Return {old_relpath: new_relpath}, both relative to the workspace root
    (data_root.parent), for renames plus stale pre-reorg aliases.

    Re-runnable / interruption-safe: already-renamed level_<n>_<NNN> dirs are
    included in each group's size ranking (not just untouched stamp-named
    ones), so a partial previous run never causes two different source dirs
    to be assigned the same target rank.
    """
    workspace_root = data_root.parent
    games_root = _games_container(data_root)
    games_rel = games_root.relative_to(workspace_root).as_posix()  # "data" or "data/Recordings"
    plan: dict[str, str] = {}
    for game_dir in sorted(p for p in games_root.iterdir() if p.is_dir()):
        groups: dict[str, list[Path]] = {}
        for entry in sorted(game_dir.iterdir()):
            if not entry.is_dir():
                continue
            match = LEVEL_RE.match(entry.name) or RANKED_RE.match(entry.name)
            if not match:
                continue
            groups.setdefault(match.group("level"), []).append(entry)
        for level, dirs in groups.items():
            sized = sorted(((dir_size(d), d) for d in dirs), key=lambda item: item[0], reverse=True)
            for rank, (_size, d) in enumerate(sized, start=1):
                new_name = f"level_{level}_{rank:03d}"
                current_rel = d.relative_to(workspace_root).as_posix()
                new_rel = f"{games_rel}/{game_dir.name}/{new_name}"
                if d.name != new_name:
                    plan[current_rel] = new_rel
                    # Older pre-reorg alias some savepoints/recording.json may
                    # still reference ("data/<game>/..." without "Recordings/").
                    if games_rel != "data":
                        plan.setdefault(f"data/{game_dir.name}/{d.name}", new_rel)
                # Recover aliases lost to a previously-interrupted run: if this
                # dir is already at its final name but a crash meant its own
                # recording.json (and hence savepoints referencing it) never
                # got updated, that file's stale self-reference is the only
                # remaining record of the directory's old name(s).
                recording_path = d / "recording.json"
                if recording_path.is_file():
                    try:
                        manifest = json.loads(recording_path.read_text(encoding="utf-8"))
                    except (OSError, json.JSONDecodeError):
                        manifest = {}
                    stale = manifest.get("level_directory") if isinstance(manifest, dict) else None
                    if isinstance(stale, str) and stale not in (current_rel, new_rel):
                        plan.setdefault(stale, new_rel)
    return plan


def _rewrite_path_string(value: str, plan: dict[str, str]) -> str:
    for old_rel, new_rel in plan.items():
        if value == old_rel or value.startswith(old_rel + "/"):
            return new_rel + value[len(old_rel):]
    return value


def _rewrite_json_paths(value: Any, plan: dict[str, str]) -> Any:
    if isinstance(value, str):
        return _rewrite_path_string(value, plan)
    if isinstance(value, list):
        return [_rewrite_json_paths(item, plan) for item in value]
    if isinstance(value, dict):
        return {key: _rewrite_json_paths(item, plan) for key, item in value.items()}
    return value


def apply_plan(data_root: Path, plan: dict[str, str]) -> None:
    workspace_root = data_root.parent
    games_root = _games_container(data_root)

    # Two-phase rename: stage everything under a temp name first, then move
    # temp -> final. A single-phase rename can collide when re-running after
    # a partial/interrupted previous run (some dirs already at their final
    # name, remaining ones re-ranked among a smaller pool can recompute a
    # rank number that an earlier run already claimed). Staging first makes
    # collisions structurally impossible regardless of prior partial state.
    staged: list[tuple[Path, Path]] = []  # (temp_path, final_new_path)
    for old_rel, new_rel in plan.items():
        old_path = workspace_root / old_rel
        new_path = workspace_root / new_rel
        if not old_path.is_dir() or old_path == new_path:
            continue
        temp_path = old_path.parent / f"{old_path.name}.rename_staging_{abs(hash(new_rel)) % 100000}"
        old_path.rename(temp_path)
        staged.append((temp_path, new_path))
    for temp_path, new_path in staged:
        new_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path.rename(new_path)

    # Fix each renamed dir's own recording.json self-reference.
    for new_rel in set(plan.values()):
        recording_path = workspace_root / new_rel / "recording.json"
        if recording_path.is_file():
            manifest = json.loads(recording_path.read_text(encoding="utf-8"))
            manifest = _rewrite_json_paths(manifest, plan)
            recording_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    # Fix savepoints.json for every game dir under the games container.
    for game_dir in sorted(p for p in games_root.iterdir() if p.is_dir()):
        savepoints_path = game_dir / "savepoints.json"
        if not savepoints_path.is_file():
            continue
        entries = json.loads(savepoints_path.read_text(encoding="utf-8"))
        entries = _rewrite_json_paths(entries, plan)
        savepoints_path.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir", type=Path, help="workspace data/ directory, e.g. .../arc3_random_player/data")
    parser.add_argument("--apply", action="store_true", help="actually rename + rewrite (default: dry run)")
    args = parser.parse_args()

    data_root = args.data_dir.resolve()
    if not data_root.is_dir():
        print(f"not a directory: {data_root}", file=sys.stderr)
        sys.exit(1)

    plan = build_plan(data_root)
    if not plan:
        print("nothing to rename")
        return

    real_renames = {k: v for k, v in plan.items() if (data_root.parent / k).is_dir()}
    for old_rel, new_rel in sorted(real_renames.items()):
        print(f"{old_rel}  ->  {new_rel}")
    aliases = len(plan) - len(real_renames)
    print(f"\n{len(real_renames)} directories planned ({aliases} additional stale-reference aliases for JSON repair)")

    if args.apply:
        apply_plan(data_root, plan)
        print("applied.")
    else:
        print("dry run only -- pass --apply to actually rename")


if __name__ == "__main__":
    main()
