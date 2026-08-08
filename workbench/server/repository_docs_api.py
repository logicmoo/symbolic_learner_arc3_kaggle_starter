from __future__ import annotations

import hashlib
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/repository", tags=["repository-docs"])
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
IGNORED_DIRECTORIES = {".git", ".venv", "node_modules", "dist", "build", "__pycache__", "action_trees"}
VIEWABLE_SUFFIXES = {".md", ".py", ".json", ".toml", ".txt", ".bat", ".pl", ".html", ".css", ".tsx", ".ts", ".js", ".mjs", ".yml", ".yaml", ".ipynb"}
VIEWABLE_NAMES = {"Makefile", ".gitattributes", ".gitignore", ".env.example"}
MOJIBAKE_REPLACEMENTS = {
    "\u00e2\u2020\u0090": "←",
    "\u00e2\u2020\u2019": "→",
    "\u00e2\u201d\u0153": "├",
    "\u00e2\u201d\u20ac": "─",
    "\u00e2\u201d\u201d": "└",
    "\u00e2\u2030\u02c6": "≈",
    "\u00e2\u20ac\u0153": "“",
    "\u00e2\u20ac\u009d": "”",
    "\u00e2\u20ac\u201d": "—",
    "\u00e2\u0153\u201c": "✓",
    "\u00c2\u00b7": "·",
}


def repair_display_text(content: str) -> str:
    for broken, intended in MOJIBAKE_REPLACEMENTS.items():
        content = content.replace(broken, intended)
    return content


@router.get("/markdown-index")
def list_repository_markdown() -> dict[str, object]:
    documents: list[dict[str, object]] = []
    for target in REPOSITORY_ROOT.rglob("*.md"):
        relative = target.relative_to(REPOSITORY_ROOT)
        if any(part in IGNORED_DIRECTORIES for part in relative.parts):
            continue
        stat = target.stat()
        display_content = repair_display_text(target.read_text(encoding="utf-8"))
        documents.append({
            "path": relative.as_posix(),
            "name": target.name,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "checksum": hashlib.sha256(display_content.encode("utf-8")).hexdigest(),
        })
    documents.sort(key=lambda item: str(item["path"]).lower())
    return {"root": str(REPOSITORY_ROOT), "documents": documents}


@router.get("/markdown")
def read_repository_markdown(path: str = Query(..., min_length=1)) -> dict[str, str]:
    target = (REPOSITORY_ROOT / path).resolve()
    try:
        target.relative_to(REPOSITORY_ROOT)
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Markdown path must stay inside the repository") from error
    if target.suffix.lower() != ".md":
        raise HTTPException(status_code=400, detail="Only Markdown documents can be read")
    if not target.is_file():
        raise HTTPException(status_code=404, detail=f"Markdown document not found: {path}")
    return {"path": target.relative_to(REPOSITORY_ROOT).as_posix(), "content": repair_display_text(target.read_text(encoding="utf-8"))}


@router.get("/file")
def read_repository_file(path: str = Query(..., min_length=1)) -> dict[str, str]:
    target = (REPOSITORY_ROOT / path).resolve()
    try:
        target.relative_to(REPOSITORY_ROOT)
    except ValueError as error:
        raise HTTPException(status_code=400, detail="File path must stay inside the repository") from error
    if target.suffix.lower() not in VIEWABLE_SUFFIXES and target.name not in VIEWABLE_NAMES:
        raise HTTPException(status_code=400, detail="This repository file type cannot be displayed")
    if not target.is_file():
        raise HTTPException(status_code=404, detail=f"Repository file not found: {path}")
    if target.stat().st_size > 5_000_000:
        raise HTTPException(status_code=413, detail="Repository file is too large to display")
    display_content = repair_display_text(target.read_text(encoding="utf-8"))
    return {
        "path": target.relative_to(REPOSITORY_ROOT).as_posix(),
        "content": display_content,
        "format": "markdown" if target.suffix.lower() == ".md" else "source",
        "checksum": hashlib.sha256(display_content.encode("utf-8")).hexdigest(),
    }
