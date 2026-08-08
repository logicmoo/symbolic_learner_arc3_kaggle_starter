"""Repair UTF-8 text that was accidentally decoded as Windows-1252.

Usage:
    python scripts/normalize_markdown_encoding.py [root]
    python scripts/normalize_markdown_encoding.py --check [root]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from _runtime import configure_runtime_home


MARKERS = ("Ã", "Â", "â", "ð", "ï¿½", "�")
IGNORED = {".git", ".venv", "node_modules", "dist"}


def _suspicion(value: str) -> int:
    return sum(value.count(marker) for marker in MARKERS)


def _legacy_bytes(value: str) -> bytes:
    output = bytearray()
    for character in value:
        codepoint = ord(character)
        if codepoint <= 255:
            output.append(codepoint)
        else:
            encoded = character.encode("cp1252")
            if len(encoded) != 1:
                raise UnicodeEncodeError("cp1252", character, 0, 1, "not a single legacy byte")
            output.extend(encoded)
    return bytes(output)


def repair_text(value: str) -> str:
    current = value
    for _ in range(3):
        if not _suspicion(current):
            break
        try:
            candidate = _legacy_bytes(current).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
        if _suspicion(candidate) >= _suspicion(current):
            break
        current = candidate
    return current


def markdown_files(root: Path):
    for path in root.rglob("*.md"):
        if not any(part in IGNORED for part in path.parts):
            yield path


def main() -> int:
    project_root = configure_runtime_home(__file__)
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=str(project_root))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed: list[Path] = []
    for path in markdown_files(Path(args.root).resolve()):
        source = path.read_text(encoding="utf-8")
        repaired = "".join(repair_text(line) for line in source.splitlines(keepends=True))
        if repaired == source:
            continue
        changed.append(path)
        if not args.check:
            path.write_text(repaired, encoding="utf-8", newline="")
    for path in changed:
        print(path)
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
