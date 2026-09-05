#!/usr/bin/env python
"""Generate Markdown API documentation for the repository's first-party packages.

Uses the well-known ``pydoc-markdown`` toolchain (which statically parses source,
so nothing is imported) to render one Markdown page per top-level package
(recursively, via ``-p``) and per top-level module (via ``-m``) declared in
``pyproject.toml`` (``[tool.setuptools]`` ``packages`` + ``py-modules``). Each page
is written to ``docs/api/`` and prefixed with a link back to the project README so
it satisfies the documentation-link tests.

Run:      ``python scripts/build_api_docs.py``   (or ``scripts\\build_api_docs.bat``)
Requires: ``pip install -e ".[docs]"``            (installs pydoc-markdown)
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "docs" / "api"
BACKLINK = "> [\u2190 Project README](../../README.md)"


def _pydoc_markdown() -> str:
    """Locate the pydoc-markdown console script (prefer the current venv)."""
    name = "pydoc-markdown.exe" if sys.platform == "win32" else "pydoc-markdown"
    candidate = Path(sys.executable).parent / name
    if candidate.exists():
        return str(candidate)
    found = shutil.which("pydoc-markdown")
    if found:
        return found
    sys.exit('pydoc-markdown not found. Install it with: pip install -e ".[docs]"')


def _targets() -> tuple[list[str], list[str]]:
    """Top-level packages (deduped) and top-level modules from pyproject."""
    data = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))
    st = data["tool"]["setuptools"]
    packages = sorted({p.split(".")[0] for p in st.get("packages", [])})
    modules = sorted(st.get("py-modules", []))
    return packages, modules


def _render(tool: str, flag: str, name: str) -> str | None:
    """Render one package (``-p``) or module (``-m``) to Markdown, or None on error.

    Drives pydoc-markdown through a generated config (JSON is valid YAML) instead
    of the bare CLI flags so the ``filter`` processor can run with
    ``documented_only: false``. That keeps *every* public member in the output --
    including undocumented dataclass fields (e.g. ``NormalizedResult.value``) and
    methods that would otherwise be dropped -- while ``--render-toc`` behaviour is
    preserved via ``render_toc: true``.
    """
    key = "packages" if flag == "-p" else "modules"
    # pydoc-markdown resolves relative loader search paths relative to the config
    # file's directory. Since the config is written to a temp file, use absolute
    # paths so ``python/`` and the repo root are always found.
    search_path = [str(REPO / "python"), str(REPO)]
    config = {
        "loaders": [{"type": "python", "search_path": search_path, key: [name]}],
        "processors": [
            {
                "type": "filter",
                # Keep undocumented members (e.g. dataclass fields such as
                # NormalizedResult.value) so every public member is listed, but
                # drop the re-export Indirection nodes that ``__init__`` files
                # create -- otherwise each re-exported name appears again as an
                # empty stub and the TOC links to the stub, not the definition.
                "documented_only": False,
                "skip_empty_modules": True,
                "expression": "default() and type(obj).__name__ != 'Indirection'",
            },
            {"type": "smart"},
            {"type": "crossref"},
        ],
        "renderer": {
            "type": "markdown",
            "render_toc": True,
            # Show each data member's annotation in its header (e.g.
            # ``value: Any``) instead of a misleading ``= None`` assignment.
            "render_typehint_in_data_header": True,
        },
    }
    tmp = tempfile.NamedTemporaryFile(
        "w", suffix=".yml", delete=False, encoding="utf-8"
    )
    try:
        json.dump(config, tmp)
        tmp.close()
        cmd = [tool, tmp.name]
        try:
            result = subprocess.run(
                cmd, cwd=REPO, capture_output=True, text=True, encoding="utf-8"
            )
        except OSError as exc:
            print(f"  ! {name}: {exc}")
            return None
    finally:
        Path(tmp.name).unlink(missing_ok=True)
    if result.returncode != 0 or not result.stdout.strip():
        print(f"  ! {name}: {(result.stderr or 'empty output').strip()[:140]}")
        return None
    return result.stdout


def main() -> int:
    tool = _pydoc_markdown()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUT_DIR.glob("*.md"):
        old.unlink()

    packages, modules = _targets()
    written: list[str] = []
    for flag, names in (("-p", packages), ("-m", modules)):
        for name in names:
            md = _render(tool, flag, name)
            if md is None:
                continue
            (OUT_DIR / f"{name}.md").write_text(
                f"{BACKLINK}\n\n{md.strip()}\n", encoding="utf-8"
            )
            written.append(name)

    index = [
        "# API Reference", "", BACKLINK, "",
        "Auto-generated from source docstrings with "
        "[`pydoc-markdown`](https://niklasrosenstein.github.io/pydoc-markdown/) by "
        "[`scripts/build_api_docs.py`](../../scripts/build_api_docs.py) "
        "(or `scripts/build_api_docs.bat`). Regenerate after code changes.", "",
        "## Packages & modules", "",
    ]
    index += [f"- [`{name}`]({name}.md)" for name in written]
    index.append("")
    (OUT_DIR / "README.md").write_text("\n".join(index), encoding="utf-8")
    print(f"Wrote {len(written)} API pages + index to {OUT_DIR.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
