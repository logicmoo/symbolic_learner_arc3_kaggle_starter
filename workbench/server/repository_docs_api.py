from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import threading
import time
from datetime import datetime, timezone
from fnmatch import fnmatch
from pathlib import Path, PurePosixPath

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from resource_store import get_filesystem_provider
from workflow_providers import _llm_complete

router = APIRouter(prefix="/repository", tags=["repository-docs"])
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
IGNORED_DIRECTORIES = {".git", ".venv", ".codex-tmp", "node_modules", "dist", "build", "__pycache__", "action_trees", ".pytest_cache"}
VIEWABLE_SUFFIXES = {".md", ".py", ".json", ".metta", ".toml", ".txt", ".bat", ".pl", ".html", ".css", ".tsx", ".ts", ".js", ".mjs", ".yml", ".yaml", ".ipynb"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
VIEWABLE_NAMES = {"Makefile", ".gitattributes", ".gitignore", ".env.example"}
FILESYSTEM_INDEX_CACHE_TTL_SECONDS = 30.0
_filesystem_index_cache_lock = threading.RLock()
_filesystem_index_cache: dict[
    tuple[str, str, str],
    tuple[float, int, dict[str, object]],
] = {}
SENSITIVE_PATTERNS = {
    ".env", ".env.*", "*.key", "*.pem", "*.p12", "*.pfx", "*.jks",
    "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519", "credentials.json",
    "credentials.*.json", "secrets.json", "secrets.*", "*.kdbx",
}
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


class RepositoryFileUpdate(BaseModel):
    content: str


class RepositorySummaryRequest(BaseModel):
    paths: list[str]
    model: str | None = None
    workspaceId: str | None = None
    lineCount: int = 10


def repair_display_text(content: str) -> str:
    for broken, intended in MOJIBAKE_REPLACEMENTS.items():
        content = content.replace(broken, intended)
    return content


def _file_revision(stat: object) -> str:
    """Cheap change token for indexes; content is hashed only when opened."""
    size = int(getattr(stat, "st_size"))
    modified_ns = int(getattr(stat, "st_mtime_ns", round(float(getattr(stat, "st_mtime")) * 1_000_000_000)))
    return hashlib.sha256(f"{size}:{modified_ns}".encode("ascii")).hexdigest()


def _exclusion_reason(relative: Path) -> str | None:
    if any(part in IGNORED_DIRECTORIES for part in relative.parts[:-1]):
        return "generated, dependency, or internal directory"
    name = relative.name
    lower_name = name.lower()
    if name not in VIEWABLE_NAMES and any(fnmatch(lower_name, pattern) for pattern in SENSITIVE_PATTERNS):
        return "potential credentials or private key material"
    if relative.suffix.lower() not in VIEWABLE_SUFFIXES | IMAGE_SUFFIXES and name not in VIEWABLE_NAMES:
        return "file type is not approved for browser display"
    return None


def _entry(target: Path, *, exposed: bool, reason: str | None = None) -> dict[str, object]:
    relative = target.relative_to(REPOSITORY_ROOT)
    stat = target.stat()
    entry: dict[str, object] = {
        "path": relative.as_posix(),
        "name": target.name,
        "size": stat.st_size,
        "modified": stat.st_mtime,
        "exposed": exposed,
    }
    if exposed:
        entry["checksum"] = _file_revision(stat)
    else:
        entry["reason"] = reason or "not exposed"
    return entry


def _repository_scan_root(directory: str) -> tuple[Path, str]:
    resources = get_filesystem_provider()
    normalized = directory.strip().replace("\\", "/").strip("/")
    try:
        target = resources.resolve(REPOSITORY_ROOT, normalized or ".")
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Scan directory must stay inside the repository") from error
    if not resources.is_dir(target):
        raise HTTPException(status_code=404, detail=f"Repository directory does not exist: {normalized or '.'}")
    return target, normalized


def _scan_masks(raw: str) -> list[str]:
    masks = [value.strip().replace("\\", "/") for value in raw.split("|")]
    for mask in masks:
        if not mask:
            continue
        path = PurePosixPath(mask.strip("/"))
        if path.is_absolute() or ".." in path.parts:
            raise HTTPException(status_code=400, detail="Scan masks must stay inside the start directory")
    return [mask for mask in masks if mask]


def _matches_scan_mask(path: str, mask: str) -> bool:
    normalized_path = path.replace("\\", "/")
    normalized_mask = mask.strip("/")
    if any(token in normalized_mask for token in "*?[]"):
        candidate = PurePosixPath(normalized_path.strip("/"))
        return candidate.match(normalized_mask) or PurePosixPath(f"_/{candidate}").match(normalized_mask)
    return normalized_mask.lower() in normalized_path.lower()


def _git_repository_scan_roots(
    start: Path,
    directory_masks: list[str],
    exclude_masks: list[str],
) -> list[Path]:
    if not (REPOSITORY_ROOT / ".git").is_dir():
        return []
    try:
        start_relative = start.relative_to(REPOSITORY_ROOT).as_posix()
    except ValueError:
        return []
    prefix = "" if start_relative == "." else f"{start_relative}/"
    pathspecs = [
        f":(glob){prefix}{mask.strip('/')}/**"
        for mask in directory_masks
    ]
    try:
        completed = subprocess.run(
            ["git", "-C", str(REPOSITORY_ROOT), "ls-files", "--cached", "--others", "--exclude-standard", "--", *pathspecs],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    roots: set[Path] = set()
    for raw in completed.stdout.splitlines():
        target = REPOSITORY_ROOT / raw
        if not target.is_file():
            continue
        parent = target.parent
        while parent != start and start in parent.parents:
            relative = f"{parent.relative_to(start).as_posix()}/"
            if any(_matches_scan_mask(relative, mask) for mask in directory_masks):
                if not any(_matches_scan_mask(relative, mask) for mask in exclude_masks):
                    roots.add(parent)
                break
            parent = parent.parent

    # Nested plugin repositories and disabled vendor trees may not be expanded
    # by the outer Git index. Probe their one-level package roots directly.
    terminal_names = {
        PurePosixPath(mask.strip("/")).name
        for mask in directory_masks
        if not any(token in PurePosixPath(mask.strip("/")).name for token in "*?[]")
    }
    resources = get_filesystem_provider()
    collections = [
        REPOSITORY_ROOT / "workbench" / "plugins",
        REPOSITORY_ROOT / "workbench" / "workspaces",
        REPOSITORY_ROOT / "vendor",
    ]
    for name in terminal_names:
        direct = start / name
        if resources.is_dir(direct):
            relative = f"{direct.relative_to(start).as_posix()}/"
            if not any(_matches_scan_mask(relative, mask) for mask in exclude_masks):
                roots.add(direct)
        for collection in collections:
            if not resources.is_dir(collection) or (collection != start and start not in collection.parents):
                continue
            for child in resources.iterdir(collection):
                candidate = child / name
                if not resources.is_dir(candidate):
                    continue
                relative = f"{candidate.relative_to(start).as_posix()}/"
                if any(_matches_scan_mask(relative, mask) for mask in directory_masks) and not any(
                    _matches_scan_mask(relative, mask) for mask in exclude_masks
                ):
                    roots.add(candidate)
    return sorted(roots, key=lambda path: path.as_posix().lower())


def _repository_scan_roots(start: Path, include: str, exclude: str) -> tuple[list[Path], list[str], list[str]]:
    include_masks = _scan_masks(include)
    exclude_masks = _scan_masks(exclude)
    directory_masks = [mask for mask in include_masks if mask.endswith("/")]
    if not directory_masks:
        return [start], include_masks, exclude_masks
    indexed_roots = _git_repository_scan_roots(start, directory_masks, exclude_masks)
    if indexed_roots:
        return indexed_roots, include_masks, exclude_masks
    matches: list[Path] = []
    for directory, names, _files in os.walk(start):
        current = Path(directory)
        retained: list[str] = []
        for name in names:
            child = current / name
            if name in IGNORED_DIRECTORIES:
                continue
            relative = f"{child.relative_to(start).as_posix()}/"
            if any(_matches_scan_mask(relative, mask) for mask in exclude_masks):
                continue
            if any(_matches_scan_mask(relative, mask) for mask in directory_masks):
                matches.append(child)
                # The matched root is indexed below; no need to discover nested
                # roots inside it as a separate scan.
                continue
            retained.append(name)
        names[:] = retained
    return sorted(set(matches), key=lambda path: path.as_posix().lower()), include_masks, exclude_masks


def _clear_filesystem_index_cache() -> None:
    with _filesystem_index_cache_lock:
        _filesystem_index_cache.clear()


@router.get("/filesystem-index")
def list_repository_filesystem(
    directory: str = "",
    include: str = "",
    exclude: str = "",
    refresh: bool = False,
) -> dict[str, object]:
    """Inventory browser-safe files and disclose exclusions without file contents."""
    resources = get_filesystem_provider()
    start, normalized = _repository_scan_root(directory)
    normalized_include = "|".join(_scan_masks(include))
    normalized_exclude = "|".join(_scan_masks(exclude))
    cache_key = (str(start).lower(), normalized_include, normalized_exclude)
    revision = resources.revision
    now = time.monotonic()
    if not refresh:
        with _filesystem_index_cache_lock:
            cached = _filesystem_index_cache.get(cache_key)
        if cached and cached[1] == revision and now - cached[0] <= FILESYSTEM_INDEX_CACHE_TTL_SECONDS:
            return {**cached[2], "cached": True}
    scan_roots, include_masks, exclude_masks = _repository_scan_roots(
        start,
        normalized_include,
        normalized_exclude,
    )
    file_include_masks = [mask for mask in include_masks if not mask.endswith("/")]
    files: list[dict[str, object]] = []
    unexposed: list[dict[str, object]] = []
    seen: set[Path] = set()
    for scan_root in scan_roots:
        for target in resources.rglob(scan_root, "*", ignored_names=IGNORED_DIRECTORIES):
            if target in seen:
                continue
            seen.add(target)
            relative = target.relative_to(REPOSITORY_ROOT)
            relative_text = relative.as_posix()
            if file_include_masks and not any(_matches_scan_mask(relative_text, mask) for mask in file_include_masks):
                continue
            if any(_matches_scan_mask(relative_text, mask) for mask in exclude_masks):
                continue
            reason = _exclusion_reason(relative)
            if reason:
                unexposed.append(_entry(target, exposed=False, reason=reason))
            else:
                files.append(_entry(target, exposed=True))
    files.sort(key=lambda item: str(item["path"]).lower())
    unexposed.sort(key=lambda item: str(item["path"]).lower())
    payload: dict[str, object] = {
        "root": str(REPOSITORY_ROOT),
        "scope": normalized,
        "include": "|".join(include_masks),
        "exclude": "|".join(exclude_masks),
        "scanRoots": [path.relative_to(REPOSITORY_ROOT).as_posix() for path in scan_roots],
        "files": files,
        "unexposed": unexposed,
        "cached": False,
    }
    with _filesystem_index_cache_lock:
        expired_keys = [
            key
            for key, cached in _filesystem_index_cache.items()
            if time.monotonic() - cached[0] > FILESYSTEM_INDEX_CACHE_TTL_SECONDS
        ]
        for key in expired_keys:
            _filesystem_index_cache.pop(key, None)
        _filesystem_index_cache[cache_key] = (time.monotonic(), revision, payload)
    return payload


@router.get("/markdown-index")
def list_repository_markdown() -> dict[str, object]:
    resources = get_filesystem_provider()
    documents: list[dict[str, object]] = []
    for target in resources.rglob(REPOSITORY_ROOT, "*.md", ignored_names=IGNORED_DIRECTORIES):
        relative = target.relative_to(REPOSITORY_ROOT)
        if any(part in IGNORED_DIRECTORIES for part in relative.parts):
            continue
        stat = resources.stat(target)
        documents.append({
            "path": relative.as_posix(),
            "name": target.name,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "checksum": _file_revision(stat),
        })
    documents.sort(key=lambda item: str(item["path"]).lower())
    return {"root": str(REPOSITORY_ROOT), "documents": documents}


@router.get("/markdown")
def read_repository_markdown(path: str = Query(..., min_length=1)) -> dict[str, str]:
    resources = get_filesystem_provider()
    try:
        target = resources.resolve(REPOSITORY_ROOT, path)
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Markdown path must stay inside the repository") from error
    try:
        target.relative_to(REPOSITORY_ROOT)
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Markdown path must stay inside the repository") from error
    if target.suffix.lower() != ".md":
        raise HTTPException(status_code=400, detail="Only Markdown documents can be read")
    if not resources.is_file(target):
        raise HTTPException(status_code=404, detail=f"Markdown document not found: {path}")
    return {"path": target.relative_to(REPOSITORY_ROOT).as_posix(), "content": repair_display_text(resources.read_text(target))}


@router.get("/file")
def read_repository_file(path: str = Query(..., min_length=1)) -> dict[str, str]:
    resources = get_filesystem_provider()
    try:
        target = resources.resolve(REPOSITORY_ROOT, path)
    except ValueError as error:
        raise HTTPException(status_code=400, detail="File path must stay inside the repository") from error
    try:
        target.relative_to(REPOSITORY_ROOT)
    except ValueError as error:
        raise HTTPException(status_code=400, detail="File path must stay inside the repository") from error
    reason = _exclusion_reason(target.relative_to(REPOSITORY_ROOT))
    if reason:
        raise HTTPException(status_code=403, detail=f"This repository file is not exposed: {reason}")
    if not resources.is_file(target):
        raise HTTPException(status_code=404, detail=f"Repository file not found: {path}")
    if target.suffix.lower() in IMAGE_SUFFIXES:
        stat = resources.stat(target)
        return {
            "path": target.relative_to(REPOSITORY_ROOT).as_posix(),
            "content": "",
            "format": "image",
            "checksum": _file_revision(stat),
            "contentChecksum": "",
        }
    if resources.stat(target).st_size > 5_000_000:
        raise HTTPException(status_code=413, detail="Repository file is too large to display")
    stat = resources.stat(target)
    display_content = repair_display_text(resources.read_text(target))
    return {
        "path": target.relative_to(REPOSITORY_ROOT).as_posix(),
        "content": display_content,
        "format": "markdown" if target.suffix.lower() == ".md" else "source",
        "checksum": _file_revision(stat),
        "contentChecksum": hashlib.sha256(display_content.encode("utf-8")).hexdigest(),
    }


@router.get("/asset")
def read_repository_asset(path: str = Query(..., min_length=1)) -> FileResponse:
    resources = get_filesystem_provider()
    try:
        target = resources.resolve(REPOSITORY_ROOT, path)
        relative = target.relative_to(REPOSITORY_ROOT)
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Asset path must stay inside the repository") from error
    reason = _exclusion_reason(relative)
    action_tree_image = (
        len(relative.parts) >= 1
        and relative.parts[0] == "action_trees"
        and target.suffix.lower() in IMAGE_SUFFIXES
    )
    if (reason and not action_tree_image) or target.suffix.lower() not in IMAGE_SUFFIXES:
        raise HTTPException(status_code=403, detail="This repository asset is not exposed")
    if not resources.is_file(target):
        raise HTTPException(status_code=404, detail=f"Repository asset not found: {path}")
    return FileResponse(target)


@router.put("/file")
def update_repository_file(payload: RepositoryFileUpdate, path: str = Query(..., min_length=1)) -> dict[str, str]:
    resources = get_filesystem_provider()
    try:
        target = resources.resolve(REPOSITORY_ROOT, path)
        relative = target.relative_to(REPOSITORY_ROOT)
    except ValueError as error:
        raise HTTPException(status_code=400, detail="File path must stay inside the repository") from error
    reason = _exclusion_reason(relative)
    if reason:
        raise HTTPException(status_code=403, detail=f"This repository file is not exposed: {reason}")
    suffix = target.suffix.lower()
    if suffix not in VIEWABLE_SUFFIXES and target.name not in VIEWABLE_NAMES:
        raise HTTPException(status_code=400, detail="Only exposed text and source files can be edited here")
    if not resources.is_file(target):
        raise HTTPException(status_code=404, detail=f"Repository file not found: {path}")
    if len(payload.content.encode("utf-8")) > 5_000_000:
        raise HTTPException(status_code=413, detail="Repository file is too large to save")
    if suffix in {".json", ".ipynb"}:
        try:
            json.loads(payload.content)
        except json.JSONDecodeError as error:
            raise HTTPException(status_code=422, detail=f"Invalid JSON at line {error.lineno}, column {error.colno}") from error
    resources.write_text(target, payload.content)
    _clear_filesystem_index_cache()
    return read_repository_file(path)


@router.post("/summarize-files")
def summarize_repository_files(payload: RepositorySummaryRequest) -> dict[str, str]:
    """Ask the configured LLM to group and explain exposed files, then persist Markdown."""
    resources = get_filesystem_provider()
    requested = list(dict.fromkeys(str(path).strip() for path in payload.paths if str(path).strip()))
    if not requested:
        raise HTTPException(status_code=400, detail="Select at least one exposed file")
    if len(requested) > 200:
        raise HTTPException(status_code=400, detail="Summaries are limited to 200 files per request")
    line_count = max(1, min(200, int(payload.lineCount)))
    records: list[dict[str, object]] = []
    total_characters = 0
    for logical_path in requested:
        try:
            target = resources.resolve(REPOSITORY_ROOT, logical_path)
            relative = target.relative_to(REPOSITORY_ROOT)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=f"Invalid repository path: {logical_path}") from error
        reason = _exclusion_reason(relative)
        if reason:
            raise HTTPException(status_code=403, detail=f"Cannot summarize unexposed file {logical_path}: {reason}")
        if not resources.is_file(target):
            raise HTTPException(status_code=404, detail=f"Repository file not found: {logical_path}")
        excerpt = ""
        if target.suffix.lower() not in IMAGE_SUFFIXES and total_characters < 120_000:
            excerpt = "\n".join(repair_display_text(resources.read_text(target)).splitlines()[:line_count])
            excerpt = excerpt[:12_000]
            total_characters += len(excerpt)
        records.append({"path": relative.as_posix(), "bytes": resources.stat(target).st_size, "excerpt": excerpt})
    prompt = (
        "Create a useful Markdown guide to the supplied repository files. Group files by their actual purpose, "
        "explain what each file is for in one or two concrete sentences, describe important relationships between "
        "groups, and include every supplied path exactly once. Do not invent files or claim behavior absent from the "
        f"path or the supplied first {line_count} lines. Use headings and linked file paths. Return Markdown only, beginning with '# File List Summary'.\n\n"
        + json.dumps(records, ensure_ascii=False)
    )
    parameters: dict[str, object]
    if payload.model:
        from operation_resolution import _model_execution_parameters
        from workspace_api import _resolve_workspace

        try:
            workspace = _resolve_workspace(payload.workspaceId or "shared_library_system")
            parameters = _model_execution_parameters(Path(workspace["root"]), {"models": [payload.model], "strategy": "single"})
            parameters["timeoutSeconds"] = 180
        except Exception as error:
            raise HTTPException(status_code=400, detail=f"Selected summary model is unavailable: {error}") from error
    else:
        parameters = {
            "baseUrlEnvironmentVariable": "OPENAI_BASE_URL",
            "apiKeyEnv": os.getenv("WORKBENCH_LLM_API_KEY_ENV", "OPENAI_API_KEY"),
            "model": os.getenv("WORKBENCH_LLM_MODEL", os.getenv("OPENAI_MODEL", "gpt-4.1-mini")),
            "temperature": 0,
            "timeoutSeconds": 180,
        }
    try:
        result = _llm_complete(
            {"prompt": prompt},
            parameters,
        )
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"LLM file summary failed: {error}") from error
    markdown = str(result.get("text") or "").strip()
    markdown = re.sub(r"^```(?:markdown|md)?\s*", "", markdown, flags=re.IGNORECASE)
    markdown = re.sub(r"\s*```$", "", markdown).strip()
    if not markdown:
        raise HTTPException(status_code=502, detail="LLM returned an empty file summary")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    relative_output = Path("workbench/docs/generated") / f"FILE_LIST_SUMMARY_{stamp}.md"
    target_output = REPOSITORY_ROOT / relative_output
    content = "[← Back to repository README](../../../README.md)\n\n" + markdown + "\n"
    resources.write_text(target_output, content)
    _clear_filesystem_index_cache()
    return read_repository_file(relative_output.as_posix())
