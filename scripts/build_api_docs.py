#!/usr/bin/env python
"""Generate Markdown API documentation for the repository's first-party packages.

Introspects every package/module declared in ``pyproject.toml`` (``[tool.setuptools]``
``packages`` + ``py-modules``), expanding packages to their submodules, and writes one
Markdown reference page per module into ``docs/api/`` plus an ``index`` page. Each page
links back to the project README so it satisfies the documentation-link tests.

Run: ``python scripts/build_api_docs.py``  (from the repository root).
"""
from __future__ import annotations

import dataclasses
import enum
import inspect
import importlib
import pkgutil
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PY_DIR = REPO / "python"
SERVER_DIR = REPO / "workbench" / "server"
OUT_DIR = REPO / "docs" / "api"
BACKLINK = "> [\u2190 Project README](../../README.md)"

for _p in (PY_DIR, SERVER_DIR, REPO):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))


def _targets() -> list[str]:
    """Every top-level first-party module/package name from pyproject, expanded."""
    data = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))
    st = data["tool"]["setuptools"]
    names: list[str] = list(st.get("packages", [])) + list(st.get("py-modules", []))
    expanded: set[str] = set()
    for name in names:
        expanded.add(name)
        try:
            mod = importlib.import_module(name)
        except Exception:  # noqa: BLE001 - keep going; report missing later
            continue
        if hasattr(mod, "__path__"):  # a package -> add its submodules
            for info in pkgutil.iter_modules(mod.__path__):
                if not info.name.startswith("_"):
                    expanded.add(f"{name}.{info.name}")
    return sorted(expanded)


def _sig(obj) -> str:
    try:
        return str(inspect.signature(obj))
    except (TypeError, ValueError):
        return "(...)"


def _first_line(obj) -> str:
    doc = inspect.getdoc(obj) or ""
    line = doc.strip().split("\n\n")[0].replace("\n", " ").strip()
    if line.startswith("Initialize self."):  # inherited object.__init__ boilerplate
        return ""
    return line


def _is_local(obj, module) -> bool:
    return getattr(obj, "__module__", None) == module.__name__


def _document_class(cls) -> list[str]:
    bases = ", ".join(b.__name__ for b in cls.__bases__ if b is not object)
    head = f"### `class {cls.__name__}" + (f"({bases})`" if bases else "`")
    lines = [head, ""]
    doc = _first_line(cls)
    if dataclasses.is_dataclass(cls) and doc.startswith(cls.__name__ + "("):
        doc = ""  # suppress the auto-generated dataclass repr shown as __doc__
    if doc:
        lines += [doc, ""]
    if isinstance(cls, type) and issubclass(cls, enum.Enum):
        lines.append("Values: " + ", ".join(f"`{e.name}`" for e in cls))
        lines.append("")
        return lines
    if dataclasses.is_dataclass(cls):
        lines.append("Fields:")
        for f in dataclasses.fields(cls):
            tname = getattr(f.type, "__name__", str(f.type))
            lines.append(f"- `{f.name}: {tname}`")
        lines.append("")
    methods = [
        (n, m) for n, m in inspect.getmembers(cls, predicate=inspect.isfunction)
        if not n.startswith("_") or n == "__init__"
    ]
    if not dataclasses.is_dataclass(cls):
        methods = [(n, m) for (n, m) in methods]
    else:
        methods = [(n, m) for (n, m) in methods if n != "__init__"]
    for name, meth in methods:
        d = _first_line(meth)
        lines.append(f"- `{name}{_sig(meth)}`" + (f" \u2014 {d}" if d else ""))
    lines.append("")
    return lines


def _document_module(name: str) -> str | None:
    try:
        module = importlib.import_module(name)
    except Exception as exc:  # noqa: BLE001
        return None if name == "__main__" else (
            f"# `{name}`\n\n{BACKLINK}\n\n*Could not import: "
            f"{type(exc).__name__}: {str(exc)[:200]}*\n"
        )
    exported = getattr(module, "__all__", None)
    members = {}
    if exported:
        for n in exported:
            members[n] = getattr(module, n, None)
    else:
        for n, obj in inspect.getmembers(module):
            if n.startswith("_"):
                continue
            if (inspect.isclass(obj) or inspect.isfunction(obj)) and _is_local(obj, module):
                members[n] = obj
    classes = {n: o for n, o in members.items() if inspect.isclass(o)}
    funcs = {n: o for n, o in members.items() if inspect.isfunction(o)}

    out = [f"# `{name}`", "", BACKLINK, ""]
    mdoc = inspect.getdoc(module)
    if mdoc:
        out += [mdoc, ""]
    if classes:
        out += ["## Classes", ""]
        for cn in sorted(classes):
            out += _document_class(classes[cn])
    if funcs:
        out += ["## Functions", ""]
        for fn in sorted(funcs):
            d = _first_line(funcs[fn])
            out.append(f"### `{fn}{_sig(funcs[fn])}`")
            out.append("")
            if d:
                out += [d, ""]
    if not classes and not funcs:
        out += ["*No public classes or functions.*", ""]
    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    targets = _targets()
    written: list[str] = []
    for name in targets:
        md = _document_module(name)
        if md is None:
            continue
        path = OUT_DIR / (name.replace(".", "_") + ".md")
        path.write_text(md, encoding="utf-8")
        written.append(name)

    index = [
        "# API Reference", "", BACKLINK, "",
        "Auto-generated from package docstrings by "
        "[`scripts/build_api_docs.py`](../../scripts/build_api_docs.py). "
        "Regenerate with `python scripts/build_api_docs.py`.", "",
        "## Modules", "",
    ]
    for name in written:
        index.append(f"- [`{name}`]({name.replace('.', '_')}.md)")
    index.append("")
    (OUT_DIR / "README.md").write_text("\n".join(index), encoding="utf-8")
    print(f"Wrote {len(written)} API pages + index to {OUT_DIR.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
