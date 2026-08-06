from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SERVER = Path(__file__).resolve().parents[1] / "server"
if str(SERVER) not in sys.path:
    sys.path.insert(0, str(SERVER))

from resource_convention import canonical_resource_path, infer_resource_kind, validate_kind_filename


WORKSPACES = Path(__file__).resolve().parents[1] / "workspaces"


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

    if write and changed:
        if target != path and target.exists():
            return False, [f"{path}: target already exists: {target}"]
        target.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if target != path:
            path.unlink()

    final_path = target if write and changed else path
    errors = validate_kind_filename(final_path, document)
    if errors and write:
        return False, [f"{final_path}: {error}" for error in errors]
    return changed, [f"{path.relative_to(WORKSPACES)}: " + ", ".join(messages)] if messages else []


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize workbench workspace JSON resource kinds and filenames.")
    parser.add_argument("--write", action="store_true", help="Rewrite and rename resources in place. Without this flag the command only reports changes.")
    args = parser.parse_args()

    changed_count = 0
    problems: list[str] = []
    for path in sorted(WORKSPACES.rglob("*.json")):
        changed, messages = normalize_file(path, write=args.write)
        if changed:
            changed_count += 1
        for message in messages:
            print(message)
        if not changed and messages and any("invalid" in message or "unable" in message or "target already" in message for message in messages):
            problems.extend(messages)

    mode = "normalized" if args.write else "would normalize"
    print(f"{mode} {changed_count} JSON resource(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
