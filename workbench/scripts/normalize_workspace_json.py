from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

SERVER = Path(__file__).resolve().parents[1] / "server"
if str(SERVER) not in sys.path:
    sys.path.insert(0, str(SERVER))

from resource_convention import canonical_resource_path, infer_resource_kind, validate_kind_filename


WORKSPACES = Path(__file__).resolve().parents[1] / "workspaces"


def merge_json_values(legacy: Any, canonical: Any) -> Any:
    """Merge a legacy value into the canonical value without losing either side.

    Canonical scalar values win because the canonical file is the current resource.
    Dictionaries are merged recursively. Lists use a stable union so capabilities,
    variants, tags, etc. from either copy survive normalization.
    """
    if isinstance(legacy, dict) and isinstance(canonical, dict):
        merged = deepcopy(legacy)
        for key, canonical_value in canonical.items():
            if key in merged:
                merged[key] = merge_json_values(merged[key], canonical_value)
            else:
                merged[key] = deepcopy(canonical_value)
        return merged

    if isinstance(legacy, list) and isinstance(canonical, list):
        merged = deepcopy(legacy)
        for item in canonical:
            if item not in merged:
                merged.append(deepcopy(item))
        return merged

    return deepcopy(canonical)


def merge_duplicate_resource(
    source_path: Path,
    target_path: Path,
    source_document: dict[str, Any],
    *,
    write: bool,
) -> tuple[bool, list[str]]:
    """Merge a legacy/non-canonical resource into an existing canonical target."""
    try:
        target_document = json.loads(target_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return False, [f"{source_path}: existing canonical target is invalid JSON: {target_path}: {error}"]

    if not isinstance(target_document, dict):
        return False, [f"{source_path}: existing canonical target must contain an object: {target_path}"]

    source_kind = infer_resource_kind(source_path, source_document)
    target_kind = infer_resource_kind(target_path, target_document)
    if source_kind != target_kind:
        return False, [
            f"{source_path}: refusing to merge different resource kinds: "
            f"{source_kind!r} -> {target_kind!r} ({target_path})"
        ]

    source_id = str(source_document.get("id") or "").strip()
    target_id = str(target_document.get("id") or "").strip()
    if source_id and target_id and source_id != target_id:
        return False, [
            f"{source_path}: refusing to merge different resource ids: "
            f"{source_id!r} -> {target_id!r} ({target_path})"
        ]

    source_document = dict(source_document)
    source_document["kind"] = source_kind
    target_document = dict(target_document)
    target_document["kind"] = target_kind
    merged = merge_json_values(source_document, target_document)

    errors = validate_kind_filename(target_path, merged)
    if errors:
        return False, [f"{target_path}: {error}" for error in errors]

    relative_source = source_path.relative_to(WORKSPACES)
    relative_target = target_path.relative_to(WORKSPACES)
    message = (
        f"{relative_source}: merge duplicate -> {relative_target} "
        "(canonical values kept on scalar conflicts; lists unioned)"
    )

    if write:
        target_path.write_text(
            json.dumps(merged, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        source_path.unlink()

    return True, [message]


def normalize_file(path: Path, *, write: bool) -> tuple[bool, list[str]]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return False, [f"{path}: invalid JSON: {error}"]
    if not isinstance(document, dict):
        return False, [f"{path}: top-level JSON value must be an object"]

    kind = infer_resource_kind(path, document)
    if not kind:
        return False, [f"{path}: unable to infer kind; add a kind property explicitly"]

    changed = False
    messages: list[str] = []
    if document.get("kind") != kind:
        document["kind"] = kind
        changed = True
        messages.append(f"kind -> {kind}")

    target = canonical_resource_path(path, document)
    if target != path:
        changed = True
        messages.append(f"rename -> {target.name}")

    if target != path and target.exists():
        return merge_duplicate_resource(path, target, document, write=write)

    if write and changed:
        target.write_text(
            json.dumps(document, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        if target != path:
            path.unlink()

    final_path = target if write and changed else path
    errors = validate_kind_filename(final_path, document)
    if errors and write:
        return False, [f"{final_path}: {error}" for error in errors]
    return changed, [f"{path.relative_to(WORKSPACES)}: " + ", ".join(messages)] if messages else []


def _is_problem(message: str) -> bool:
    problem_tokens = (
        "invalid JSON",
        "must contain an object",
        "unable to infer",
        "refusing to merge",
        "existing canonical target is invalid",
    )
    return any(token in message for token in problem_tokens)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize workbench workspace JSON resource kinds and filenames."
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help=(
            "Rewrite/rename resources in place. Existing legacy+canonical duplicates "
            "are merged into the canonical file and the legacy copy is removed."
        ),
    )
    args = parser.parse_args()

    changed_count = 0
    problems: list[str] = []
    # Materialize first because --write may rename/delete entries while walking.
    paths = sorted(WORKSPACES.rglob("*.json"))
    for path in paths:
        if not path.exists():
            continue
        changed, messages = normalize_file(path, write=args.write)
        if changed:
            changed_count += 1
        for message in messages:
            print(message)
            if _is_problem(message):
                problems.append(message)

    mode = "normalized" if args.write else "would normalize"
    print(f"{mode} {changed_count} JSON resource(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
