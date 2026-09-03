"""Video import: download a video the user has rights to, extract frames,
and materialize them as an ARC3-style playable recording.

The recording's moves track the characters visible in each frame: each move
adds/subtracts the number of characters on screen and can introduce new
characters by name (``ADD_CHARACTER``/``REMOVE_CHARACTER``/``FRAME`` actions
whose ``action_data`` carries the names added, the names removed, the full
cast list, and the head count).

This tool downloads only what the caller points it at; picking sources they
have the rights to import is the caller's responsibility.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import io
import json
import re
import shutil
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterator

from fastapi import APIRouter, Body, File, Form, HTTPException, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import Response, StreamingResponse

from arc3_play_api import (
    _all_game_dirs,
    _curated_games_container,
    _game_slug,
    _game_write_dir,
    _iter_recording_dirs,
    _next_ranked_saved_dir_name,
    _safe_workspace_child,
    _utc_now,
    _workspace_root,
)
from backend_library import backend_matches, load_workspace_backend_records
from model_library import resolve_model_records
from operation_resolution import _model_execution_parameters
from resource_relationships import relationship_ids
from workspace_credentials import resolve_workspace_credential

router = APIRouter(prefix="/video-import", tags=["video-import"])
_PAGE_STATE_SHARDS = {
    "memberInventories": "member_inventories.json",
    "modelResponseCache": "model_response_cache.json",
}
_page_state_locks: dict[str, threading.RLock] = {}
_page_state_locks_guard = threading.Lock()
_data_layout_lock = threading.RLock()
_migrated_data_roots: set[Path] = set()


def _page_state_lock(workspace_id: str) -> threading.RLock:
    with _page_state_locks_guard:
        return _page_state_locks.setdefault(workspace_id, threading.RLock())


def _atomic_json_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(json.dumps(value, indent=2), encoding="utf-8")
        # On Windows os.replace fails with WinError 5 (access denied) when another
        # process momentarily holds the target open for reading (e.g. a concurrent
        # GET page-state, or the headless pipeline writing while the API serves the
        # same file). Retry the rename briefly to ride out that sharing window.
        last_error: OSError | None = None
        for attempt in range(10):
            try:
                temporary.replace(path)
                return
            except PermissionError as error:  # WinError 5 / 32 sharing race
                last_error = error
                time.sleep(0.05 * (attempt + 1))
        if last_error is not None:
            raise last_error
    finally:
        temporary.unlink(missing_ok=True)


def _shard_is_empty(value: Any) -> bool:
    """A shard payload with nothing worth persisting (None or an empty container)."""
    if value is None:
        return True
    if isinstance(value, (list, dict, str)):
        return len(value) == 0
    return False


def _shard_file_has_data(path: Path) -> bool:
    """True when an existing shard file holds real (non-empty) data."""
    if not path.is_file():
        return False
    try:
        existing = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return not _shard_is_empty(existing)

_VIDEO_SUFFIXES = {".mp4", ".webm", ".mkv", ".mov", ".avi", ".m4v"}
_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}
_IMAGE_ARCHIVE_MAX_FILES = 2_000
_IMAGE_ARCHIVE_MAX_ENTRY_BYTES = 64 * 1024 * 1024
_IMAGE_ARCHIVE_MAX_TOTAL_BYTES = 1024 * 1024 * 1024
_CURATED_DATA_EXCLUDES = {"videoimports", "recordings", "importables"}

# Running/finished frame-extraction jobs, polled for the progress bar.
_extract_jobs: dict[str, dict[str, Any]] = {}
# Running/finished download (import) jobs, polled for the import progress bar.
_download_jobs: dict[str, dict[str, Any]] = {}
_video_meta_locks: dict[Path, threading.Lock] = {}
_video_meta_locks_guard = threading.Lock()
_MEDIAMTX_IMAGE = "bluenviron/mediamtx:1.20.1"
_MEDIAMTX_CONTAINER = "workbench-mediamtx"
_STREAM_SOURCE_SCHEMES = {"http", "https", "rtsp", "rtmp", "rtmps", "srt"}


def _video_frame_source_id(root: Path, video_path: Path) -> str:
    relative = video_path.parent.resolve().relative_to(root.resolve()).as_posix()
    digest = hashlib.sha256(relative.encode("utf-8")).hexdigest()[:8]
    return f"{_slug(video_path.parent.name)}-{digest}"


def _rewrite_data_paths(paths: list[Path], replacements: list[tuple[str, str]]) -> None:
    for base in paths:
        if not base.is_dir():
            continue
        for path in base.rglob("*.json"):
            source = path.read_text(encoding="utf-8")
            migrated = source
            for old, new in replacements:
                migrated = migrated.replace(old, new)
            if migrated != source:
                path.write_text(migrated, encoding="utf-8")


def _imports_root(root: Path) -> Path:
    resolved_root = root.resolve()
    canonical = root / "data" / "video_import"
    legacy = root / "data" / "VideoImports"
    vision_root = root / "data" / "vision_frames"
    with _data_layout_lock:
        if resolved_root in _migrated_data_roots:
            return canonical
        replacements = [
            ("data/VideoImports/", "data/video_import/"),
            ("data/Recordings/", "data/arc3_games/recordings/"),
            ("data/importables/", "data/arc3_games/importables/"),
        ]
        if legacy.is_dir() and not canonical.exists():
            legacy.rename(canonical)
        canonical.mkdir(parents=True, exist_ok=True)
        for child in list(canonical.iterdir()):
            frames_dir = child / "frames"
            video_path = next(
                (
                    entry
                    for entry in child.iterdir()
                    if entry.is_file() and entry.suffix.lower() in _VIDEO_SUFFIXES
                ),
                None,
            ) if child.is_dir() else None
            if video_path is None or not frames_dir.is_dir():
                continue
            destination = vision_root / "video" / _video_frame_source_id(root, video_path)
            if not destination.exists():
                destination.parent.mkdir(parents=True, exist_ok=True)
                frames_dir.rename(destination)
                replacements.append(
                    (
                        f"data/video_import/{child.name}/frames/",
                        f"data/vision_frames/video/{destination.name}/",
                    )
                )
        curated_root = root / "data" / "arc3_games" / "curated"
        if curated_root.is_dir():
            replacements.extend(
                (
                    f"data/{child.name}/",
                    f"data/arc3_games/curated/{child.name}/",
                )
                for child in curated_root.iterdir()
                if child.is_dir()
            )
        _rewrite_data_paths([canonical, vision_root], replacements)
        _migrated_data_roots.add(resolved_root)
    return canonical


def _vision_frames_root(root: Path) -> Path:
    path = root / "data" / "vision_frames"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _video_frames_dir(root: Path, video_path: Path) -> Path:
    return _vision_frames_root(root) / "video" / _video_frame_source_id(root, video_path)


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", value).strip("-").lower()
    return cleaned or uuid.uuid4().hex[:8]


def _multipart_body(fields: dict[str, str], files: dict[str, tuple[str, str, bytes]]) -> tuple[str, bytes]:
    boundary = f"----workbench-{uuid.uuid4().hex}"
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.extend((
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
            value.encode(),
            b"\r\n",
        ))
    for name, (filename, content_type, data) in files.items():
        chunks.extend((
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode(),
            f"Content-Type: {content_type}\r\n\r\n".encode(),
            data,
            b"\r\n",
        ))
    chunks.append(f"--{boundary}--\r\n".encode())
    return boundary, b"".join(chunks)


def _model_provider_parameters(workspace_root: Path, model_id: str) -> dict[str, Any]:
    parameters = _model_execution_parameters(workspace_root, {"models": [model_id], "strategy": "single"})
    if parameters.get("baseUrl"):
        return parameters
    model_record = next(
        (
            record for record in resolve_model_records(workspace_root)
            if str((record.get("document") or {}).get("id") or "") == model_id
        ),
        None,
    )
    model_document = (model_record or {}).get("document") or {}
    discovery = model_document.get("discovery") if isinstance(model_document.get("discovery"), dict) else {}
    backend_ids = [
        str(discovery.get("backendId") or ""),
        *relationship_ids(model_document.get("implements")),
        *relationship_ids(model_document.get("dependsOn")),
    ]
    backend_record = next(
        (
            record for record in load_workspace_backend_records(workspace_root)
            if any(backend_id and backend_matches(record.get("document") or {}, backend_id) for backend_id in backend_ids)
        ),
        None,
    )
    backend = (backend_record or {}).get("document") or {}
    configuration = backend.get("configuration") if isinstance(backend.get("configuration"), dict) else {}
    return {
        **parameters,
        "model": model_document.get("model") or parameters.get("model") or model_id,
        "baseUrl": configuration.get("baseUrl"),
        "apiKeyEnv": configuration.get("apiKeyEnvironmentVariable") or configuration.get("apiKeyEnvironment"),
        "timeoutSeconds": configuration.get("timeoutSeconds"),
    }


def _try_model_image_edit(
    workspace_root: Path,
    model_id: str,
    source_image: Any,
    edit_mask: Any,
    prompt: str,
) -> tuple[Any | None, dict[str, Any]]:
    if not model_id:
        return None, {"renderer": "boundary_diffusion", "reason": "no image-output model selected"}
    parameters = _model_provider_parameters(workspace_root, model_id)
    base_url = str(parameters.get("baseUrl") or "").rstrip("/")
    remote_model = str(parameters.get("model") or model_id)
    if not base_url:
        return None, {"renderer": "boundary_diffusion", "modelId": model_id, "reason": "model backend has no base URL"}
    source_buffer = io.BytesIO()
    source_image.convert("RGBA").save(source_buffer, format="PNG")
    mask_buffer = io.BytesIO()
    edit_mask.convert("RGBA").save(mask_buffer, format="PNG")
    boundary, request_body = _multipart_body(
        {
            "model": remote_model,
            "prompt": prompt,
            "n": "1",
            "size": f"{source_image.width}x{source_image.height}",
            "response_format": "b64_json",
        },
        {
            "image": ("source.png", "image/png", source_buffer.getvalue()),
            "mask": ("mask.png", "image/png", mask_buffer.getvalue()),
        },
    )
    headers = {
        "Accept": "application/json",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "User-Agent": "MeTTaSymbolicLearnerWorkbench/0.6",
    }
    api_key_name = str(parameters.get("apiKeyEnv") or "")
    api_key = resolve_workspace_credential(workspace_root, api_key_name) if api_key_name else ""
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(
        f"{base_url}/images/edits",
        data=request_body,
        headers=headers,
        method="POST",
    )
    timeout = max(1, int(parameters.get("timeoutSeconds") or 300))
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        entry = (payload.get("data") or [{}])[0]
        artifact = entry.get("artifact") if isinstance(entry.get("artifact"), dict) else {}
        source = str(entry.get("source") or artifact.get("source") or "provider")
        metadata = {
            "renderer": "model_image_edit",
            "modelId": model_id,
            "remoteModel": remote_model,
            "source": source,
            "artifact": artifact,
            "inputs": entry.get("inputs"),
        }
        if source == "simulated":
            return None, {**metadata, "renderer": "boundary_diffusion", "reason": "provider returned a simulated image"}
        raw: bytes | None = None
        encoded = entry.get("b64_json")
        if isinstance(encoded, str) and encoded:
            raw = base64.b64decode(encoded)
        elif isinstance(entry.get("url") or artifact.get("url"), str):
            url = urllib.parse.urljoin(f"{base_url}/", str(entry.get("url") or artifact["url"]))
            with urllib.request.urlopen(url, timeout=timeout) as response:
                raw = response.read()
        if not raw:
            return None, {**metadata, "renderer": "boundary_diffusion", "reason": "provider returned no image bytes"}
        from PIL import Image  # noqa: PLC0415

        generated = Image.open(io.BytesIO(raw)).convert("RGB")
        if generated.size != source_image.size:
            return None, {
                **metadata,
                "renderer": "boundary_diffusion",
                "reason": f"provider returned {generated.size[0]}x{generated.size[1]}, expected {source_image.width}x{source_image.height}",
            }
        return generated, metadata
    except (OSError, ValueError, KeyError, json.JSONDecodeError, urllib.error.URLError) as error:
        return None, {
            "renderer": "boundary_diffusion",
            "modelId": model_id,
            "remoteModel": remote_model,
            "reason": str(error),
        }


def _ffmpeg_executable() -> str:
    executable = shutil.which("ffmpeg")
    if executable:
        return executable
    try:
        import imageio_ffmpeg  # noqa: PLC0415

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError as error:
        raise RuntimeError("ffmpeg is unavailable") from error


def _transcribe_audio_file(workspace_root: Path, model_id: str, audio_path: Path) -> str:
    parameters = _model_provider_parameters(workspace_root, model_id)
    base_url = str(parameters.get("baseUrl") or "").rstrip("/")
    remote_model = str(parameters.get("model") or model_id)
    if not base_url:
        raise RuntimeError("caption model backend has no base URL")
    boundary, request_body = _multipart_body(
        {"model": remote_model, "response_format": "json"},
        {"file": ("audio.wav", "audio/wav", audio_path.read_bytes())},
    )
    headers = {
        "Accept": "application/json",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "User-Agent": "MeTTaSymbolicLearnerWorkbench/0.6",
    }
    api_key_name = str(parameters.get("apiKeyEnv") or "")
    api_key = resolve_workspace_credential(workspace_root, api_key_name) if api_key_name else ""
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(
        f"{base_url}/audio/transcriptions",
        data=request_body,
        headers=headers,
        method="POST",
    )
    timeout = max(1, int(parameters.get("timeoutSeconds") or 300))
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    text = str(payload.get("text") or "").strip()
    if not text or text.lower().startswith("[emullm stub:"):
        raise RuntimeError("audio transcription provider returned no real transcript")
    return text


def _image_provenance_path(image_path: Path) -> Path:
    return image_path.with_suffix(".provenance.json")


def _workspace_relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _read_image_provenance(image_path: Path) -> dict[str, Any] | None:
    path = _image_provenance_path(image_path)
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _write_image_provenance(
    root: Path,
    image_path: Path,
    *,
    dimensions: tuple[int, int],
    operation: str,
    parent_image: Path | None = None,
    source: dict[str, Any] | None = None,
    transform: dict[str, Any] | None = None,
) -> dict[str, Any]:
    image_rel = _workspace_relative(root, image_path)
    size = {"width": int(dimensions[0]), "height": int(dimensions[1])}
    parent_payload = _read_image_provenance(parent_image) if parent_image else None
    if parent_image and parent_payload is None and parent_image.is_file():
        from PIL import Image  # noqa: PLC0415

        with Image.open(parent_image) as parent:
            parent_payload = _write_image_provenance(
                root,
                parent_image,
                dimensions=parent.size,
                operation="legacy_source",
                source={"path": _workspace_relative(root, parent_image)},
            )
    parent_rel = _workspace_relative(root, parent_image) if parent_image else None
    root_record = dict(parent_payload.get("root") or {}) if parent_payload else {
        "firstSeenImage": image_rel,
        "dimensions": size,
    }
    if source and not parent_payload:
        root_record.update({
            key: value
            for key, value in source.items()
            if key in {"sourceVideo", "atSeconds", "sceneIndex", "videoFrameIndex"}
        })
    step = {
        "image": image_rel,
        "operation": operation,
        "dimensions": size,
        "transform": transform or {},
        "createdAt": _utc_now(),
    }
    lineage = list(parent_payload.get("lineage") or []) if parent_payload else []
    lineage.append(step)
    payload = {
        "kind": "video_import_image_provenance",
        "version": 1,
        "image": image_rel,
        "provenance": _workspace_relative(root, _image_provenance_path(image_path)),
        "createdAt": step["createdAt"],
        "operation": operation,
        "dimensions": size,
        "originalDimensions": root_record.get("dimensions", size),
        "root": root_record,
        "parent": {
            "image": parent_rel,
            "provenance": _workspace_relative(root, _image_provenance_path(parent_image)),
        } if parent_image else None,
        "source": source or {},
        "transform": transform or {},
        "lineage": lineage,
    }
    provenance_path = _image_provenance_path(image_path)
    temporary = provenance_path.with_suffix(provenance_path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    temporary.replace(provenance_path)
    return payload


def _save_image_with_provenance(
    root: Path,
    image: Any,
    image_path: Path,
    *,
    operation: str,
    parent_image: Path | None = None,
    source: dict[str, Any] | None = None,
    transform: dict[str, Any] | None = None,
    image_format: str | None = None,
) -> dict[str, Any]:
    image_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(image_path, image_format) if image_format else image.save(image_path)
    return _write_image_provenance(
        root,
        image_path,
        dimensions=image.size,
        operation=operation,
        parent_image=parent_image,
        source=source,
        transform=transform,
    )


def _catalog_path(root: Path) -> Path:
    return _imports_root(root) / "download_catalog.json"


# Seeded with openly licensed films; the file is plain JSON the user can edit
# or extend (each entry: {title, url, note}).
_DEFAULT_CATALOG = [
    {"title": "Sintel (Blender, CC-BY)", "url": "https://www.youtube.com/watch?v=eRsGyueVLvQ",
     "note": "Animated short with real cuts and named characters"},
    {"title": "Big Buck Bunny (Blender, CC-BY)", "url": "https://www.youtube.com/watch?v=aqz-KE-bpKQ",
     "note": "Animated short, bright scenes"},
    {"title": "Elephants Dream (Blender, CC-BY)", "url": "https://www.youtube.com/watch?v=TLkA0RELQ1g",
     "note": "First open movie"},
    {"title": "Tears of Steel (Blender, CC-BY)", "url": "https://www.youtube.com/watch?v=R6MlUcmOul8",
     "note": "Live action + VFX open movie"},
]


def _append_catalog_entry(root: Path, entry: dict[str, Any]) -> None:
    """Add/refresh one catalog entry (deduped by url, then by downloadedPath)."""
    path = _catalog_path(root)
    entries: list[dict[str, Any]] = []
    if path.is_file():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            entries = loaded if isinstance(loaded, list) else []
        except (OSError, json.JSONDecodeError):
            entries = []
    else:
        entries = list(_DEFAULT_CATALOG)
    key_url = entry.get("url")
    key_path = entry.get("downloadedPath")
    kept = []
    merged = dict(entry)
    for existing in entries:
        if not isinstance(existing, dict):
            continue
        if (key_url and existing.get("url") == key_url) or (key_path and existing.get("downloadedPath") == key_path):
            merged = {**existing, **entry}
            continue
        kept.append(existing)
    kept.append(merged)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(kept, indent=2, ensure_ascii=False), encoding="utf-8")


@router.get("/catalog")
def download_catalog(workspaceId: str) -> dict[str, Any]:
    """The saved list of videos we may want to download (a combobox source).

    Every video already imported is backfilled in as an entry too, so imports
    made by upload, file path, trim, or filter all show in the catalog with
    their extraction history.
    """
    root = _workspace_root(workspaceId)
    path = _catalog_path(root)
    if not path.is_file():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(_DEFAULT_CATALOG, indent=2, ensure_ascii=False), encoding="utf-8")
    try:
        entries = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=400, detail=f"download_catalog.json is not valid JSON: {error}") from error
    if not isinstance(entries, list):
        raise HTTPException(status_code=400, detail="download_catalog.json must hold a JSON array")
    # Backfill: any imported video without a catalog entry gets one now.
    known_urls = {entry.get("url") for entry in entries if isinstance(entry, dict)}
    known_paths = {entry.get("downloadedPath") for entry in entries if isinstance(entry, dict)}
    backfilled = False
    for video in list_videos(workspaceId)["videos"]:
        if video["path"] in known_paths or (video.get("source") and video["source"] in known_urls):
            continue
        entries.append({
            "title": video["title"],
            "url": video.get("source") or "",
            "note": "imported video (auto-registered)",
            "downloadedPath": video["path"],
            "downloadedAt": video.get("importedAt") or _utc_now(),
        })
        known_paths.add(video["path"])
        backfilled = True
    if backfilled:
        path.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"entries": entries, "path": path.relative_to(root).as_posix()}


@router.post("/catalog")
def add_catalog_entry(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Append one candidate video to the download catalog (deduped by url)."""
    workspace_id = str(body.get("workspaceId") or "")
    url = str(body.get("url") or "").strip()
    title = str(body.get("title") or "").strip() or url
    note = str(body.get("note") or "").strip()
    if not workspace_id or not url:
        raise HTTPException(status_code=400, detail="workspaceId and url are required")
    root = _workspace_root(workspace_id)
    path = _catalog_path(root)
    entries: list[dict[str, Any]] = []
    if path.is_file():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            entries = loaded if isinstance(loaded, list) else []
        except (OSError, json.JSONDecodeError):
            entries = []
    else:
        entries = list(_DEFAULT_CATALOG)
    entries = [entry for entry in entries if not (isinstance(entry, dict) and entry.get("url") == url)]
    entries.append({"title": title, "url": url, **({"note": note} if note else {})})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"entries": entries, "path": path.relative_to(root).as_posix()}


def _update_catalog_for_video(root: Path, video_path: Path, updates: dict[str, Any],
                              extraction: dict[str, Any] | None = None) -> None:
    """Reflect a video's life into the download catalog entry that names it.

    Entries are matched by their download url (== the import's source) or by
    a previously recorded downloadedPath. Extraction runs are appended to the
    entry's ``extractions`` history (newest last, capped) so the catalog JSON
    tracks what has been pulled out of each candidate so far.
    """
    path = _catalog_path(root)
    if not path.is_file():
        return
    try:
        entries = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if not isinstance(entries, list):
        return
    _, meta = _video_meta(video_path)
    source = str(meta.get("source") or "")
    rel = video_path.relative_to(root).as_posix() if video_path.is_relative_to(root) else str(video_path)
    changed = False
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if entry.get("url") not in (source,) and entry.get("downloadedPath") != rel:
            continue
        entry.update(updates)
        entry["downloadedPath"] = rel
        if extraction is not None:
            history = entry.get("extractions")
            if not isinstance(history, list):
                history = []
            history.append(extraction)
            entry["extractions"] = history[-20:]
        changed = True
    if changed:
        try:
            path.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
        except OSError:
            pass


@router.get("/importables")
def list_importables(workspaceId: str) -> dict[str, Any]:
    """Loose video files dropped by hand into data/video_import/importables/.

    These are raw drops with no metadata yet; picking one in the UI starts
    the normal import process on it (copy into its own shelf + video.json)."""
    root = _workspace_root(workspaceId)
    drop = _imports_root(root) / "importables"
    drop.mkdir(parents=True, exist_ok=True)
    files = [
        {
            "path": entry.relative_to(root).as_posix(),
            "name": entry.name,
            "bytes": entry.stat().st_size,
        }
        for entry in sorted(drop.iterdir())
        if entry.is_file() and entry.suffix.lower() in _VIDEO_SUFFIXES
    ]
    return {"dropDir": drop.relative_to(root).as_posix(), "files": files}


@router.get("/page-state")
def get_page_state(workspaceId: str) -> dict[str, Any]:
    """The page's exact-state JSON, stored beside the image repository."""
    container = _imports_root(_workspace_root(workspaceId))
    path = container / "page_state.json"
    with _page_state_lock(workspaceId):
        if not path.is_file():
            return {"state": None}
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
            shards = state.pop("stateShards", {})
            if isinstance(shards, dict):
                shard_root = container / "page_state"
                for key, filename in _PAGE_STATE_SHARDS.items():
                    if shards.get(key) != filename:
                        continue
                    shard_path = shard_root / filename
                    if shard_path.is_file():
                        state[key] = json.loads(shard_path.read_text(encoding="utf-8"))
            return {"state": state}
        except (OSError, json.JSONDecodeError):
            return {"state": None}


@router.post("/page-state")
async def save_page_state(request: Request) -> dict[str, Any]:
    """Persist the page's exact-state JSON into data/video_import/page_state.json."""
    try:
        payload = await asyncio.to_thread(json.loads, await request.body())
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=400, detail="page state must be valid JSON") from error
    return await asyncio.to_thread(_save_page_state_payload, payload)


@router.post("/pipeline/start")
async def pipeline_start(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Start the headless scene-object pipeline for a workspace.

    Runs describe -> group -> outline -> extract server-side so the work no
    longer depends on a browser tab. The page (if open) becomes a status viewer.
    """
    workspace_id = str(payload.get("workspaceId") or "")
    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspaceId is required")
    from video_import_pipeline import start_run

    concurrency = payload.get("concurrency")
    return await asyncio.to_thread(
        start_run,
        workspace_id,
        str(payload.get("stage") or "describe"),
        model_override=(str(payload["model"]).strip() if payload.get("model") else None),
        goal_override=(str(payload["goal"]).strip() if payload.get("goal") else None),
        only_selected=bool(payload.get("onlySelected", True)),
        concurrency_override=int(concurrency) if concurrency else None,
    )


@router.get("/pipeline/status")
def pipeline_status(workspaceId: str) -> dict[str, Any]:
    """Current headless pipeline run status for a workspace."""
    from video_import_pipeline import get_run

    run = get_run(workspaceId)
    if not run:
        return {"workspaceId": workspaceId, "status": "idle"}
    return run.snapshot()


@router.post("/pipeline/stop")
def pipeline_stop(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Request the headless pipeline run for a workspace to stop."""
    workspace_id = str(payload.get("workspaceId") or "")
    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspaceId is required")
    from video_import_pipeline import stop_run

    return {"workspaceId": workspace_id, "stopping": stop_run(workspace_id)}


@router.websocket("/pipeline/ws")
async def pipeline_ws(websocket: WebSocket) -> None:
    """Bidirectional channel for the Video Import page.

    The page subscribes with its workspaceId, then the server pushes pipeline
    status + log (so the STATUS window updates in real time with no polling) and
    accepts commands (start/stop/clear) so buttons are just messages.
    """
    await websocket.accept()
    from video_import_pipeline import get_run, start_run, stop_run

    state = {"workspaceId": "", "last_key": None, "last_state_mtime": 0.0}
    stop_flag = asyncio.Event()

    def _snapshot() -> dict[str, Any]:
        workspace_id = state["workspaceId"]
        if not workspace_id:
            return {"type": "status", "status": "idle"}
        run = get_run(workspace_id)
        snap = run.snapshot() if run else {"workspaceId": workspace_id, "status": "idle", "log": []}
        return {"type": "status", **snap}

    def _page_state_path(workspace_id: str) -> Path:
        return _imports_root(_workspace_root(workspace_id)) / "page_state.json"

    def _state_frame(workspace_id: str) -> dict[str, Any] | None:
        """The produced artifacts (inventories/members/scenes) for the gallery."""
        payload = get_page_state(workspace_id)
        page = payload.get("state") if isinstance(payload, dict) else None
        if not isinstance(page, dict):
            return None
        return {
            "type": "state",
            "workspaceId": workspace_id,
            "memberInventories": page.get("memberInventories") or [],
            "memberScenes": page.get("memberScenes") or {},
            "members": page.get("members") or [],
            "turtleArtifacts": page.get("turtleArtifacts") or {},
            "recognitions": page.get("recognitions") or {},
        }

    async def push_loop() -> None:
        # Push a status frame whenever the run status or its log length changes,
        # and a state frame (inventories/members/scenes → gallery) whenever the
        # persisted page-state changes — both without any client polling.
        while not stop_flag.is_set():
            workspace_id = state["workspaceId"]
            if workspace_id:
                snap = await asyncio.to_thread(_snapshot)
                key = (snap.get("status"), len(snap.get("log") or []))
                if key != state["last_key"]:
                    state["last_key"] = key
                    try:
                        await websocket.send_json(snap)
                    except Exception:  # noqa: BLE001 - client went away
                        stop_flag.set()
                        return
                try:
                    mtime = _page_state_path(workspace_id).stat().st_mtime
                except OSError:
                    mtime = 0.0
                if mtime != state["last_state_mtime"]:
                    state["last_state_mtime"] = mtime
                    frame = await asyncio.to_thread(_state_frame, workspace_id)
                    if frame is not None:
                        try:
                            await websocket.send_json(frame)
                        except Exception:  # noqa: BLE001
                            stop_flag.set()
                            return
            await asyncio.sleep(0.6)

    async def receive_loop() -> None:
        while not stop_flag.is_set():
            try:
                message = await websocket.receive_json()
            except WebSocketDisconnect:
                stop_flag.set()
                return
            except Exception:  # noqa: BLE001 - malformed frame; keep the socket open
                continue
            command = str(message.get("cmd") or "")
            workspace_id = str(message.get("workspaceId") or state["workspaceId"])
            state["workspaceId"] = workspace_id
            if not workspace_id:
                continue
            try:
                if command in ("subscribe", "status"):
                    state["last_key"] = None  # force an immediate push
                    state["last_state_mtime"] = 0.0  # force a gallery/state push
                elif command == "start":
                    concurrency = message.get("concurrency")
                    await asyncio.to_thread(
                        start_run,
                        workspace_id,
                        str(message.get("stage") or "full"),
                        model_override=(str(message["model"]).strip() if message.get("model") else None),
                        goal_override=(str(message["goal"]).strip() if message.get("goal") else None),
                        only_selected=bool(message.get("onlySelected", True)),
                        concurrency_override=int(concurrency) if concurrency else None,
                    )
                    state["last_key"] = None
                elif command == "stop":
                    await asyncio.to_thread(stop_run, workspace_id)
                    state["last_key"] = None
                elif command == "clear":
                    from video_import_pipeline import clear_llm_work

                    await asyncio.to_thread(clear_llm_work, workspace_id)
                    try:
                        await websocket.send_json({"type": "cleared", "workspaceId": workspace_id})
                        state["last_state_mtime"] = 0.0  # push the emptied gallery
                    except Exception:  # noqa: BLE001
                        stop_flag.set()
                        return
            except Exception as error:  # noqa: BLE001 - report, keep socket open
                try:
                    await websocket.send_json({"type": "error", "error": str(error)})
                except Exception:  # noqa: BLE001
                    stop_flag.set()
                    return

    try:
        await asyncio.gather(push_loop(), receive_loop())
    except WebSocketDisconnect:
        pass
    finally:
        stop_flag.set()




def _compact_page_state(state: dict[str, Any]) -> dict[str, Any]:
    cache = state.get("modelResponseCache")
    if not isinstance(cache, dict):
        return state
    allowed = {
        "modelId",
        "text",
        "latencyMs",
        "inputTokens",
        "outputTokens",
        "responseId",
        "backendId",
    }
    for entry in cache.values():
        if not isinstance(entry, dict):
            continue
        payload = entry.get("payload")
        if isinstance(payload, dict):
            entry["payload"] = {
                key: value for key, value in payload.items() if key in allowed
            }
    return state


def _save_page_state_payload(payload: dict[str, Any]) -> dict[str, Any]:
    workspace_id = str(payload.get("workspaceId") or "")
    state = payload.get("state")
    if not workspace_id or not isinstance(state, dict):
        raise HTTPException(status_code=400, detail="workspaceId and a state object are required")
    # Explicit, intentional shard clears (e.g. the "clear LLM work" button) must
    # bypass the empty-overwrite safety guard below.
    clear_shards_raw = payload.get("clearShards")
    force_clear = {str(key) for key in clear_shards_raw} if isinstance(clear_shards_raw, list) else set()
    state = _compact_page_state(state)
    container = _imports_root(_workspace_root(workspace_id))
    path = container / "page_state.json"
    with _page_state_lock(workspace_id):
        manifest = dict(state)
        shard_root = container / "page_state"
        for key, filename in _PAGE_STATE_SHARDS.items():
            incoming = manifest.pop(key, {})
            shard_path = shard_root / filename
            # Data-safety guard: never let an empty/blank save overwrite an
            # existing non-empty shard. A stale or freshly-loaded browser tab
            # must not be able to wipe real member-inventory / cache work by
            # auto-saving empty state. An explicit clearShards request overrides
            # this so the user can intentionally clear the work.
            if key not in force_clear and _shard_is_empty(incoming) and _shard_file_has_data(shard_path):
                continue
            _atomic_json_write(shard_path, incoming)
        manifest["stateShards"] = dict(_PAGE_STATE_SHARDS)
        _atomic_json_write(path, manifest)
    return {
        "saved": True,
        "cleared": sorted(force_clear),
        "path": str(path),
        "shards": {
            key: str((shard_root / filename).resolve())
            for key, filename in _PAGE_STATE_SHARDS.items()
        },
    }


@router.post("/select-degenerate")
def select_degenerate(payload: dict[str, Any]) -> dict[str, Any]:
    """Flag degenerate frames (all-black / flat solid-color) among the given images.

    kind: "black" (near-black), "flat" (any solid/blank color). Used by the
    YOUR PICK curation UI to pre-select junk for one-click deletion.
    """
    workspace_id = str(payload.get("workspaceId") or "")
    images = [str(item) for item in (payload.get("images") or []) if item]
    kind = str(payload.get("kind") or "black")
    if not workspace_id or not images:
        raise HTTPException(status_code=400, detail="workspaceId and images are required")
    root = _workspace_root(workspace_id)
    try:
        from PIL import Image, ImageStat  # noqa: PLC0415
    except ImportError as error:
        raise HTTPException(status_code=500, detail="Pillow is not installed in the server environment") from error
    selected: list[str] = []
    for rel in images:
        path = (root / rel).resolve()
        if root.resolve() not in path.parents or not path.is_file():
            continue
        try:
            with Image.open(path) as raw:
                gray = raw.convert("L")
                gray.thumbnail((64, 64))
                stat = ImageStat.Stat(gray)
                mean = float(stat.mean[0])
                stddev = float(stat.stddev[0])
        except OSError:
            continue
        if kind == "black" and mean <= 20.0 and stddev <= 16.0:
            selected.append(rel)
        elif kind == "flat" and stddev <= 6.0:
            selected.append(rel)
    return {"selected": selected, "count": len(selected)}


@router.get("/videos")
def list_videos(workspaceId: str) -> dict[str, Any]:
    """Every imported video plus any frames already extracted beside it."""
    root = _workspace_root(workspaceId)
    container = _imports_root(root)
    videos: list[dict[str, Any]] = []

    def collect(directory: Path) -> None:
        for entry in sorted(directory.iterdir()):
            if entry.is_file() and entry.suffix.lower() in _VIDEO_SUFFIXES:
                canonical_frames = _video_frames_dir(root, entry)
                legacy_frames = directory / "frames"
                frames_dir = canonical_frames if canonical_frames.is_dir() else legacy_frames
                frames = sorted(frames_dir.glob("frame_*.png")) if frames_dir.is_dir() else []
                meta_path = directory / "video.json"
                meta: dict[str, Any] = {}
                if meta_path.is_file():
                    try:
                        meta = json.loads(meta_path.read_text(encoding="utf-8"))
                    except (OSError, json.JSONDecodeError):
                        meta = {}
                videos.append({
                    "path": entry.relative_to(root).as_posix(),
                    "bytes": entry.stat().st_size,
                    "title": meta.get("title") or directory.name,
                    "source": meta.get("source") or "",
                    "duration": meta.get("duration"),
                    "importedAt": meta.get("downloaded_at") or meta.get("imported_at") or "",
                    "frameCount": len(frames),
                    "framesDir": frames_dir.relative_to(root).as_posix() if frames else None,
                    "lastExtract": meta.get("lastExtract"),
                    "scenes": meta.get("scenes") or [],
                    "captions": meta.get("captions") or [],
                    "captionSource": meta.get("captionSource"),
                    "segments": meta.get("segments") or [],
                })

    if container.is_dir():
        for directory in sorted(container.iterdir()):
            if not directory.is_dir():
                continue
            if directory.name == "importables":
                # The uploads shelf: one more directory level down.
                for shelf_entry in sorted(directory.iterdir()):
                    if shelf_entry.is_dir():
                        collect(shelf_entry)
                continue
            collect(directory)
    videos.sort(key=lambda video: str(video.get("importedAt") or ""), reverse=True)
    return {"videos": videos}


@router.post("/download")
def download_video(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Download one video URL into data/video_import/<slug>/.

    The caller supplies the URL and is responsible for having the rights to
    the content it names. `quality` picks the yt-dlp format ceiling (480p
    lo-fi by default, up to `best`); `tool` may be "python-direct" to fetch
    a direct video-file URL with plain Python instead of yt-dlp."""
    workspace_id = str(body.get("workspaceId") or "")
    url = str(body.get("url") or "").strip()
    requested_name = str(body.get("name") or "").strip()
    quality = str(body.get("quality") or "480p")
    tool = str(body.get("tool") or "yt-dlp")
    if not workspace_id or not url:
        raise HTTPException(status_code=400, detail="workspaceId and url are required")
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="url must be http(s)")
    root = _workspace_root(workspace_id)
    container = _imports_root(root)
    container.mkdir(parents=True, exist_ok=True)
    staging = container / f"dl_{uuid.uuid4().hex[:8]}"
    staging.mkdir(parents=True, exist_ok=True)
    info: dict[str, Any] = {}
    if tool == "python-direct":
        # Plain-Python fetch for direct video-file URLs (no yt-dlp involved).
        import urllib.request  # noqa: PLC0415
        suffix = Path(url.split("?")[0]).suffix.lower()
        if suffix not in _VIDEO_SUFFIXES:
            suffix = ".mp4"
        target = staging / f"video{suffix}"
        try:
            request_obj = urllib.request.Request(url, headers={"User-Agent": "workbench-video-import/1.0"})
            with urllib.request.urlopen(request_obj, timeout=60) as response, target.open("wb") as sink:
                shutil.copyfileobj(response, sink)
        except Exception as error:  # noqa: BLE001 - reported to the caller
            shutil.rmtree(staging, ignore_errors=True)
            raise HTTPException(status_code=400, detail=f"direct fetch failed: {error}") from error
        info = {"title": requested_name or Path(url.split("?")[0]).stem or "video"}
    else:
        try:
            import yt_dlp  # noqa: PLC0415 - optional dependency, imported on use
        except ImportError as error:
            shutil.rmtree(staging, ignore_errors=True)
            raise HTTPException(status_code=500, detail="yt-dlp is not installed in the server environment") from error
        formats = {
            "480p": "mp4[height<=480]/best[height<=480]/mp4/best",
            "720p": "mp4[height<=720]/best[height<=720]/mp4/best",
            "1080p": "mp4[height<=1080]/best[height<=1080]/mp4/best",
            "best": "mp4/best",
        }
        options = {
            "outtmpl": str(staging / "video.%(ext)s"),
            "format": formats.get(quality, formats["480p"]),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
        }
        try:
            with yt_dlp.YoutubeDL(options) as downloader:
                info = downloader.extract_info(url, download=True)
        except Exception as error:  # noqa: BLE001 - reported to the caller
            shutil.rmtree(staging, ignore_errors=True)
            raise HTTPException(status_code=400, detail=f"download failed: {error}") from error
    try:
        return _finalize_download(root, container, staging, info, url, requested_name)
    except FileNotFoundError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


def _finalize_download(
    root: Path,
    container: Path,
    staging: Path,
    info: dict[str, Any],
    url: str,
    requested_name: str,
) -> dict[str, Any]:
    """Move a completed download out of staging and record its metadata."""
    title = requested_name or str(info.get("title") or "video")
    directory = container / _slug(title)
    if directory.exists():
        directory = container / f"{_slug(title)}-{uuid.uuid4().hex[:6]}"
    staging.rename(directory)
    video_file = next(
        (entry for entry in sorted(directory.iterdir()) if entry.suffix.lower() in _VIDEO_SUFFIXES),
        None,
    )
    if video_file is None:
        raise FileNotFoundError("download completed but produced no video file")
    if not info.get("duration"):
        info["duration"] = _probe_duration_seconds(video_file)
    (directory / "video.json").write_text(
        json.dumps({
            "title": title,
            "source": url,
            "duration": info.get("duration"),
            "uploader": info.get("uploader"),
            "downloaded_at": _utc_now(),
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    result = {
        "path": video_file.relative_to(root).as_posix(),
        "title": title,
        "duration": info.get("duration"),
    }
    _update_catalog_for_video(root, video_file, {"downloadedAt": _utc_now()})
    _append_catalog_entry(root, {
        "title": title,
        "url": url,
        "downloadedPath": result["path"],
        "downloadedAt": _utc_now(),
    })
    return result


def _download_worker(
    job_id: str,
    workspace_id: str,
    url: str,
    requested_name: str,
    quality: str,
    tool: str,
) -> None:
    """Run one import in the background, reporting progress into _download_jobs."""
    job = _download_jobs[job_id]
    staging: Path | None = None
    try:
        root = _workspace_root(workspace_id)
        container = _imports_root(root)
        container.mkdir(parents=True, exist_ok=True)
        staging = container / f"dl_{uuid.uuid4().hex[:8]}"
        staging.mkdir(parents=True, exist_ok=True)
        info: dict[str, Any] = {}
        if tool == "python-direct":
            import urllib.request  # noqa: PLC0415

            suffix = Path(url.split("?")[0]).suffix.lower()
            if suffix not in _VIDEO_SUFFIXES:
                suffix = ".mp4"
            target = staging / f"video{suffix}"
            request_obj = urllib.request.Request(url, headers={"User-Agent": "workbench-video-import/1.0"})
            with urllib.request.urlopen(request_obj, timeout=60) as response, target.open("wb") as sink:
                total_header = response.headers.get("Content-Length")
                total = int(total_header) if total_header and total_header.isdigit() else None
                job.update({"totalBytes": total, "message": "downloading…"})
                downloaded = 0
                chunk = 1024 * 256
                while True:
                    if job.get("cancel"):
                        raise RuntimeError("cancelled")
                    block = response.read(chunk)
                    if not block:
                        break
                    sink.write(block)
                    downloaded += len(block)
                    percent = round(downloaded / total * 100, 1) if total else job.get("percent", 0.0)
                    job.update({
                        "downloadedBytes": downloaded,
                        "percent": percent,
                        "message": f"downloading {job.get('title') or 'video'}…",
                    })
            info = {"title": requested_name or Path(url.split("?")[0]).stem or "video"}
        else:
            import yt_dlp  # noqa: PLC0415

            formats = {
                "480p": "mp4[height<=480]/best[height<=480]/mp4/best",
                "720p": "mp4[height<=720]/best[height<=720]/mp4/best",
                "1080p": "mp4[height<=1080]/best[height<=1080]/mp4/best",
                "best": "mp4/best",
            }

            def hook(status: dict[str, Any]) -> None:
                if job.get("cancel"):
                    raise RuntimeError("cancelled")
                state = status.get("status")
                if state == "downloading":
                    total = status.get("total_bytes") or status.get("total_bytes_estimate")
                    done = status.get("downloaded_bytes") or 0
                    title = ((status.get("info_dict") or {}).get("title")) or job.get("title")
                    percent = round(done / total * 100, 1) if total else job.get("percent", 0.0)
                    update = {
                        "downloadedBytes": done,
                        "totalBytes": total,
                        "percent": percent,
                        "speedBytesPerSecond": status.get("speed"),
                        "etaSeconds": status.get("eta"),
                        "message": f"downloading {title or 'video'}…",
                    }
                    if title:
                        update["title"] = title
                    job.update(update)
                elif state == "finished":
                    job.update({"percent": 100.0, "message": "processing download…"})

            options = {
                "outtmpl": str(staging / "video.%(ext)s"),
                "format": formats.get(quality, formats["480p"]),
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
                "progress_hooks": [hook],
            }
            with yt_dlp.YoutubeDL(options) as downloader:
                info = downloader.extract_info(url, download=True)
        job.update({"state": "finalizing", "message": "finalizing import…"})
        result = _finalize_download(root, container, staging, info, url, requested_name)
        job.update({
            "state": "done",
            "percent": 100.0,
            "path": result["path"],
            "title": result["title"],
            "duration": result.get("duration"),
            "message": f"imported {result['title']}",
        })
    except Exception as error:  # noqa: BLE001 - surfaced via the job record
        if staging is not None:
            shutil.rmtree(staging, ignore_errors=True)
        job.update({"state": "error", "error": str(error), "message": f"import failed: {error}"})


@router.post("/download/start")
def download_start(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Begin a background import of one URL and return a job id to poll.

    Progress (percent, bytes, title, ETA) is reported through
    ``GET /download/status`` so the client can show an import progress bar and
    name what it is importing."""
    workspace_id = str(body.get("workspaceId") or "")
    url = str(body.get("url") or "").strip()
    requested_name = str(body.get("name") or "").strip()
    quality = str(body.get("quality") or "480p")
    tool = str(body.get("tool") or "yt-dlp")
    if not workspace_id or not url:
        raise HTTPException(status_code=400, detail="workspaceId and url are required")
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="url must be http(s)")
    if tool != "python-direct":
        try:
            import yt_dlp  # noqa: F401, PLC0415
        except ImportError as error:
            raise HTTPException(status_code=500, detail="yt-dlp is not installed in the server environment") from error
    job_id = uuid.uuid4().hex[:12]
    _download_jobs[job_id] = {
        "id": job_id,
        "state": "running",
        "percent": 0.0,
        "downloadedBytes": 0,
        "totalBytes": None,
        "speedBytesPerSecond": None,
        "etaSeconds": None,
        "title": requested_name or url,
        "tool": tool,
        "quality": quality,
        "message": "starting import…",
        "path": None,
        "duration": None,
        "error": None,
    }
    threading.Thread(
        target=_download_worker,
        args=(job_id, workspace_id, url, requested_name, quality, tool),
        name=f"video-download-{job_id}",
        daemon=True,
    ).start()
    return {"jobId": job_id, "title": requested_name or url}


@router.get("/download/status")
def download_status(jobId: str) -> dict[str, Any]:
    job = _download_jobs.get(jobId)
    if job is None:
        raise HTTPException(status_code=404, detail=f"unknown download job: {jobId}")
    return job


@router.post("/download/cancel")
def download_cancel(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    job_id = str(body.get("jobId") or "")
    job = _download_jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"unknown download job: {job_id}")
    job["cancel"] = True
    return {"jobId": job_id, "cancelling": True}


def _probe_duration_seconds(video_path: Path) -> float | None:
    """Best-effort video duration via imageio's ffmpeg metadata."""
    try:
        import imageio  # noqa: PLC0415 - optional dependency

        reader = imageio.get_reader(str(video_path))
        try:
            meta = reader.get_meta_data()
        finally:
            reader.close()
        duration = meta.get("duration")
        if duration:
            return round(float(duration), 2)
        fps = float(meta.get("fps") or 0)
        nframes = meta.get("nframes")
        if fps and isinstance(nframes, (int, float)) and nframes not in (float("inf"),):
            return round(float(nframes) / fps, 2)
    except Exception:  # noqa: BLE001 - duration stays unknown
        return None
    return None


@router.post("/import-file")
def import_file(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Import a movie already on disk: a workspace-relative or absolute path.

    The file is copied into data/video_import/<slug>/ so every imported video
    lives in one place with its metadata."""
    workspace_id = str(body.get("workspaceId") or "")
    raw_path = str(body.get("path") or "").strip().strip('"')
    requested_name = str(body.get("name") or "").strip()
    if not workspace_id or not raw_path:
        raise HTTPException(status_code=400, detail="workspaceId and path are required")
    root = _workspace_root(workspace_id)
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        try:
            candidate = _safe_workspace_child(root, raw_path)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail=f"movie file not found: {raw_path}")
    if candidate.suffix.lower() not in _VIDEO_SUFFIXES:
        raise HTTPException(status_code=400, detail=f"not a recognized movie type: {candidate.suffix}")
    title = requested_name or candidate.stem
    container = _imports_root(root)
    directory = container / _slug(title)
    if directory.exists():
        directory = container / f"{_slug(title)}-{uuid.uuid4().hex[:6]}"
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"video{candidate.suffix.lower()}"
    shutil.copyfile(candidate, target)
    duration = _probe_duration_seconds(target)
    (directory / "video.json").write_text(
        json.dumps({
            "title": title,
            "source": str(candidate),
            "duration": duration,
            "imported_at": _utc_now(),
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    result = {"path": target.relative_to(root).as_posix(), "title": title, "duration": duration}
    _append_catalog_entry(root, {
        "title": title,
        "url": str(candidate),
        "note": "imported from disk",
        "downloadedPath": result["path"],
        "downloadedAt": _utc_now(),
    })
    return result


@router.post("/upload")
async def upload_video(
    workspaceId: str = Form(...),
    name: str = Form(default=""),
    file: UploadFile = File(...),
) -> dict[str, Any]:
    """Receive a video file uploaded from the browser.

    Uploads land in their own importables/ shelf
    (data/video_import/importables/<slug>/video.<ext>) so hand-sent files are
    grouped apart from URL downloads, while still appearing in the video list."""
    root = _workspace_root(workspaceId)
    original = Path(str(file.filename or "upload.mp4")).name
    suffix = Path(original).suffix.lower()
    if suffix not in _VIDEO_SUFFIXES:
        raise HTTPException(status_code=400, detail=f"not a recognized movie type: {suffix or '(none)'}")
    title = name.strip() or Path(original).stem
    container = _imports_root(root) / "importables"
    directory = container / _slug(title)
    if directory.exists():
        directory = container / f"{_slug(title)}-{uuid.uuid4().hex[:6]}"
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"video{suffix}"
    size = 0
    with target.open("wb") as handle:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            handle.write(chunk)
    if not size:
        shutil.rmtree(directory, ignore_errors=True)
        raise HTTPException(status_code=400, detail="uploaded file was empty")
    duration = _probe_duration_seconds(target)
    (directory / "video.json").write_text(
        json.dumps({
            "title": title,
            "source": f"upload: {original}",
            "duration": duration,
            "imported_at": _utc_now(),
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    result = {"path": target.relative_to(root).as_posix(), "title": title, "duration": duration, "bytes": size}
    _append_catalog_entry(root, {
        "title": title,
        "url": f"upload: {original}",
        "note": "uploaded from the browser",
        "downloadedPath": result["path"],
        "downloadedAt": _utc_now(),
    })
    return result


def _import_image_archive(
    workspace_id: str,
    filename: str,
    file_object: Any,
) -> dict[str, Any]:
    from PIL import Image  # noqa: PLC0415

    root = _workspace_root(workspace_id)
    archive_id = _slug(Path(filename).stem or "image-archive")
    output_dir = _vision_frames_root(root) / "image_archives" / archive_id
    if output_dir.exists():
        output_dir = output_dir.parent.with_name(
            f"{archive_id}-{uuid.uuid4().hex[:6]}"
        ) / "frames"
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        archive = zipfile.ZipFile(file_object)
    except (OSError, zipfile.BadZipFile) as error:
        raise HTTPException(status_code=400, detail="uploaded file is not a valid ZIP archive") from error
    with archive:
        entries = [
            entry
            for entry in archive.infolist()
            if not entry.is_dir() and Path(entry.filename).suffix.lower() in _IMAGE_SUFFIXES
        ]
        entries.sort(key=lambda entry: entry.filename.lower())
        if not entries:
            raise HTTPException(status_code=400, detail="ZIP archive contains no supported images")
        if len(entries) > _IMAGE_ARCHIVE_MAX_FILES:
            raise HTTPException(
                status_code=413,
                detail=f"ZIP archive contains more than {_IMAGE_ARCHIVE_MAX_FILES} images",
            )
        total_bytes = sum(entry.file_size for entry in entries)
        if total_bytes > _IMAGE_ARCHIVE_MAX_TOTAL_BYTES:
            raise HTTPException(status_code=413, detail="ZIP archive image data exceeds 1 GiB")
        frames: list[dict[str, Any]] = []
        for index, entry in enumerate(entries):
            if entry.file_size > _IMAGE_ARCHIVE_MAX_ENTRY_BYTES:
                raise HTTPException(
                    status_code=413,
                    detail=f"ZIP image '{entry.filename}' exceeds 64 MiB",
                )
            if entry.compress_size and entry.file_size / entry.compress_size > 200:
                raise HTTPException(
                    status_code=413,
                    detail=f"ZIP image '{entry.filename}' has an unsafe compression ratio",
                )
            try:
                raw = archive.read(entry)
                with Image.open(io.BytesIO(raw)) as image:
                    image.load()
                    output_path = output_dir / f"frame_{index:06d}.png"
                    provenance = _save_image_with_provenance(
                        root,
                        image.convert("RGBA"),
                        output_path,
                        operation="import_image_archive_frame",
                        source={
                            "archiveName": filename,
                            "archiveEntry": entry.filename,
                            "frameIndex": index,
                        },
                        image_format="PNG",
                    )
            except (OSError, ValueError) as error:
                raise HTTPException(
                    status_code=400,
                    detail=f"ZIP entry '{entry.filename}' is not a valid image",
                ) from error
            frames.append(
                {
                    "path": output_path.relative_to(root).as_posix(),
                    "index": index,
                    "atSeconds": float(index),
                    "scene": index + 1,
                    "provenance": provenance["provenance"],
                }
            )
    manifest_path = output_dir.parent / "archive_import.json"
    _atomic_json_write(
        manifest_path,
        {
            "archiveName": filename,
            "frames": frames,
            "importedAt": _utc_now(),
        },
    )
    return {
        "archive": filename,
        "frames": frames,
        "manifest": manifest_path.relative_to(root).as_posix(),
    }


@router.post("/image-archive/upload")
async def upload_image_archive(
    workspaceId: str = Form(...),
    file: UploadFile = File(...),
) -> dict[str, Any]:
    filename = file.filename or "images.zip"
    if Path(filename).suffix.lower() != ".zip":
        raise HTTPException(status_code=400, detail="image archive must be a .zip file")
    await file.seek(0)
    return await asyncio.to_thread(
        _import_image_archive,
        workspaceId,
        filename,
        file.file,
    )


@router.get("/stream")
def stream_video(workspaceId: str, path: str, request: Request) -> Response:
    """Serve an imported video with HTTP Range support so the browser's
    <video> element can play and seek it on the timeline."""
    root = _workspace_root(workspaceId)
    try:
        video_path = _safe_workspace_child(root, path)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not video_path.is_file():
        raise HTTPException(status_code=404, detail=f"video not found: {path}")
    size = video_path.stat().st_size
    media_type = {
        ".mp4": "video/mp4", ".m4v": "video/mp4", ".webm": "video/webm",
        ".mkv": "video/x-matroska", ".mov": "video/quicktime", ".avi": "video/x-msvideo",
    }.get(video_path.suffix.lower(), "application/octet-stream")
    range_header = request.headers.get("range", "")
    start, end = 0, size - 1
    status = 200
    if range_header.startswith("bytes="):
        raw_start, _, raw_end = range_header[6:].partition("-")
        try:
            start = int(raw_start) if raw_start else 0
            end = int(raw_end) if raw_end else size - 1
        except ValueError:
            start, end = 0, size - 1
        start = max(0, min(start, size - 1))
        end = max(start, min(end, size - 1))
        status = 206

    def read_range(chunk_size: int = 1024 * 512) -> Iterator[bytes]:
        remaining = end - start + 1
        with video_path.open("rb") as handle:
            handle.seek(start)
            while remaining > 0:
                chunk = handle.read(min(chunk_size, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk

    headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(end - start + 1),
    }
    if status == 206:
        headers["Content-Range"] = f"bytes {start}-{end}/{size}"
    return StreamingResponse(read_range(), status_code=status, media_type=media_type, headers=headers)


def _scene_extraction_targets(
    markers: list[float],
    *,
    duration: float | None,
    start_seconds: float,
    end_seconds: float | None,
    start_scene: int,
    end_scene: int | None,
    skip_scenes: int,
    per_scene: int,
    scene_offset: float,
    max_frames: int,
) -> list[tuple[float, int]]:
    final_boundary = duration if duration is not None else end_seconds
    if final_boundary is None:
        return []
    boundaries = sorted({
        0.0,
        *[marker for marker in markers if 0.0 < marker < final_boundary],
        float(final_boundary),
    })
    targets: list[tuple[float, int]] = []
    stride = skip_scenes + 1
    for scene_number, (raw_start, raw_end) in enumerate(zip(boundaries, boundaries[1:]), start=1):
        if scene_number < start_scene or (end_scene is not None and scene_number > end_scene):
            continue
        if (scene_number - start_scene) % stride:
            continue
        scene_start = max(raw_start, start_seconds)
        scene_end = min(raw_end, end_seconds) if end_seconds is not None else raw_end
        length = max(0.0, scene_end - scene_start - scene_offset)
        spacing = length / per_scene if per_scene > 1 else 0.0
        for shot in range(per_scene):
            at = scene_start + scene_offset + shot * spacing
            if at < scene_end:
                targets.append((round(at, 3), scene_number))
                if len(targets) >= max_frames:
                    return targets
    return targets


@router.post("/extract")
def extract_frames(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Start extracting frames by time interval or a bounded/sparse scene set.

    Both modes honor the time window; scene mode additionally honors one-based
    start/end scene numbers and a skip-scenes stride.
    """
    workspace_id = str(body.get("workspaceId") or "")
    video_rel = str(body.get("video") or "")
    if not workspace_id or not video_rel:
        raise HTTPException(status_code=400, detail="workspaceId and video are required")
    every_seconds = max(0.1, float(body.get("everySeconds") or 2.0))
    max_frames = max(1, min(600, int(body.get("maxFrames") or 60)))
    start_seconds = max(0.0, float(body.get("startSeconds") or 0.0))
    end_raw = body.get("endSeconds")
    end_seconds = float(end_raw) if end_raw not in (None, "", 0) else None
    if end_seconds is not None and end_seconds <= start_seconds:
        raise HTTPException(status_code=400, detail="endSeconds must be after startSeconds")
    # interval mode samples every N seconds; scenes mode takes perScene images
    # per detected scene, starting right after each scene change.
    mode = str(body.get("mode") or "interval")
    per_scene = max(1, min(20, int(body.get("perScene") or 1)))
    scene_offset = max(0.0, float(body.get("sceneOffsetSeconds") or 0.3))
    start_scene = max(1, int(body.get("startScene") or 1))
    end_scene_raw = body.get("endScene")
    end_scene = int(end_scene_raw) if end_scene_raw not in (None, "") else None
    if end_scene is not None and end_scene < start_scene:
        raise HTTPException(status_code=400, detail="endScene must be at or after startScene")
    skip_scenes = max(0, min(10000, int(body.get("skipScenes") or 0)))
    root = _workspace_root(workspace_id)
    try:
        video_path = _safe_workspace_child(root, video_rel)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not video_path.is_file():
        raise HTTPException(status_code=404, detail=f"video not found: {video_rel}")
    try:
        import imageio  # noqa: F401, PLC0415 - optional dependency
    except ImportError as error:
        raise HTTPException(status_code=500, detail="imageio is not installed in the server environment") from error

    # Estimate: frames from the window and rules, time from the last run's
    # per-frame pace (or a conservative default before any run).
    meta_path = video_path.parent / "video.json"
    meta: dict[str, Any] = {}
    if meta_path.is_file():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            meta = {}
    duration = meta.get("duration") or _probe_duration_seconds(video_path)
    window_end = min(float(duration), end_seconds) if duration and end_seconds is not None else (end_seconds or (float(duration) if duration else None))
    window = (window_end - start_seconds) if window_end is not None else None
    # In scenes mode the targets are computed from the saved markers: perScene
    # images spread through each scene, the first one right after the change.
    scene_targets: list[tuple[float, int]] = []
    if mode == "scenes":
        markers = [float(marker.get("atSeconds") or 0) for marker in (meta.get("scenes") or []) if isinstance(marker, dict)]
        if not markers:
            raise HTTPException(status_code=400, detail="no scene markers saved yet — run Detect scenes first")
        scene_targets = _scene_extraction_targets(
            markers,
            duration=float(duration) if duration else None,
            start_seconds=start_seconds,
            end_seconds=window_end,
            start_scene=start_scene,
            end_scene=end_scene,
            skip_scenes=skip_scenes,
            per_scene=per_scene,
            scene_offset=scene_offset,
            max_frames=max_frames,
        )
        if not scene_targets:
            raise HTTPException(status_code=400, detail="scene rules produced no target times in this window")
    estimated_frames = len(scene_targets) if mode == "scenes" else (
        min(max_frames, int(window / every_seconds) + 1) if window is not None else max_frames
    )
    pace = float((meta.get("lastExtract") or {}).get("secondsPerFrame") or 0.25)
    estimated_seconds = round(estimated_frames * pace + 1.0, 1)

    job_id = uuid.uuid4().hex[:12]
    job: dict[str, Any] = {
        "id": job_id, "state": "running", "done": 0, "total": estimated_frames,
        "elapsedSeconds": 0.0, "etaSeconds": estimated_seconds, "frames": [],
        "framesDir": None, "error": None,
    }
    _extract_jobs[job_id] = job

    def work() -> None:
        import imageio  # noqa: PLC0415
        from PIL import Image  # noqa: PLC0415

        started = time.monotonic()
        frames_dir = _video_frames_dir(root, video_path)
        if frames_dir.is_dir():
            shutil.rmtree(frames_dir, ignore_errors=True)
        frames_dir.mkdir(parents=True, exist_ok=True)
        frames: list[dict[str, Any]] = []
        try:
            reader = imageio.get_reader(str(video_path))
            try:
                fps = float(reader.get_meta_data().get("fps") or 24.0)
                step = max(1, round(fps * every_seconds))
                first_index = int(start_seconds * fps)
                last_index = int(end_seconds * fps) if end_seconds is not None else None
                target_cursor = 0
                for index, frame in enumerate(reader):
                    if job.get("cancel"):
                        break
                    at = index / fps
                    scene_index = None
                    if mode == "scenes":
                        # Grab the first frame at or past each scene target.
                        if target_cursor >= len(scene_targets):
                            break
                        target_at, scene_index = scene_targets[target_cursor]
                        if at < target_at:
                            continue
                        target_cursor += 1
                    else:
                        if index < first_index:
                            continue
                        if last_index is not None and index > last_index:
                            break
                        if (index - first_index) % step:
                            continue
                    ordinal = len(frames)
                    if ordinal >= max_frames:
                        break
                    name = f"frame_{ordinal:04d}.png"
                    frame_path = frames_dir / name
                    frame_provenance = _save_image_with_provenance(
                        root,
                        Image.fromarray(frame),
                        frame_path,
                        operation="extract_video_frame",
                        source={
                            "sourceVideo": video_rel,
                            "atSeconds": round(at, 3),
                            "sceneIndex": scene_index,
                            "videoFrameIndex": index,
                        },
                        transform={"mode": mode},
                        image_format="PNG",
                    )
                    frames.append({
                        "path": frame_path.relative_to(root).as_posix(),
                        "index": ordinal,
                        "atSeconds": round(at, 2),
                        "provenance": frame_provenance["provenance"],
                        **({"sceneIndex": scene_index} if scene_index is not None else {}),
                    })
                    elapsed = time.monotonic() - started
                    job["done"] = len(frames)
                    job["elapsedSeconds"] = round(elapsed, 1)
                    per_frame = elapsed / len(frames)
                    remaining = max(0, job["total"] - len(frames))
                    job["etaSeconds"] = round(remaining * per_frame, 1)
            finally:
                reader.close()
            elapsed = time.monotonic() - started
            job.update({
                "state": "done", "frames": frames, "done": len(frames), "total": len(frames),
                "elapsedSeconds": round(elapsed, 1), "etaSeconds": 0.0,
                "framesDir": frames_dir.relative_to(root).as_posix(),
                "interrupted": bool(job.get("cancel")),
            })
            # Remember the pace so the next estimate is grounded in a real run.
            last_extract = {
                "count": len(frames),
                "elapsedSeconds": round(elapsed, 1),
                "secondsPerFrame": round(elapsed / len(frames), 3) if frames else None,
                "at": _utc_now(),
            }
            try:
                _merge_video_meta(video_path, {
                    "lastExtract": last_extract,
                    **({"duration": duration} if duration else {}),
                })
            except OSError:
                pass
            # The download catalog tracks what has been extracted from each
            # candidate so far.
            _update_catalog_for_video(root, video_path, {}, extraction={
                "kind": "frames",
                "mode": mode,
                "count": len(frames),
                "elapsedSeconds": round(elapsed, 1),
                "everySeconds": every_seconds if mode == "interval" else None,
                "perScene": per_scene if mode == "scenes" else None,
                "startScene": start_scene if mode == "scenes" else None,
                "endScene": end_scene if mode == "scenes" else None,
                "skipScenes": skip_scenes if mode == "scenes" else None,
                "window": [start_seconds, end_seconds],
                "framesDir": frames_dir.relative_to(root).as_posix(),
                "at": _utc_now(),
            })
        except Exception as error:  # noqa: BLE001 - surfaced via the job record
            job.update({"state": "error", "error": str(error)})

    threading.Thread(target=work, name=f"video-extract-{job_id}", daemon=True).start()
    return {
        "jobId": job_id,
        "estimatedFrames": estimated_frames,
        "estimatedSeconds": estimated_seconds,
    }


@router.get("/extract/status")
def extract_status(jobId: str) -> dict[str, Any]:
    job = _extract_jobs.get(jobId)
    if job is None:
        raise HTTPException(status_code=404, detail=f"unknown extract job: {jobId}")
    return job


@router.get("/image-provenance")
def image_provenance(workspaceId: str, image: str) -> dict[str, Any]:
    root = _workspace_root(workspaceId)
    try:
        image_path = _safe_workspace_child(root, image)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not image_path.is_file():
        raise HTTPException(status_code=404, detail=f"image not found: {image}")
    payload = _read_image_provenance(image_path)
    if payload is None:
        from PIL import Image  # noqa: PLC0415

        with Image.open(image_path) as loaded:
            payload = _write_image_provenance(
                root,
                image_path,
                dimensions=loaded.size,
                operation="legacy_source",
                source={"path": image},
            )
    return payload


@router.post("/extract/cancel")
def cancel_job(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Ask any running job (extract/scenes/trim/filter/gallery) to stop at
    its next step; partial results are kept and returned as usual."""
    job_id = str(body.get("jobId") or "")
    job = _extract_jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"unknown job: {job_id}")
    job["cancel"] = True
    return {"jobId": job_id, "cancelling": True}


@router.post("/frame-at")
def frame_at_cursor(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Grab the single frame under the playhead into the video's frames/ dir
    (the ⤵ Frame at cursor button). Synchronous: one random-access read."""
    workspace_id = str(body.get("workspaceId") or "")
    video_rel = str(body.get("video") or "")
    if not workspace_id or not video_rel:
        raise HTTPException(status_code=400, detail="workspaceId and video are required")
    at_seconds = max(0.0, float(body.get("atSeconds") or 0.0))
    root, video_path = _resolve_video(workspace_id, video_rel)
    try:
        import imageio  # noqa: PLC0415
        from PIL import Image  # noqa: PLC0415
    except ImportError as error:
        raise HTTPException(status_code=500, detail="imageio/PIL are not installed in the server environment") from error
    frames_dir = _video_frames_dir(root, video_path)
    frames_dir.mkdir(parents=True, exist_ok=True)
    reader = imageio.get_reader(str(video_path))
    try:
        fps = float(reader.get_meta_data().get("fps") or 24.0)
        index = max(0, int(round(at_seconds * fps)))
        try:
            frame = reader.get_data(index)
        except (IndexError, OSError, RuntimeError) as error:
            raise HTTPException(status_code=400, detail=f"no frame at {at_seconds:.2f}s: {error}") from error
        name = f"frame_at_{int(round(at_seconds * 1000)):08d}.png"
        frame_path = frames_dir / name
        provenance = _save_image_with_provenance(
            root,
            Image.fromarray(frame),
            frame_path,
            operation="grab_video_frame",
            source={
                "sourceVideo": video_rel,
                "atSeconds": round(at_seconds, 3),
                "videoFrameIndex": index,
            },
            image_format="PNG",
        )
    finally:
        reader.close()
    return {
        "path": frame_path.relative_to(root).as_posix(),
        "atSeconds": round(at_seconds, 2),
        "index": index,
        "provenance": provenance["provenance"],
    }


def _normalized_outline_points(
    raw: Any,
    label: str,
    width: int,
    height: int,
) -> list[tuple[int, int]]:
    points: list[tuple[int, int]] = []
    if not isinstance(raw, list):
        return points
    for index, point in enumerate(raw):
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            continue
        try:
            x = int(round(float(point[0])))
            y = int(round(float(point[1])))
        except (TypeError, ValueError, OverflowError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"{label} point {index + 1} is not numeric",
            ) from error
        if not 0 <= x < width or not 0 <= y < height:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"{label} point {index + 1} ({x}, {y}) is outside the "
                    f"{width}x{height} Outliner coordinate space"
                ),
            )
        points.append((x, y))
    return points


def _normalized_outline_geometry(
    body: dict[str, Any],
    width: int,
    height: int,
) -> tuple[list[list[tuple[int, int]]], list[list[tuple[int, int]]]]:
    polygons: list[list[tuple[int, int]]] = []
    polygons_raw = body.get("polygons")
    if isinstance(polygons_raw, list):
        polygons = [
            points
            for index, raw in enumerate(polygons_raw)
            if len(
                points := _normalized_outline_points(
                    raw,
                    f"polygon {index + 1}",
                    width,
                    height,
                )
            )
            >= 3
        ]
    polygon_raw = body.get("polygon")
    if not polygons and isinstance(polygon_raw, list):
        points = _normalized_outline_points(polygon_raw, "polygon", width, height)
        if len(points) >= 3:
            polygons = [points]
    box_raw = body.get("box")
    if not polygons and isinstance(box_raw, list) and len(box_raw) == 4:
        try:
            bx0, by0, bx1, by1 = (
                int(round(float(value))) for value in box_raw
            )
        except (TypeError, ValueError, OverflowError) as error:
            raise HTTPException(status_code=400, detail="box coordinates must be numeric") from error
        bx0, bx1 = sorted((bx0, bx1))
        by0, by1 = sorted((by0, by1))
        if bx0 < 0 or by0 < 0 or bx1 > width or by1 > height:
            raise HTTPException(
                status_code=409,
                detail=f"box is outside the {width}x{height} Outliner coordinate space",
            )
        polygons = [[(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)]]
    if not polygons:
        raise HTTPException(
            status_code=400,
            detail="polygons (each >= 3 [x, y] points), polygon, or box is required",
        )
    holes_raw = body.get("holes")
    holes = (
        [
            points
            for index, raw in enumerate(holes_raw)
            if len(
                points := _normalized_outline_points(
                    raw,
                    f"hole {index + 1}",
                    width,
                    height,
                )
            )
            >= 3
        ]
        if isinstance(holes_raw, list)
        else []
    )
    return polygons, holes


def _outline_geometry_document(
    polygons: list[list[tuple[int, int]]],
    holes: list[list[tuple[int, int]]],
) -> dict[str, list[list[list[int]]]]:
    return {
        "polygons": [[[x, y] for x, y in points] for points in polygons],
        "holes": [[[x, y] for x, y in points] for points in holes],
    }


def _outline_geometry_hash(
    polygons: list[list[tuple[int, int]]],
    holes: list[list[tuple[int, int]]],
) -> str:
    encoded = json.dumps(
        _outline_geometry_document(polygons, holes),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _outline_mask(
    polygons: list[list[tuple[int, int]]],
    holes: list[list[tuple[int, int]]],
    width: int,
    height: int,
    image_module: Any,
    image_draw_module: Any,
) -> Any:
    scale = 4
    mask_large = image_module.new("L", (width * scale, height * scale), 0)
    draw = image_draw_module.Draw(mask_large)
    for points in polygons:
        draw.polygon([(x * scale, y * scale) for x, y in points], fill=255)
    for points in holes:
        draw.polygon([(x * scale, y * scale) for x, y in points], fill=0)
    return mask_large.resize((width, height), image_module.Resampling.LANCZOS)


@router.post("/planner-visualization")
def planner_visualization(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Draw Planner order numbers on the exact image used for planning."""
    workspace_id = str(body.get("workspaceId") or "")
    image_rel = str(body.get("image") or "")
    labels_raw = body.get("labels")
    if not workspace_id or not image_rel or not isinstance(labels_raw, list):
        raise HTTPException(
            status_code=400,
            detail="workspaceId, image, and labels are required",
        )
    root = _workspace_root(workspace_id)
    try:
        image_path = _safe_workspace_child(root, image_rel)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not image_path.is_file():
        raise HTTPException(status_code=404, detail=f"image not found: {image_rel}")
    try:
        from PIL import Image, ImageDraw, ImageFont  # noqa: PLC0415
    except ImportError as error:
        raise HTTPException(status_code=500, detail="PIL is not installed") from error
    visualization = Image.open(image_path).convert("RGBA")
    width, height = visualization.size
    labels: list[dict[str, Any]] = []
    for index, value in enumerate(labels_raw):
        record = value if isinstance(value, dict) else {}
        point = record.get("point")
        if not isinstance(point, list) or len(point) != 2:
            raise HTTPException(
                status_code=400,
                detail=f"Planner label {index + 1} requires point [x, y]",
            )
        try:
            x, y = (int(round(float(coordinate))) for coordinate in point)
            number = int(record.get("number"))
        except (TypeError, ValueError, OverflowError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Planner label {index + 1} has invalid coordinates or number",
            ) from error
        if not 0 <= x < width or not 0 <= y < height:
            raise HTTPException(
                status_code=409,
                detail=f"Planner label {index + 1} is outside the {width}x{height} image",
            )
        if number < 1:
            raise HTTPException(status_code=400, detail="Planner label numbers must be positive")
        labels.append(
            {
                "object": str(record.get("object") or ""),
                "number": number,
                "point": [x, y],
            }
        )
    draw = ImageDraw.Draw(visualization, "RGBA")
    radius = max(12, min(28, round(min(width, height) * 0.035)))
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", radius)
    except OSError:
        font = ImageFont.load_default()
    for label in labels:
        x, y = label["point"]
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=(5, 13, 20, 220),
            outline=(255, 230, 0, 255),
            width=max(2, radius // 6),
        )
        draw.text(
            (x, y),
            str(label["number"]),
            fill=(255, 255, 255, 255),
            font=font,
            anchor="mm",
        )
    output_dir = image_path.parent / f"{image_path.stem}_planner"
    output_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(
        json.dumps(labels, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    output_path = output_dir / f"order_{digest[:12]}.png"
    provenance = _save_image_with_provenance(
        root,
        visualization,
        output_path,
        operation="visualize_planner_order",
        parent_image=image_path,
        transform={"labels": labels, "plannerHash": digest},
        image_format="PNG",
    )
    return {
        "visualizationImage": output_path.relative_to(root).as_posix(),
        "provenance": provenance["provenance"],
        "plannerHash": digest,
        "dimensions": {"width": width, "height": height},
        "labels": labels,
    }


@router.post("/outline-verification")
def outline_verification(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Rasterize and verify Outliner geometry and Turtle trace before extraction."""
    workspace_id = str(body.get("workspaceId") or "")
    image_rel = str(body.get("image") or "")
    name = str(body.get("name") or "object")
    trace_raw = body.get("traceTurtle")
    if not workspace_id or not image_rel or not isinstance(trace_raw, list):
        raise HTTPException(
            status_code=400,
            detail="workspaceId, image, and traceTurtle are required",
        )
    root = _workspace_root(workspace_id)
    try:
        image_path = _safe_workspace_child(root, image_rel)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not image_path.is_file():
        raise HTTPException(status_code=404, detail=f"image not found: {image_rel}")
    try:
        from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont  # noqa: PLC0415
    except ImportError as error:
        raise HTTPException(status_code=500, detail="PIL is not installed") from error
    source = Image.open(image_path).convert("RGBA")
    width, height = source.size
    polygons, holes = _normalized_outline_geometry(body, width, height)
    mask = _outline_mask(polygons, holes, width, height, Image, ImageDraw)
    bbox = mask.point(lambda alpha: 255 if alpha > 1 else 0).getbbox()
    if not bbox:
        raise HTTPException(status_code=400, detail="Outliner geometry produced an empty mask")
    trace_paths: list[list[tuple[int, int]]] = []
    current_path: list[tuple[int, int]] = []
    normalized_trace: list[dict[str, int | str]] = []
    for index, value in enumerate(trace_raw):
        record = value if isinstance(value, dict) else {}
        operation = str(record.get("op") or "").lower()
        if operation not in {"move", "line"}:
            raise HTTPException(
                status_code=400,
                detail=f"traceTurtle command {index + 1} must be move or line",
            )
        try:
            normalized_x = int(round(float(record.get("x"))))
            normalized_y = int(round(float(record.get("y"))))
        except (TypeError, ValueError, OverflowError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"traceTurtle command {index + 1} has invalid coordinates",
            ) from error
        if not 0 <= normalized_x <= 1000 or not 0 <= normalized_y <= 1000:
            raise HTTPException(
                status_code=409,
                detail=f"traceTurtle command {index + 1} is outside normalized 0..1000 space",
            )
        point = (
            round(normalized_x * max(0, width - 1) / 1000),
            round(normalized_y * max(0, height - 1) / 1000),
        )
        if operation == "move":
            if len(current_path) >= 2:
                trace_paths.append(current_path)
            current_path = [point]
        elif current_path:
            current_path.append(point)
        else:
            raise HTTPException(
                status_code=400,
                detail="traceTurtle must begin with a move command",
            )
        normalized_trace.append(
            {"op": operation, "x": normalized_x, "y": normalized_y}
        )
    if len(current_path) >= 2:
        trace_paths.append(current_path)
    if not trace_paths or sum(len(path) for path in trace_paths) < 3:
        raise HTTPException(
            status_code=400,
            detail="traceTurtle requires at least one move and two line points",
        )
    trace_mask = Image.new("L", (width, height), 0)
    trace_draw = ImageDraw.Draw(trace_mask)
    trace_width = max(2, round(min(width, height) * 0.006))
    for points in trace_paths:
        trace_draw.line(points, fill=255, width=trace_width, joint="curve")
    tolerance = max(3, min(15, round(min(width, height) * 0.012)))
    kernel = tolerance * 2 + 1
    solid_mask = mask.point(lambda alpha: 255 if alpha >= 128 else 0)
    boundary = ImageChops.difference(
        solid_mask.filter(ImageFilter.MaxFilter(kernel)),
        solid_mask.filter(ImageFilter.MinFilter(kernel)),
    )
    boundary_near = boundary.filter(ImageFilter.MaxFilter(kernel))
    trace_near = trace_mask.filter(ImageFilter.MaxFilter(kernel))
    trace_pixels = sum(trace_mask.histogram()[1:])
    boundary_pixels = sum(boundary.histogram()[1:])
    trace_on_boundary = sum(ImageChops.multiply(trace_mask, boundary_near).histogram()[1:])
    boundary_covered = sum(ImageChops.multiply(boundary, trace_near).histogram()[1:])
    trace_agreement = trace_on_boundary / trace_pixels if trace_pixels else 0.0
    boundary_coverage = boundary_covered / boundary_pixels if boundary_pixels else 0.0
    if trace_agreement < 0.70 or boundary_coverage < 0.45:
        raise HTTPException(
            status_code=409,
            detail=(
                "Outliner Turtle trace does not agree with the extraction boundary "
                f"(trace agreement {trace_agreement:.1%}, boundary coverage {boundary_coverage:.1%})"
            ),
        )
    tint = Image.new("RGBA", source.size, (0, 255, 128, 0))
    tint.putalpha(mask.point(lambda alpha: round(alpha * 0.28)))
    visualization = Image.alpha_composite(source, tint)
    draw = ImageDraw.Draw(visualization, "RGBA")
    outline_width = max(2, round(min(width, height) * 0.005))
    for points in polygons:
        draw.line(points + [points[0]], fill=(255, 40, 180, 255), width=outline_width, joint="curve")
    for points in holes:
        draw.line(points + [points[0]], fill=(255, 150, 0, 255), width=outline_width, joint="curve")
    for points in trace_paths:
        draw.line(points, fill=(0, 235, 255, 255), width=outline_width, joint="curve")
    planner_number = body.get("plannerNumber")
    if planner_number is not None:
        x = round((bbox[0] + bbox[2]) / 2)
        y = round((bbox[1] + bbox[3]) / 2)
        radius = max(12, min(28, round(min(width, height) * 0.035)))
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", radius)
        except OSError:
            font = ImageFont.load_default()
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=(5, 13, 20, 220),
            outline=(255, 230, 0, 255),
            width=max(2, radius // 6),
        )
        draw.text((x, y), str(planner_number), fill="white", font=font, anchor="mm")
    geometry_hash = _outline_geometry_hash(polygons, holes)
    output_dir = image_path.parent / f"{image_path.stem}_outlines"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"verify_{_slug(name)[:24]}_{geometry_hash[:12]}.png"
    transform = {
        **_outline_geometry_document(polygons, holes),
        "traceTurtle": normalized_trace,
        "geometryHash": geometry_hash,
        "traceAgreement": round(trace_agreement, 4),
        "boundaryCoverage": round(boundary_coverage, 4),
    }
    provenance = _save_image_with_provenance(
        root,
        visualization,
        output_path,
        operation="verify_outliner_trace",
        parent_image=image_path,
        source={"objectName": name},
        transform=transform,
        image_format="PNG",
    )
    return {
        "verificationImage": output_path.relative_to(root).as_posix(),
        "provenance": provenance["provenance"],
        "geometryHash": geometry_hash,
        "dimensions": {"width": width, "height": height},
        "traceAgreement": transform["traceAgreement"],
        "boundaryCoverage": transform["boundaryCoverage"],
        "verified": True,
    }


@router.post("/member-cut")
def member_cut(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Cut one identified member out of a scene as a precise alpha PNG: the
    member's polygon keeps its pixels, everything else is transparent. The
    member is then erased from the scene (border-median fill) so the
    extraction loop can continue on the reduced scene."""
    workspace_id = str(body.get("workspaceId") or "")
    image_rel = str(body.get("image") or "")
    name = str(body.get("name") or "member")
    step = max(1, int(body.get("step") or 1))
    outline_source_rel = str(body.get("outlineSourceImage") or "")
    outline_source_dimensions = body.get("outlineSourceDimensions")
    if not workspace_id or not image_rel:
        raise HTTPException(status_code=400, detail="workspaceId and image are required")
    root = _workspace_root(workspace_id)
    try:
        image_path = _safe_workspace_child(root, image_rel)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not image_path.is_file():
        raise HTTPException(status_code=404, detail=f"image not found: {image_rel}")
    try:
        import numpy as np  # noqa: PLC0415
        from PIL import Image, ImageChops, ImageDraw, ImageFilter  # noqa: PLC0415
    except ImportError as error:
        raise HTTPException(status_code=500, detail="numpy/PIL are not installed in the server environment") from error
    source_rgba = Image.open(image_path).convert("RGBA")
    image = Image.new("RGB", source_rgba.size, (0, 0, 0))
    image.paste(source_rgba, mask=source_rgba.getchannel("A"))
    width, height = source_rgba.size
    alignment = {
        "cutImage": image_rel,
        "outlineSourceImage": outline_source_rel or image_rel,
        "dimensions": {"width": width, "height": height},
        "verified": False,
    }
    if outline_source_rel:
        try:
            outline_source_path = _safe_workspace_child(root, outline_source_rel)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        if not outline_source_path.is_file():
            raise HTTPException(status_code=404, detail=f"Outliner source image not found: {outline_source_rel}")
        with Image.open(outline_source_path) as outline_source:
            if outline_source.size != source_rgba.size:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"Outliner coordinate space is {outline_source.width}x{outline_source.height}, "
                        f"but cut image is {width}x{height}"
                    ),
                )
        if isinstance(outline_source_dimensions, dict):
            expected = (
                int(outline_source_dimensions.get("width") or 0),
                int(outline_source_dimensions.get("height") or 0),
            )
            if expected != source_rgba.size:
                raise HTTPException(
                    status_code=409,
                    detail=f"Stored Outliner dimensions {expected[0]}x{expected[1]} do not match cut image {width}x{height}",
                )
        if outline_source_rel != image_rel:
            current_provenance = _read_image_provenance(image_path)
            lineage_images = {
                str(step_record.get("image") or "")
                for step_record in (current_provenance or {}).get("lineage") or []
                if isinstance(step_record, dict)
            }
            if outline_source_rel not in lineage_images:
                raise HTTPException(
                    status_code=409,
                    detail=f"Cut image is not a provenance descendant of Outliner source: {outline_source_rel}",
                )
        alignment["verified"] = True

    polygons, holes = _normalized_outline_geometry(body, width, height)
    scale = 4
    mask = _outline_mask(polygons, holes, width, height, Image, ImageDraw)
    geometry_hash = _outline_geometry_hash(polygons, holes)
    verification_rel = str(body.get("outlineVerificationImage") or "")
    verification_hash = str(body.get("outlineGeometryHash") or "")
    if verification_rel:
        try:
            verification_path = _safe_workspace_child(root, verification_rel)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        verification_provenance = _read_image_provenance(verification_path)
        recorded_hash = str(
            ((verification_provenance or {}).get("transform") or {}).get("geometryHash")
            or ""
        )
        if not verification_path.is_file() or recorded_hash != geometry_hash or verification_hash != geometry_hash:
            raise HTTPException(
                status_code=409,
                detail="Outliner verification artifact does not match extraction geometry",
            )
        alignment["verificationImage"] = verification_rel
        alignment["geometryHash"] = geometry_hash
        alignment["traceVerified"] = True
    bbox = mask.point(lambda alpha: 255 if alpha > 1 else 0).getbbox()
    if not bbox or (bbox[2] - bbox[0]) < 2 or (bbox[3] - bbox[1]) < 2:
        raise HTTPException(status_code=400, detail=f"polygon too small after clamping to {width}x{height}")
    x0, y0, x1, y1 = bbox
    members_dir = image_path.parent / f"{image_path.stem}_members"
    members_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug(name)[:24] or f"member{step}"
    # Preserve source transparency and anti-alias the traced silhouette.
    rgba = source_rgba.copy()
    rgba.putalpha(ImageChops.multiply(source_rgba.getchannel("A"), mask))
    cut = rgba.crop(bbox)
    cutout_path = members_dir / f"cut_{step:02d}_{slug}.png"
    cutout_provenance = _save_image_with_provenance(
        root,
        cut,
        cutout_path,
        operation="extract_object_cutout",
        parent_image=image_path,
        source={"objectName": name},
        transform={
            "inputDimensions": {"width": width, "height": height},
            "outlineAlignment": alignment,
            "cropBox": [x0, y0, x1, y1],
            "maskScale": scale,
            "polygons": [[[x, y] for x, y in points] for points in polygons],
            "holes": [[[x, y] for x, y in points] for points in holes],
        },
        image_format="PNG",
    )
    # Recursive vision calls need enough pixels to inspect small sub-objects.
    # Keep the precise cutout unchanged for output, and create a padded,
    # high-resolution analysis image for the next Describer pass.
    enlarge_for_next_pass = body.get("enlargeForNextPass") is not False
    next_pass_scale = 1
    padding = 0
    next_pass_path = cutout_path
    if enlarge_for_next_pass:
        longest_side = max(cut.size)
        next_pass_scale = max(1, (640 + longest_side - 1) // longest_side)
        enlarged = cut.resize(
            (cut.width * next_pass_scale, cut.height * next_pass_scale),
            Image.Resampling.LANCZOS,
        )
        padding = max(16, round(max(enlarged.size) * 0.08))
        next_pass = Image.new(
            "RGBA",
            (enlarged.width + padding * 2, enlarged.height + padding * 2),
            (0, 0, 0, 0),
        )
        next_pass.alpha_composite(enlarged, (padding, padding))
        next_pass_path = members_dir / f"next_pass_{step:02d}_{slug}.png"
        _save_image_with_provenance(
            root,
            next_pass,
            next_pass_path,
            operation="enlarge_object_for_analysis",
            parent_image=cutout_path,
            source={"objectName": name},
            transform={
                "sourceDimensions": {"width": cut.width, "height": cut.height},
                "scale": next_pass_scale,
                "resizedDimensions": {"width": enlarged.width, "height": enlarged.height},
                "padding": {"left": padding, "top": padding, "right": padding, "bottom": padding},
            },
            image_format="PNG",
        )
    # Erase the member from the scene. `fill` picks the removal method.
    fill_mode = str(body.get("fill") or "inpaint")
    if fill_mode not in {"inpaint", "median", "blur", "hole"}:
        raise HTTPException(status_code=400, detail="fill must be inpaint, median, blur, or hole")
    fill_instructions = body.get("fillInstructions") if isinstance(body.get("fillInstructions"), dict) else {}
    image_generation_model_id = str(body.get("imageGenerationModelId") or "")
    image_generation: dict[str, Any] = {"renderer": "boundary_diffusion" if fill_mode == "inpaint" else fill_mode}
    array = np.array(image)
    mask_array = np.array(mask) >= 128
    if fill_mode == "inpaint":
        generated_scene = None
        if image_generation_model_id:
            mask_alpha = Image.eval(mask, lambda value: 255 - value)
            edit_mask = Image.new("RGBA", image.size, (255, 255, 255, 255))
            edit_mask.putalpha(mask_alpha)
            edit_prompt = (
                f"Remove only the outlined object '{name}' and reconstruct what belongs behind it. "
                "Preserve every pixel outside the transparent mask. Return the complete image at the exact input dimensions. "
                f"Background continuation plan: {json.dumps(fill_instructions, ensure_ascii=True)}"
            )
            generated_scene, image_generation = _try_model_image_edit(
                root,
                image_generation_model_id,
                image,
                edit_mask,
                edit_prompt,
            )
        if generated_scene is not None:
            scene_image = Image.composite(generated_scene.convert("RGB"), image, mask)
        else:
            pad = max(16, min(64, round(max(x1 - x0, y1 - y0) * 0.2)))
            rx0, ry0 = max(0, x0 - pad), max(0, y0 - pad)
            rx1, ry1 = min(width, x1 + pad), min(height, y1 + pad)
            region = array[ry0:ry1, rx0:rx1].astype(np.float64)
            region_mask = mask_array[ry0:ry1, rx0:rx1]
            known = ~region_mask
            for _ in range(max(region.shape[:2])):
                remaining = ~known
                if not remaining.any():
                    break
                color_sum = np.zeros_like(region)
                neighbor_count = np.zeros(region.shape[:2], dtype=np.float64)
                for dy, dx in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
                    dest_y0, dest_y1 = max(0, -dy), min(region.shape[0], region.shape[0] - dy)
                    dest_x0, dest_x1 = max(0, -dx), min(region.shape[1], region.shape[1] - dx)
                    source_y = slice(dest_y0 + dy, dest_y1 + dy)
                    source_x = slice(dest_x0 + dx, dest_x1 + dx)
                    dest_y = slice(dest_y0, dest_y1)
                    dest_x = slice(dest_x0, dest_x1)
                    neighbor_known = known[source_y, source_x]
                    color_sum[dest_y, dest_x] += region[source_y, source_x] * neighbor_known[..., None]
                    neighbor_count[dest_y, dest_x] += neighbor_known
                fillable = remaining & (neighbor_count > 0)
                if not fillable.any():
                    fallback = np.median(region[known], axis=0) if known.any() else np.array([127, 127, 127])
                    region[remaining] = fallback
                    known[remaining] = True
                    break
                region[fillable] = color_sum[fillable] / neighbor_count[fillable, None]
                known[fillable] = True
            filled_region = np.clip(region, 0, 255).astype(array.dtype)
            array[ry0:ry1, rx0:rx1][region_mask] = filled_region[region_mask]
            scene_image = Image.fromarray(array)
    elif fill_mode == "hole":
        rgba_scene = source_rgba.copy()
        alpha_channel = np.array(source_rgba.getchannel("A"))
        alpha_channel[mask_array] = 0
        rgba_scene.putalpha(Image.fromarray(alpha_channel))
        scene_image = rgba_scene
    elif fill_mode == "blur":
        blurred = np.array(image.filter(ImageFilter.GaussianBlur(14)))
        array[mask_array] = blurred[mask_array]
        scene_image = Image.fromarray(array)
    else:
        pad = 6
        rx0, ry0 = max(0, x0 - pad), max(0, y0 - pad)
        rx1, ry1 = min(width, x1 + pad), min(height, y1 + pad)
        ring = np.zeros((height, width), dtype=bool)
        ring[ry0:ry1, rx0:rx1] = True
        ring &= ~mask_array
        fill = np.median(array[ring], axis=0).astype(array.dtype) if ring.any() else np.array([127, 127, 127], dtype=array.dtype)
        array[mask_array] = fill
        scene_image = Image.fromarray(array)
    scene_path = members_dir / f"scene_after_{step:02d}.png"
    scene_provenance = _save_image_with_provenance(
        root,
        scene_image,
        scene_path,
        operation="remove_object_from_scene",
        parent_image=image_path,
        source={"objectName": name, "cutout": cutout_path.relative_to(root).as_posix(), "fillInstructions": fill_instructions},
        transform={"fill": fill_mode, "outlineAlignment": alignment, "removedBox": [x0, y0, x1, y1], "maskScale": scale, "fillInstructions": fill_instructions, "imageGeneration": image_generation},
        image_format="PNG",
    )
    return {
        "cutout": cutout_path.relative_to(root).as_posix(),
        "cutoutProvenance": cutout_provenance["provenance"],
        "nextPassImage": next_pass_path.relative_to(root).as_posix(),
        "nextPassProvenance": _workspace_relative(root, _image_provenance_path(next_pass_path)),
        "nextPassScale": next_pass_scale,
        "nextPassPadding": padding,
        "enlargedForNextPass": enlarge_for_next_pass,
        "scene": scene_path.relative_to(root).as_posix(),
        "sceneProvenance": scene_provenance["provenance"],
        "box": [x0, y0, x1, y1],
        "name": name,
        "fill": fill_mode,
        "fillInstructions": fill_instructions,
        "fillRenderer": image_generation.get("renderer"),
        "imageGeneration": image_generation,
        "outlineAlignment": alignment,
        "polygonCount": len(polygons),
        "holeCount": len(holes),
        "maskScale": scale,
    }


@router.post("/member-return")
def member_return(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Reject an extracted member: paste its cutout back onto the current
    reduced scene at its original box, producing a new scene image."""
    workspace_id = str(body.get("workspaceId") or "")
    scene_rel = str(body.get("scene") or "")
    cutout_rel = str(body.get("cutout") or "")
    box_raw = body.get("box") or []
    if not workspace_id or not scene_rel or not cutout_rel:
        raise HTTPException(status_code=400, detail="workspaceId, scene, and cutout are required")
    if not isinstance(box_raw, list) or len(box_raw) != 4:
        raise HTTPException(status_code=400, detail="box must be [x0, y0, x1, y1]")
    root = _workspace_root(workspace_id)
    try:
        scene_path = _safe_workspace_child(root, scene_rel)
        cutout_path = _safe_workspace_child(root, cutout_rel)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not scene_path.is_file() or not cutout_path.is_file():
        raise HTTPException(status_code=404, detail="scene or cutout not found")
    try:
        from PIL import Image  # noqa: PLC0415
    except ImportError as error:
        raise HTTPException(status_code=500, detail="PIL is not installed in the server environment") from error
    scene = Image.open(scene_path).convert("RGB")
    # The cutout GIF is transparent outside the member: composite it back so
    # exactly the member's pixels return to the scene.
    cutout = Image.open(cutout_path).convert("RGBA")
    x0, y0 = int(round(float(box_raw[0]))), int(round(float(box_raw[1])))
    scene.paste(cutout, (max(0, x0), max(0, y0)), cutout)
    returned_path = scene_path.parent / f"scene_return_{uuid.uuid4().hex[:6]}.png"
    provenance = _save_image_with_provenance(
        root,
        scene,
        returned_path,
        operation="return_object_to_scene",
        parent_image=scene_path,
        source={"returnedCutout": cutout_rel},
        transform={"pasteAt": [max(0, x0), max(0, y0)], "box": box_raw},
        image_format="PNG",
    )
    return {"scene": returned_path.relative_to(root).as_posix(), "provenance": provenance["provenance"]}


@router.post("/turtle-render")
def turtle_render(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Persist and safely render a normalized JSON turtle drawing program."""
    workspace_id = str(body.get("workspaceId") or "")
    source_rel = str(body.get("sourceImage") or "")
    raw_program = body.get("program")
    if not workspace_id or not source_rel or raw_program in (None, ""):
        raise HTTPException(status_code=400, detail="workspaceId, sourceImage, and program are required")
    root = _workspace_root(workspace_id)
    try:
        source_path = _safe_workspace_child(root, source_rel)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not source_path.is_file():
        raise HTTPException(status_code=404, detail=f"source image not found: {source_rel}")

    if isinstance(raw_program, dict):
        program = raw_program
        raw_text = json.dumps(raw_program, indent=2, ensure_ascii=False)
    else:
        raw_text = str(raw_program).strip()
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text, flags=re.IGNORECASE)
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start < 0 or end <= start:
            raise HTTPException(status_code=400, detail="turtle program must contain one JSON object")
        try:
            parsed = json.loads(cleaned[start:end + 1])
        except json.JSONDecodeError as error:
            raise HTTPException(status_code=400, detail=f"invalid turtle JSON: {error}") from error
        if not isinstance(parsed, dict):
            raise HTTPException(status_code=400, detail="turtle program must be a JSON object")
        program = parsed
    commands = program.get("commands")
    if not isinstance(commands, list) or not commands:
        raise HTTPException(status_code=400, detail="turtle program commands must be a non-empty array")
    if len(commands) > 200:
        raise HTTPException(status_code=400, detail="turtle program exceeds the 200-command limit")

    from PIL import Image, ImageColor, ImageDraw  # noqa: PLC0415

    with Image.open(source_path) as source:
        source_width, source_height = source.size
    scale = min(1.0, 768 / max(source_width, source_height))
    width = max(2, round(source_width * scale))
    height = max(2, round(source_height * scale))

    def color(value: Any, default: str) -> tuple[int, int, int, int]:
        candidate = default if value in (None, "") else str(value)
        if candidate.lower() == "transparent":
            return (0, 0, 0, 0)
        try:
            return ImageColor.getcolor(candidate, "RGBA")
        except ValueError as error:
            raise HTTPException(status_code=400, detail=f"invalid turtle color: {candidate}") from error

    def point(x: Any, y: Any) -> tuple[int, int]:
        try:
            normalized_x = max(0.0, min(1000.0, float(x)))
            normalized_y = max(0.0, min(1000.0, float(y)))
        except (TypeError, ValueError, OverflowError) as error:
            raise HTTPException(status_code=400, detail="turtle coordinates must be numbers from 0 to 1000") from error
        return (round(normalized_x * width / 1000), round(normalized_y * height / 1000))

    def bounded_int(value: Any, default: int, label: str, maximum: int = 64) -> int:
        try:
            return max(1, min(maximum, int(value if value not in (None, "") else default)))
        except (TypeError, ValueError, OverflowError) as error:
            raise HTTPException(status_code=400, detail=f"{label} must be a number") from error

    background = color(program.get("background"), "transparent")
    rendered = Image.new("RGBA", (width, height), background)
    draw = ImageDraw.Draw(rendered, "RGBA")
    cursor = (0, 0)
    pen_color = color(program.get("penColor"), "#ffffff")
    pen_width = bounded_int(program.get("penWidth"), 4, "penWidth")
    for index, command in enumerate(commands):
        if not isinstance(command, dict):
            raise HTTPException(status_code=400, detail=f"turtle command {index + 1} must be an object")
        operation = str(command.get("op") or "").lower()
        if operation == "pen":
            pen_color = color(command.get("color"), "#ffffff")
            pen_width = bounded_int(command.get("width"), pen_width, f"command {index + 1} width")
        elif operation == "move":
            cursor = point(command.get("x"), command.get("y"))
        elif operation == "line":
            target = point(command.get("x"), command.get("y"))
            draw.line([cursor, target], fill=color(command.get("color"), "#ffffff") if command.get("color") else pen_color, width=bounded_int(command.get("width"), pen_width, f"command {index + 1} width"))
            cursor = target
        elif operation in {"polyline", "polygon"}:
            raw_points = command.get("points")
            if not isinstance(raw_points, list) or len(raw_points) < (3 if operation == "polygon" else 2):
                raise HTTPException(status_code=400, detail=f"turtle {operation} command {index + 1} has too few points")
            points = [point(raw_point[0], raw_point[1]) for raw_point in raw_points if isinstance(raw_point, (list, tuple)) and len(raw_point) == 2]
            if len(points) != len(raw_points):
                raise HTTPException(status_code=400, detail=f"turtle {operation} command {index + 1} has invalid points")
            outline = color(command.get("outline"), "#ffffff") if command.get("outline") else pen_color
            if operation == "polygon":
                draw.polygon(points, fill=color(command.get("fill"), "transparent"), outline=outline, width=bounded_int(command.get("width"), pen_width, f"command {index + 1} width"))
            else:
                draw.line(points, fill=outline, width=bounded_int(command.get("width"), pen_width, f"command {index + 1} width"), joint="curve")
            cursor = points[-1]
        elif operation in {"rectangle", "ellipse"}:
            box = command.get("box")
            if not isinstance(box, list) or len(box) != 4:
                raise HTTPException(status_code=400, detail=f"turtle {operation} command {index + 1} requires box [x0,y0,x1,y1]")
            first = point(box[0], box[1])
            second = point(box[2], box[3])
            bounds = [min(first[0], second[0]), min(first[1], second[1]), max(first[0], second[0]), max(first[1], second[1])]
            painter = draw.rectangle if operation == "rectangle" else draw.ellipse
            painter(
                bounds,
                fill=color(command.get("fill"), "transparent"),
                outline=color(command.get("outline"), "#ffffff") if command.get("outline") else pen_color,
                width=bounded_int(command.get("width"), pen_width, f"command {index + 1} width"),
            )
        elif operation == "dot":
            center = point(command.get("x"), command.get("y"))
            try:
                radius_value = float(command.get("radius") or 8)
            except (TypeError, ValueError, OverflowError) as error:
                raise HTTPException(status_code=400, detail=f"command {index + 1} radius must be a number") from error
            radius = max(1, min(min(width, height), round(radius_value * min(width, height) / 1000)))
            draw.ellipse([center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius], fill=color(command.get("color"), "#ffffff"))
        else:
            raise HTTPException(status_code=400, detail=f"unsupported turtle operation at command {index + 1}: {operation}")

    program_path = source_path.with_suffix(".turtle.json")
    program_artifact = {
        "kind": "turtle_program",
        "version": 1,
        "sourceImage": source_rel,
        "subjectName": str(body.get("subjectName") or source_path.stem),
        "modelId": str(body.get("modelId") or ""),
        "prompt": str(body.get("prompt") or ""),
        "rawModelOutput": raw_text,
        "program": program,
        "createdAt": _utc_now(),
    }
    program_path.write_text(json.dumps(program_artifact, indent=2, ensure_ascii=False), encoding="utf-8")
    render_path = source_path.with_suffix(".turtle.png")
    provenance = _save_image_with_provenance(
        root,
        rendered,
        render_path,
        operation="render_turtle_program",
        parent_image=source_path,
        source={"turtleProgram": _workspace_relative(root, program_path)},
        transform={
            "coordinateSpace": [1000, 1000],
            "sourceDimensions": {"width": source_width, "height": source_height},
            "renderScale": scale,
            "commandCount": len(commands),
        },
        image_format="PNG",
    )
    source_provenance = image_provenance(workspace_id, source_rel)
    source_provenance["terminal"] = {
        "turtleProgram": _workspace_relative(root, program_path),
        "renderedImage": _workspace_relative(root, render_path),
        "renderedProvenance": provenance["provenance"],
    }
    provenance_path = _image_provenance_path(source_path)
    temporary = provenance_path.with_suffix(provenance_path.suffix + ".tmp")
    temporary.write_text(json.dumps(source_provenance, indent=2, ensure_ascii=False), encoding="utf-8")
    temporary.replace(provenance_path)
    return {
        "program": program,
        "programPath": _workspace_relative(root, program_path),
        "renderedImage": _workspace_relative(root, render_path),
        "provenance": provenance["provenance"],
        "width": width,
        "height": height,
        "commandCount": len(commands),
    }


def _video_meta(video_path: Path) -> tuple[Path, dict[str, Any]]:
    meta_path = video_path.parent / "video.json"
    meta: dict[str, Any] = {}
    if meta_path.is_file():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            meta = {}
    return meta_path, meta


def _merge_video_meta(video_path: Path, updates: dict[str, Any]) -> dict[str, Any]:
    key = video_path.resolve()
    with _video_meta_locks_guard:
        lock = _video_meta_locks.setdefault(key, threading.Lock())
    with lock:
        meta_path, current = _video_meta(video_path)
        current.update(updates)
        temporary = meta_path.with_suffix(meta_path.suffix + ".tmp")
        temporary.write_text(json.dumps(current, indent=2, ensure_ascii=False), encoding="utf-8")
        temporary.replace(meta_path)
        return current


def _caption_seconds(value: str) -> float:
    parts = value.strip().replace(",", ".").split(":")
    if len(parts) == 2:
        parts.insert(0, "0")
    if len(parts) != 3:
        raise ValueError(f"invalid caption timestamp: {value}")
    return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])


def _parse_webvtt(source: str) -> list[dict[str, Any]]:
    cues: list[dict[str, Any]] = []
    for block in re.split(r"\r?\n\r?\n+", source):
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        timing_index = next((index for index, line in enumerate(lines) if "-->" in line), -1)
        if timing_index < 0:
            continue
        start_text, end_text = (part.strip().split()[0] for part in lines[timing_index].split("-->", 1))
        try:
            start = _caption_seconds(start_text)
            end = _caption_seconds(end_text)
        except ValueError:
            continue
        text = re.sub(r"<[^>]+>", "", " ".join(lines[timing_index + 1:])).strip()
        if text and end > start:
            cues.append({"start": round(start, 3), "end": round(end, 3), "text": text})
    return cues


def _caption_timestamp(seconds_value: float) -> str:
    milliseconds = max(0, round(seconds_value * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


def _captions_to_webvtt(cues: list[dict[str, Any]]) -> str:
    blocks = ["WEBVTT", ""]
    for index, cue in enumerate(cues, 1):
        blocks.extend((
            str(index),
            f"{_caption_timestamp(float(cue['start']))} --> {_caption_timestamp(float(cue['end']))}",
            str(cue["text"]),
            "",
        ))
    return "\n".join(blocks)


def _resolve_video(workspace_id: str, video_rel: str) -> tuple[Path, Path]:
    root = _workspace_root(workspace_id)
    try:
        video_path = _safe_workspace_child(root, video_rel)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not video_path.is_file():
        raise HTTPException(status_code=404, detail=f"video not found: {video_rel}")
    return root, video_path


@router.post("/captions")
def create_video_captions(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    workspace_id = str(body.get("workspaceId") or "")
    video_rel = str(body.get("video") or "")
    model_id = str(body.get("modelId") or "")
    if not workspace_id or not video_rel:
        raise HTTPException(status_code=400, detail="workspaceId and video are required")
    root, video_path = _resolve_video(workspace_id, video_rel)
    _, meta = _video_meta(video_path)
    duration = float(meta.get("duration") or _probe_duration_seconds(video_path) or 0)
    chunk_seconds = max(10, min(120, int(body.get("chunkSeconds") or 30)))
    chunks = max(1, int((duration + chunk_seconds - 0.001) // chunk_seconds)) if duration else 1
    job_id = uuid.uuid4().hex[:12]
    job: dict[str, Any] = {
        "id": job_id, "state": "running", "done": 0, "total": chunks,
        "elapsedSeconds": 0.0, "etaSeconds": round(duration * 0.3 + 2, 1),
        "captions": [], "captionSource": None, "error": None,
    }
    _extract_jobs[job_id] = job

    def work() -> None:
        started = time.monotonic()
        ffmpeg = _ffmpeg_executable()
        captions_path = video_path.parent / "captions.vtt"
        embedded_path = video_path.parent / f".captions-{job_id}.vtt"
        temporary_directory = video_path.parent / f".captions-{job_id}"
        try:
            embedded = subprocess.run(
                [ffmpeg, "-loglevel", "error", "-y", "-i", str(video_path), "-map", "0:s:0", "-f", "webvtt", str(embedded_path)],
                capture_output=True,
                check=False,
                timeout=max(30, int(duration) + 10),
            )
            cues = _parse_webvtt(embedded_path.read_text(encoding="utf-8", errors="replace")) if embedded.returncode == 0 and embedded_path.is_file() else []
            caption_source = "embedded"
            if not cues:
                if not model_id:
                    raise RuntimeError("video has no embedded subtitles and no audio transcription model is selected")
                temporary_directory.mkdir(parents=True, exist_ok=True)
                audio_chunks: list[tuple[int, float, float, Path]] = []
                for index in range(chunks):
                    if job.get("cancel"):
                        break
                    start = index * chunk_seconds
                    end = min(duration, start + chunk_seconds) if duration else start + chunk_seconds
                    audio_path = temporary_directory / f"audio-{index:04d}.wav"
                    extracted = subprocess.run(
                        [ffmpeg, "-loglevel", "error", "-y", "-ss", str(start), "-t", str(max(0.1, end - start)), "-i", str(video_path), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(audio_path)],
                        capture_output=True,
                        check=False,
                        timeout=max(30, int(end - start) * 2 + 10),
                    )
                    if extracted.returncode == 0 and audio_path.is_file() and audio_path.stat().st_size > 44:
                        audio_chunks.append((index, start, end, audio_path))
                if not audio_chunks and not job.get("cancel"):
                    raise RuntimeError("video has no extractable audio track")
                cues = []
                errors: list[str] = []
                concurrency = max(1, min(8, int(body.get("concurrency") or 4)))
                with ThreadPoolExecutor(max_workers=concurrency) as executor:
                    futures = {
                        executor.submit(_transcribe_audio_file, root, model_id, audio_path): (index, start, end)
                        for index, start, end, audio_path in audio_chunks
                    }
                    for future in as_completed(futures):
                        index, start, end = futures[future]
                        if job.get("cancel"):
                            continue
                        try:
                            text = future.result()
                            cues.append({"start": round(start, 3), "end": round(end, 3), "text": text})
                        except Exception as error:  # noqa: BLE001 - per-chunk failure is reported with the job
                            errors.append(f"chunk {index + 1}: {error}")
                        job["done"] = min(job["total"], job["done"] + 1)
                        elapsed = time.monotonic() - started
                        job["elapsedSeconds"] = round(elapsed, 1)
                        job["etaSeconds"] = round(max(0.0, (job["total"] - job["done"]) * (elapsed / max(1, job["done"]))), 1)
                cues.sort(key=lambda cue: float(cue["start"]))
                if not cues and not job.get("cancel"):
                    raise RuntimeError(errors[0] if errors else "audio transcription returned no captions")
                caption_source = f"transcribed:{model_id}"
            captions_path.write_text(_captions_to_webvtt(cues), encoding="utf-8")
            elapsed = time.monotonic() - started
            _merge_video_meta(video_path, {
                "captions": cues,
                "captionSource": caption_source,
                "lastCaptions": {
                    "count": len(cues),
                    "source": caption_source,
                    "modelId": model_id or None,
                    "elapsedSeconds": round(elapsed, 1),
                    "at": _utc_now(),
                },
            })
            job.update({
                "state": "done", "done": job["total"], "captions": cues,
                "captionSource": caption_source, "elapsedSeconds": round(elapsed, 1),
                "etaSeconds": 0.0, "interrupted": bool(job.get("cancel")),
            })
        except Exception as error:  # noqa: BLE001 - surfaced through job status
            job.update({"state": "error", "error": str(error)})
        finally:
            embedded_path.unlink(missing_ok=True)
            if temporary_directory.is_dir():
                shutil.rmtree(temporary_directory, ignore_errors=True)

    threading.Thread(target=work, name=f"video-captions-{job_id}", daemon=True).start()
    return {"jobId": job_id, "estimatedChunks": chunks}


@router.post("/captions/clear")
def clear_video_captions(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    workspace_id = str(body.get("workspaceId") or "")
    video_rel = str(body.get("video") or "")
    if not workspace_id or not video_rel:
        raise HTTPException(status_code=400, detail="workspaceId and video are required")
    _, video_path = _resolve_video(workspace_id, video_rel)
    (video_path.parent / "captions.vtt").unlink(missing_ok=True)
    _merge_video_meta(video_path, {"captions": [], "captionSource": None})
    return {"captions": [], "captionSource": None}


def _scene_marker_limit(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        limit = int(value)
    except (TypeError, ValueError) as error:
        raise HTTPException(status_code=400, detail="maxMarkers must be an integer") from error
    if limit <= 0:
        return None
    return min(10_000, limit)


def _scene_detection_float(
    value: Any,
    *,
    default: float,
    minimum: float,
    maximum: float,
    label: str,
) -> float:
    try:
        result = default if value is None or value == "" else float(value)
    except (TypeError, ValueError) as error:
        raise HTTPException(status_code=400, detail=f"{label} must be numeric") from error
    if not minimum <= result <= maximum:
        raise HTTPException(
            status_code=400,
            detail=f"{label} must be between {minimum:g} and {maximum:g}",
        )
    return result


def _docker_command(*arguments: str, timeout: float = 30.0) -> subprocess.CompletedProcess[str]:
    executable = shutil.which("docker")
    if not executable:
        raise HTTPException(status_code=503, detail="Docker is required to run the MediaMTX stream router")
    return subprocess.run(
        [executable, *arguments],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )


def _media_router_running() -> bool:
    result = _docker_command(
        "inspect",
        "--format",
        "{{.State.Running}}",
        _MEDIAMTX_CONTAINER,
    )
    return result.returncode == 0 and result.stdout.strip().lower() == "true"


def _stream_router_urls(host: str, stream_id: str) -> dict[str, str]:
    stream_id = _slug(stream_id)
    return {
        "publishWhip": f"http://{host}:8889/{stream_id}/whip",
        "publishRtmp": f"rtmp://{host}:1935/{stream_id}",
        "watchWhep": f"http://{host}:8889/{stream_id}/whep",
        "watchHls": f"http://{host}:8888/{stream_id}/index.m3u8",
        "sourceHls": f"http://{host}:8888/{stream_id}/index.m3u8",
    }


@router.get("/stream-router")
def stream_router_status(
    request: Request,
    streamId: str = "workbench",
    publicHost: str = "",
) -> dict[str, Any]:
    host = publicHost.strip() or request.url.hostname or "127.0.0.1"
    return {
        "running": _media_router_running(),
        "container": _MEDIAMTX_CONTAINER,
        "image": _MEDIAMTX_IMAGE,
        "streamId": _slug(streamId),
        "urls": _stream_router_urls(host, streamId),
    }


@router.post("/stream-router/start")
def start_stream_router(body: dict[str, Any] = Body(default={})) -> dict[str, Any]:
    if _media_router_running():
        return {"running": True, "started": False, "container": _MEDIAMTX_CONTAINER}
    inspect = _docker_command("inspect", _MEDIAMTX_CONTAINER)
    if inspect.returncode == 0:
        result = _docker_command("start", _MEDIAMTX_CONTAINER, timeout=60)
    else:
        result = _docker_command(
            "run",
            "--detach",
            "--name",
            _MEDIAMTX_CONTAINER,
            "--restart",
            "unless-stopped",
            "-e",
            "MTX_API=yes",
            "-p",
            "1935:1935",
            "-p",
            "8554:8554",
            "-p",
            "8888:8888",
            "-p",
            "8889:8889",
            "-p",
            "8189:8189/udp",
            "-p",
            "8890:8890/udp",
            "-p",
            "9997:9997",
            _MEDIAMTX_IMAGE,
            timeout=180,
        )
    if result.returncode != 0:
        raise HTTPException(
            status_code=502,
            detail=result.stderr.strip() or result.stdout.strip() or "MediaMTX failed to start",
        )
    return {
        "running": True,
        "started": True,
        "container": _MEDIAMTX_CONTAINER,
        "image": _MEDIAMTX_IMAGE,
    }


@router.post("/stream-router/stop")
def stop_stream_router() -> dict[str, Any]:
    if not _media_router_running():
        return {"running": False, "stopped": False, "container": _MEDIAMTX_CONTAINER}
    result = _docker_command("stop", "--time", "10", _MEDIAMTX_CONTAINER, timeout=30)
    if result.returncode != 0:
        raise HTTPException(
            status_code=502,
            detail=result.stderr.strip() or result.stdout.strip() or "MediaMTX failed to stop",
        )
    return {"running": False, "stopped": True, "container": _MEDIAMTX_CONTAINER}


def _stream_source_url(value: Any) -> str:
    source_url = str(value or "").strip()
    parsed = urllib.parse.urlparse(source_url)
    if parsed.scheme.lower() not in _STREAM_SOURCE_SCHEMES or not parsed.netloc:
        raise HTTPException(
            status_code=400,
            detail="sourceUrl must use http, https, rtsp, rtmp, rtmps, or srt",
        )
    return source_url


def _resolve_stream_source(source_url: str) -> str:
    host = (urllib.parse.urlparse(source_url).hostname or "").lower()
    if host not in {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}:
        return source_url
    try:
        import yt_dlp  # noqa: PLC0415
    except ImportError as error:
        raise RuntimeError("yt-dlp is required to consume a YouTube video URL") from error
    options = {
        "format": "bestvideo[height<=720]/best[height<=720]/best",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(options) as downloader:
        info = downloader.extract_info(source_url, download=False)
    resolved = str(info.get("url") or "").strip() if isinstance(info, dict) else ""
    if not resolved:
        raise RuntimeError("yt-dlp returned no playable video endpoint")
    return resolved


def _arc_recording_images(recording_dir: Path) -> list[Path]:
    images: list[tuple[int, Path]] = []
    root_image = recording_dir / "image.png"
    if root_image.is_file():
        images.append((-1, root_image))
    for child in recording_dir.iterdir() if recording_dir.is_dir() else []:
        image = child / "image.png"
        if not child.is_dir() or not image.is_file():
            continue
        try:
            ordinal = int(child.name)
        except ValueError:
            continue
        images.append((ordinal, image))
    return [path for _, path in sorted(images, key=lambda item: item[0])]


def _natural_path_key(path: Path) -> tuple[Any, ...]:
    return tuple(
        int(part) if part.isdigit() else part.lower()
        for segment in path.parts
        for part in re.split(r"(\d+)", segment)
        if part
    )


def _curated_source_images(root: Path, source_dir: Path) -> list[Path]:
    curated_root = _curated_games_container(root).resolve()
    resolved = source_dir.resolve()
    try:
        resolved.relative_to(curated_root)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail="curated source must be under data/arc3_games/curated/",
        ) from error
    images = [
        path
        for path in resolved.rglob("*")
        if path.is_file() and path.suffix.lower() in _IMAGE_SUFFIXES
    ]
    return sorted(images, key=lambda path: _natural_path_key(path.relative_to(resolved)))


@router.get("/curated-image-sources")
def list_curated_image_sources(workspaceId: str) -> dict[str, Any]:
    root = _workspace_root(workspaceId)
    data_root = _curated_games_container(root)
    sources: list[dict[str, Any]] = []
    if data_root.is_dir():
        for source_dir in sorted(
            (entry for entry in data_root.iterdir() if entry.is_dir()),
            key=lambda path: path.name.lower(),
        ):
            if source_dir.name.lower() in _CURATED_DATA_EXCLUDES:
                continue
            images = _curated_source_images(root, source_dir)
            if not images:
                continue
            sources.append(
                {
                    "path": source_dir.relative_to(root).as_posix(),
                    "label": source_dir.name,
                    "frames": len(images),
                    "preview": images[0].relative_to(root).as_posix(),
                }
            )
    return {"sources": sources}


@router.post("/curated-image-sources/import")
def import_curated_image_source(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    from PIL import Image  # noqa: PLC0415

    workspace_id = str(body.get("workspaceId") or "")
    source_rel = str(body.get("source") or "")
    if not workspace_id or not source_rel:
        raise HTTPException(status_code=400, detail="workspaceId and source are required")
    root = _workspace_root(workspace_id)
    try:
        source_dir = _safe_workspace_child(root, source_rel)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not source_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"curated image source not found: {source_rel}")
    source_images = _curated_source_images(root, source_dir)
    if not source_images:
        raise HTTPException(status_code=400, detail="curated source contains no supported images")
    output_dir = _vision_frames_root(root) / "curated_data" / _slug(source_rel)
    output_dir.mkdir(parents=True, exist_ok=True)
    frames: list[dict[str, Any]] = []
    for index, source_path in enumerate(source_images):
        output_path = output_dir / f"frame_{index:06d}.png"
        with Image.open(source_path) as image:
            provenance = _save_image_with_provenance(
                root,
                image.convert("RGBA"),
                output_path,
                operation="import_curated_data_frame",
                parent_image=source_path,
                source={
                    "curatedSource": source_rel,
                    "sourceImage": source_path.relative_to(root).as_posix(),
                    "frameIndex": index,
                },
                image_format="PNG",
            )
        frames.append(
            {
                "path": output_path.relative_to(root).as_posix(),
                "index": index,
                "atSeconds": float(index),
                "scene": index + 1,
                "provenance": provenance["provenance"],
            }
        )
    manifest_path = output_dir.parent / "curated_import.json"
    _atomic_json_write(
        manifest_path,
        {"source": source_rel, "frames": frames, "importedAt": _utc_now()},
    )
    return {
        "source": source_rel,
        "frames": frames,
        "manifest": manifest_path.relative_to(root).as_posix(),
    }


@router.get("/arc-recordings")
def list_arc_recordings(workspaceId: str) -> dict[str, Any]:
    root = _workspace_root(workspaceId)
    recordings: list[dict[str, Any]] = []
    for game_root in _all_game_dirs(root):
        for recording_dir in _iter_recording_dirs(game_root):
            images = _arc_recording_images(recording_dir)
            if not images:
                continue
            manifest_path = recording_dir / "recording.json"
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                manifest = {}
            recordings.append(
                {
                    "path": recording_dir.relative_to(root).as_posix(),
                    "gameId": str(manifest.get("game_id") or game_root.name),
                    "level": manifest.get("level"),
                    "frames": len(images),
                    "preview": images[0].relative_to(root).as_posix(),
                    "updatedAt": manifest.get("updated_at"),
                }
            )
    recordings.sort(key=lambda item: (item["gameId"], item["path"]))
    return {"recordings": recordings}


@router.post("/arc-recordings/import")
def import_arc_recording(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    from PIL import Image  # noqa: PLC0415

    workspace_id = str(body.get("workspaceId") or "")
    recording_rel = str(body.get("recording") or "")
    if not workspace_id or not recording_rel:
        raise HTTPException(status_code=400, detail="workspaceId and recording are required")
    root = _workspace_root(workspace_id)
    try:
        recording_dir = _safe_workspace_child(root, recording_rel)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not recording_dir.is_dir() or not (recording_dir / "recording.json").is_file():
        raise HTTPException(status_code=404, detail=f"ARC recording not found: {recording_rel}")
    try:
        recording_manifest = json.loads(
            (recording_dir / "recording.json").read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=400, detail="ARC recording manifest is invalid") from error
    recording_moves = (
        recording_manifest.get("moves")
        if isinstance(recording_manifest.get("moves"), list)
        else []
    )
    source_images = _arc_recording_images(recording_dir)
    if not source_images:
        raise HTTPException(status_code=400, detail="ARC recording contains no image sequence")
    output_dir = _vision_frames_root(root) / "arc_recordings" / _slug(recording_rel)
    output_dir.mkdir(parents=True, exist_ok=True)
    frames: list[dict[str, Any]] = []
    for index, source_path in enumerate(source_images):
        output_path = output_dir / f"frame_{index:06d}.png"
        node_state_path = source_path.parent / "state.json"
        try:
            node_state = json.loads(node_state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            node_state = {}
        move_count = 0 if source_path.parent == recording_dir else index
        move_list = [
            dict(move)
            for move in recording_moves[:move_count]
            if isinstance(move, dict)
        ]
        with Image.open(source_path) as image:
            provenance = _save_image_with_provenance(
                root,
                image.convert("RGBA"),
                output_path,
                operation="import_arc_playback_frame",
                parent_image=source_path,
                source={
                    "arcRecording": recording_rel,
                    "arcFrame": source_path.relative_to(recording_dir).as_posix(),
                    "frameIndex": index,
                    "moveCount": len(move_list),
                    "moveList": move_list,
                    "incomingAction": node_state.get("incoming_action"),
                    "actionData": node_state.get("action_data"),
                    "actionPath": node_state.get("action_path") or [],
                    "gameState": node_state.get("state"),
                    "level": node_state.get("level"),
                    "observation": node_state.get("observation"),
                },
                image_format="PNG",
            )
        frames.append(
            {
                "path": output_path.relative_to(root).as_posix(),
                "index": index,
                "atSeconds": float(index),
                "scene": index + 1,
                "provenance": provenance["provenance"],
            }
        )
    manifest_path = output_dir.parent / "recording_import.json"
    _atomic_json_write(
        manifest_path,
        {
            "sourceRecording": recording_rel,
            "frames": frames,
            "importedAt": _utc_now(),
        },
    )
    return {
        "recording": recording_rel,
        "frames": frames,
        "manifest": manifest_path.relative_to(root).as_posix(),
    }


@router.post("/stream-scenes")
def detect_stream_scenes(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Consume a standard external video stream and save frames at scene changes."""
    workspace_id = str(body.get("workspaceId") or "")
    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspaceId is required")
    source_url = _stream_source_url(body.get("sourceUrl"))
    stream_id = _slug(str(body.get("streamId") or "external-stream"))
    threshold = _scene_detection_float(
        body.get("threshold"),
        default=28.0,
        minimum=0.1,
        maximum=255.0,
        label="threshold",
    )
    samples_per_second = _scene_detection_float(
        body.get("samplesPerSecond"),
        default=4.0,
        minimum=0.25,
        maximum=30.0,
        label="samplesPerSecond",
    )
    min_scene_gap_seconds = _scene_detection_float(
        body.get("minSceneGapSeconds"),
        default=0.5,
        minimum=0.0,
        maximum=60.0,
        label="minSceneGapSeconds",
    )
    max_scenes = _scene_marker_limit(body.get("maxScenes"))
    max_seconds = _scene_detection_float(
        body.get("maxSeconds"),
        default=0.0,
        minimum=0.0,
        maximum=86_400.0,
        label="maxSeconds",
    )
    root = _workspace_root(workspace_id)
    output_dir = _vision_frames_root(root) / "live_streams" / stream_id
    output_dir.mkdir(parents=True, exist_ok=True)
    job_id = uuid.uuid4().hex[:12]
    job: dict[str, Any] = {
        "id": job_id,
        "state": "running",
        "done": 0,
        "total": 0,
        "elapsedSeconds": 0.0,
        "etaSeconds": None,
        "frames": [],
        "markers": [],
        "error": None,
        "sourceUrl": source_url,
        "streamId": stream_id,
    }
    _extract_jobs[job_id] = job

    def work() -> None:
        import imageio  # noqa: PLC0415
        import numpy as np  # noqa: PLC0415
        from PIL import Image  # noqa: PLC0415

        started = time.monotonic()
        reader = None
        try:
            resolved_source_url = _resolve_stream_source(source_url)
            reader = imageio.get_reader(resolved_source_url)
            metadata = reader.get_meta_data()
            fps = float(metadata.get("fps") or 24.0)
            sample_step = max(1, round(fps / samples_per_second))
            previous: Any = None
            last_marker_seconds = float("-inf")
            scene_index = 0
            for index, frame in enumerate(reader):
                if job.get("cancel"):
                    break
                at_seconds = index / fps
                if max_seconds and at_seconds >= max_seconds:
                    break
                if index % sample_step:
                    continue
                small = np.asarray(frame, dtype=np.int16)[::4, ::4]
                score = (
                    float(np.abs(small - previous).mean())
                    if previous is not None and small.shape == previous.shape
                    else threshold
                )
                if (
                    score >= threshold
                    and at_seconds - last_marker_seconds >= min_scene_gap_seconds
                ):
                    scene_index += 1
                    path = output_dir / f"scene_{scene_index:06d}_{int(round(at_seconds * 1000)):012d}.png"
                    provenance = _save_image_with_provenance(
                        root,
                        Image.fromarray(frame),
                        path,
                        operation="capture_stream_scene",
                        source={
                            "sourceStreamUrl": source_url,
                            "streamId": stream_id,
                            "atSeconds": round(at_seconds, 3),
                            "scene": scene_index,
                        },
                        image_format="PNG",
                    )
                    marker = {"atSeconds": round(at_seconds, 2), "score": round(score, 1)}
                    frame_row = {
                        "path": path.relative_to(root).as_posix(),
                        "index": scene_index - 1,
                        "atSeconds": round(at_seconds, 2),
                        "scene": scene_index,
                        "provenance": provenance["provenance"],
                    }
                    job["markers"] = [*job["markers"], marker]
                    job["frames"] = [*job["frames"], frame_row]
                    job["done"] = scene_index
                    last_marker_seconds = at_seconds
                    if max_scenes is not None and scene_index >= max_scenes:
                        break
                previous = small
                job["elapsedSeconds"] = round(time.monotonic() - started, 1)
            elapsed = time.monotonic() - started
            manifest_path = output_dir.parent / "stream.json"
            _atomic_json_write(
                manifest_path,
                {
                    "sourceUrl": source_url,
                    "streamId": stream_id,
                    "frames": job["frames"],
                    "markers": job["markers"],
                    "interrupted": bool(job.get("cancel")),
                    "elapsedSeconds": round(elapsed, 1),
                    "updatedAt": _utc_now(),
                },
            )
            job.update(
                {
                    "state": "done",
                    "elapsedSeconds": round(elapsed, 1),
                    "interrupted": bool(job.get("cancel")),
                    "manifest": manifest_path.relative_to(root).as_posix(),
                }
            )
        except Exception as error:  # noqa: BLE001 - surfaced through job status
            job.update({"state": "error", "error": str(error)})
        finally:
            if reader is not None:
                reader.close()

    threading.Thread(
        target=work,
        name=f"video-stream-scenes-{job_id}",
        daemon=True,
    ).start()
    return {"jobId": job_id, "streamId": stream_id, "sourceUrl": source_url}


@router.post("/scenes")
def detect_scenes(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Detect scene changes and save them as timeline markers.

    Samples the video a few frames per second and marks the places where the
    mean per-pixel difference between consecutive samples spikes over the
    threshold. Runs as a job; poll /extract/status for the progress bar. The
    markers persist in video.json as ``scenes``.
    """
    workspace_id = str(body.get("workspaceId") or "")
    video_rel = str(body.get("video") or "")
    if not workspace_id or not video_rel:
        raise HTTPException(status_code=400, detail="workspaceId and video are required")
    threshold = _scene_detection_float(
        body.get("threshold"),
        default=28.0,
        minimum=0.1,
        maximum=255.0,
        label="threshold",
    )
    samples_per_second = _scene_detection_float(
        body.get("samplesPerSecond"),
        default=4.0,
        minimum=0.25,
        maximum=30.0,
        label="samplesPerSecond",
    )
    min_scene_gap_seconds = _scene_detection_float(
        body.get("minSceneGapSeconds"),
        default=0.5,
        minimum=0.0,
        maximum=60.0,
        label="minSceneGapSeconds",
    )
    start_seconds = max(0.0, float(body.get("startSeconds") or 0.0))
    max_markers = _scene_marker_limit(body.get("maxMarkers"))
    root, video_path = _resolve_video(workspace_id, video_rel)
    try:
        import imageio  # noqa: F401, PLC0415
        import numpy  # noqa: F401, PLC0415
    except ImportError as error:
        raise HTTPException(status_code=500, detail="imageio/numpy are not installed in the server environment") from error

    meta_path, meta = _video_meta(video_path)
    duration = meta.get("duration") or _probe_duration_seconds(video_path)
    pace = float((meta.get("lastScenes") or {}).get("secondsPerVideoSecond") or 0.08)
    window = max(0.0, float(duration) - start_seconds) if duration else 60.0
    estimated_seconds = round(window * pace + 1.0, 1)
    job_id = uuid.uuid4().hex[:12]
    job: dict[str, Any] = {
        "id": job_id, "state": "running", "done": 0, "total": int(window) or 1,
        "elapsedSeconds": 0.0, "etaSeconds": estimated_seconds, "frames": [],
        "markers": [], "error": None,
    }
    _extract_jobs[job_id] = job

    def work() -> None:
        import imageio  # noqa: PLC0415
        import numpy as np  # noqa: PLC0415

        started = time.monotonic()
        # Resuming: keep every already-detected marker up to the start point
        # (including the marker we resume at) and append what this run finds.
        kept: list[dict[str, Any]] = [
            marker for marker in (meta.get("scenes") or [])
            if float(marker.get("atSeconds") or 0.0) <= start_seconds + 0.01
        ]
        markers: list[dict[str, Any]] = []
        try:
            reader = imageio.get_reader(str(video_path))
            try:
                fps = float(reader.get_meta_data().get("fps") or 24.0)
                sample_step = max(1, round(fps / samples_per_second))
                first_index = int(start_seconds * fps)
                previous: Any = None
                last_marker_seconds = max(
                    (
                        float(marker.get("atSeconds") or 0.0)
                        for marker in kept
                    ),
                    default=float("-inf"),
                )
                for index, frame in enumerate(reader):
                    if job.get("cancel"):
                        break
                    if index < first_index or index % sample_step:
                        continue
                    small = np.asarray(frame, dtype=np.int16)[::4, ::4]
                    if previous is not None and small.shape == previous.shape:
                        score = float(np.abs(small - previous).mean())
                        at_seconds = index / fps
                        if (
                            score >= threshold
                            and at_seconds - last_marker_seconds >= min_scene_gap_seconds
                        ):
                            markers.append({"atSeconds": round(at_seconds, 2), "score": round(score, 1)})
                            last_marker_seconds = at_seconds
                            if max_markers is not None and len(markers) >= max_markers:
                                break
                    previous = small
                    elapsed = time.monotonic() - started
                    job["done"] = int(index / fps - start_seconds)
                    job["elapsedSeconds"] = round(elapsed, 1)
                    processed = max(0.1, index / fps - start_seconds)
                    job["etaSeconds"] = round(max(0.0, (window - processed) * (elapsed / processed)), 1)
            finally:
                reader.close()
            elapsed = time.monotonic() - started
            seen: set[int] = set()
            merged: list[dict[str, Any]] = []
            for marker in sorted(kept + markers, key=lambda entry: float(entry.get("atSeconds") or 0.0)):
                stamp = int(round(float(marker.get("atSeconds") or 0.0) * 10))
                if stamp in seen:
                    continue
                seen.add(stamp)
                merged.append(marker)
            job.update({
                "state": "done", "markers": merged, "done": job["total"],
                "interrupted": bool(job.get("cancel")),
                "elapsedSeconds": round(elapsed, 1), "etaSeconds": 0.0,
            })
            last_scenes = {
                "count": len(merged),
                "newThisRun": len(markers),
                "resumedFromSeconds": start_seconds,
                "elapsedSeconds": round(elapsed, 1),
                "secondsPerVideoSecond": round(elapsed / window, 4) if window else None,
                "threshold": threshold,
                "samplesPerSecond": samples_per_second,
                "minSceneGapSeconds": min_scene_gap_seconds,
                "maxMarkers": max_markers,
                "at": _utc_now(),
            }
            try:
                _merge_video_meta(video_path, {
                    "scenes": merged,
                    "lastScenes": last_scenes,
                    **({"duration": duration} if duration else {}),
                })
            except OSError:
                pass
            _update_catalog_for_video(root, video_path, {}, extraction={
                "kind": "scenes",
                "count": len(markers),
                "threshold": threshold,
                "elapsedSeconds": round(elapsed, 1),
                "at": _utc_now(),
            })
        except Exception as error:  # noqa: BLE001 - surfaced via the job record
            job.update({"state": "error", "error": str(error)})

    threading.Thread(target=work, name=f"video-scenes-{job_id}", daemon=True).start()
    return {"jobId": job_id, "estimatedSeconds": estimated_seconds}


@router.post("/markers")
def save_markers(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Persist the scene-marker list (detected and/or hand-placed marks)."""
    workspace_id = str(body.get("workspaceId") or "")
    video_rel = str(body.get("video") or "")
    markers = body.get("markers")
    if not workspace_id or not video_rel:
        raise HTTPException(status_code=400, detail="workspaceId and video are required")
    if not isinstance(markers, list):
        raise HTTPException(status_code=400, detail="markers must be a list")
    cleaned = sorted(
        {
            round(float(marker.get("atSeconds") or 0), 2): {
                "atSeconds": round(float(marker.get("atSeconds") or 0), 2),
                "score": round(float(marker.get("score") or 0), 1),
            }
            for marker in markers
            if isinstance(marker, dict) and float(marker.get("atSeconds") or 0) >= 0
        }.values(),
        key=lambda marker: marker["atSeconds"],
    )
    _, video_path = _resolve_video(workspace_id, video_rel)
    _merge_video_meta(video_path, {"scenes": cleaned})
    return {"markers": cleaned}


@router.post("/segments")
def save_segments(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Persist the split/keep segment list a user built on the timeline."""
    workspace_id = str(body.get("workspaceId") or "")
    video_rel = str(body.get("video") or "")
    segments = body.get("segments")
    if not workspace_id or not video_rel:
        raise HTTPException(status_code=400, detail="workspaceId and video are required")
    if not isinstance(segments, list):
        raise HTTPException(status_code=400, detail="segments must be a list")
    cleaned = []
    for segment in segments:
        if not isinstance(segment, dict):
            continue
        start = max(0.0, float(segment.get("start") or 0.0))
        end = float(segment.get("end") or 0.0)
        if end <= start:
            continue
        cleaned.append({"start": round(start, 2), "end": round(end, 2), "keep": bool(segment.get("keep", True))})
    _, video_path = _resolve_video(workspace_id, video_rel)
    _merge_video_meta(video_path, {"segments": cleaned})
    return {"segments": cleaned}


@router.post("/trim")
def trim_video(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Re-encode only the kept segments into a new imported video.

    This is the delete step of split-and-trim: everything in a dropped
    segment is left out of the new file (video only — the trim re-encodes
    frames, it does not carry audio). Runs as a job; poll /extract/status.
    """
    workspace_id = str(body.get("workspaceId") or "")
    video_rel = str(body.get("video") or "")
    requested_name = str(body.get("name") or "").strip()
    if not workspace_id or not video_rel:
        raise HTTPException(status_code=400, detail="workspaceId and video are required")
    root, video_path = _resolve_video(workspace_id, video_rel)
    meta_path, meta = _video_meta(video_path)
    del meta_path
    segments = [
        segment for segment in (body.get("segments") or meta.get("segments") or [])
        if isinstance(segment, dict) and segment.get("keep", True)
    ]
    if not segments:
        raise HTTPException(status_code=400, detail="no kept segments to trim to")
    try:
        import imageio  # noqa: F401, PLC0415
    except ImportError as error:
        raise HTTPException(status_code=500, detail="imageio is not installed in the server environment") from error
    kept_total = sum(float(segment["end"]) - float(segment["start"]) for segment in segments)
    job_id = uuid.uuid4().hex[:12]
    job: dict[str, Any] = {
        "id": job_id, "state": "running", "done": 0, "total": max(1, int(kept_total)),
        "elapsedSeconds": 0.0, "etaSeconds": round(kept_total * 0.5, 1), "frames": [],
        "error": None, "resultPath": None,
    }
    _extract_jobs[job_id] = job
    title = requested_name or f"{meta.get('title') or video_path.parent.name}-trimmed"
    container = _imports_root(root)
    directory = container / _slug(title)
    if directory.exists():
        directory = container / f"{_slug(title)}-{uuid.uuid4().hex[:6]}"

    def work() -> None:
        import imageio  # noqa: PLC0415

        started = time.monotonic()
        try:
            directory.mkdir(parents=True, exist_ok=True)
            target = directory / "video.mp4"
            reader = imageio.get_reader(str(video_path))
            try:
                fps = float(reader.get_meta_data().get("fps") or 24.0)
                writer = imageio.get_writer(str(target), fps=fps, codec="libx264", quality=7)
                try:
                    ranges = [
                        (int(float(segment["start"]) * fps), int(float(segment["end"]) * fps))
                        for segment in segments
                    ]
                    written = 0
                    for index, frame in enumerate(reader):
                        if job.get("cancel"):
                            break
                        if not any(start <= index <= end for start, end in ranges):
                            if index > max(end for _, end in ranges):
                                break
                            continue
                        writer.append_data(frame)
                        written += 1
                        elapsed = time.monotonic() - started
                        job["done"] = int(written / fps)
                        job["elapsedSeconds"] = round(elapsed, 1)
                        processed = max(0.1, written / fps)
                        job["etaSeconds"] = round(max(0.0, (kept_total - processed) * (elapsed / processed)), 1)
                finally:
                    writer.close()
            finally:
                reader.close()
            (directory / "video.json").write_text(
                json.dumps({
                    "title": title,
                    "source": f"trim of {video_rel}",
                    "duration": round(kept_total, 2),
                    "segmentsFrom": meta.get("segments"),
                    "imported_at": _utc_now(),
                }, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            job.update({
                "state": "done", "done": job["total"], "etaSeconds": 0.0,
                "elapsedSeconds": round(time.monotonic() - started, 1),
                "resultPath": target.relative_to(root).as_posix(),
                "interrupted": bool(job.get("cancel")),
            })
            _update_catalog_for_video(root, video_path, {}, extraction={
                "kind": "trim",
                "resultPath": target.relative_to(root).as_posix(),
                "keptSeconds": round(kept_total, 1),
                "at": _utc_now(),
            })
        except Exception as error:  # noqa: BLE001 - surfaced via the job record
            shutil.rmtree(directory, ignore_errors=True)
            job.update({"state": "error", "error": str(error)})

    threading.Thread(target=work, name=f"video-trim-{job_id}", daemon=True).start()
    return {"jobId": job_id, "keptSeconds": round(kept_total, 1)}


def _luts_dir(root: Path) -> Path:
    return _imports_root(root) / "luts"


def _parse_cube_lut(path: Path) -> tuple[int, "Any"]:
    """Parse a .cube 3D LUT (the format LUT sites like FreshLUTs publish)."""
    import numpy as np  # noqa: PLC0415

    size = 0
    rows: list[list[float]] = []
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        upper = line.upper()
        if upper.startswith("LUT_3D_SIZE"):
            size = int(line.split()[-1])
            continue
        if upper.startswith(("TITLE", "DOMAIN_MIN", "DOMAIN_MAX", "LUT_1D_SIZE")):
            continue
        parts = line.split()
        if len(parts) == 3:
            try:
                rows.append([float(parts[0]), float(parts[1]), float(parts[2])])
            except ValueError:
                continue
    if size <= 1 or len(rows) != size ** 3:
        raise ValueError(f"not a valid 3D .cube LUT: {path.name} (size={size}, rows={len(rows)})")
    table = np.asarray(rows, dtype=np.float32).reshape((size, size, size, 3))  # [b][g][r]
    return size, table


def _apply_cube_lut(image: "Any", lut_path: Path) -> "Any":
    """Color-grade one frame through a .cube LUT (trilinear interpolation)."""
    import numpy as np  # noqa: PLC0415
    from PIL import Image  # noqa: PLC0415

    size, table = _parse_cube_lut(lut_path)
    pixels = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
    coords = pixels * (size - 1)
    base = np.floor(coords).astype(np.int32)
    base = np.clip(base, 0, size - 2)
    frac = coords - base
    r0, g0, b0 = base[..., 0], base[..., 1], base[..., 2]
    fr, fg, fb = frac[..., 0:1], frac[..., 1:2], frac[..., 2:3]

    def sample(ri: "Any", gi: "Any", bi: "Any") -> "Any":
        return table[bi, gi, ri]

    c000 = sample(r0, g0, b0)
    c100 = sample(r0 + 1, g0, b0)
    c010 = sample(r0, g0 + 1, b0)
    c110 = sample(r0 + 1, g0 + 1, b0)
    c001 = sample(r0, g0, b0 + 1)
    c101 = sample(r0 + 1, g0, b0 + 1)
    c011 = sample(r0, g0 + 1, b0 + 1)
    c111 = sample(r0 + 1, g0 + 1, b0 + 1)
    c00 = c000 * (1 - fr) + c100 * fr
    c10 = c010 * (1 - fr) + c110 * fr
    c01 = c001 * (1 - fr) + c101 * fr
    c11 = c011 * (1 - fr) + c111 * fr
    c0 = c00 * (1 - fg) + c10 * fg
    c1 = c01 * (1 - fg) + c11 * fg
    out = c0 * (1 - fb) + c1 * fb
    return Image.fromarray(np.clip(out * 255.0, 0, 255).astype(np.uint8))


def _filters_path(root: Path) -> Path:
    return _imports_root(root) / "filter_catalog.json"


# Built-in prepass filters; the JSON file beside the videos lets anyone
# publish parameterized variants for the editing tools to load.
_BUILTIN_FILTERS = [
    {"id": "cartoon", "title": "Convert to cartoon", "filter": "cartoon",
     "params": {"colors": 8, "scale": 8},
     "description": "Flat quantized color regions with darkened edges", "builtin": True},
    {"id": "pixelate", "title": "Lower quality (turtle-friendly)", "filter": "pixelate",
     "params": {"colors": 8, "scale": 8},
     "description": "Blocky low-res + reduced palette so objects reduce to a small redraw program", "builtin": True},
    {"id": "downscale", "title": "Decrease resolution", "filter": "downscale",
     "params": {"colors": 8, "scale": 2},
     "description": "Generic 1/N resolution decrease, nothing else", "builtin": True},
]


@router.get("/filters")
def list_filters(workspaceId: str) -> dict[str, Any]:
    """The loadable filter catalog: built-ins, published customs, and any
    .cube LUTs dropped into data/video_import/luts/ (e.g. from LUT sites)."""
    root = _workspace_root(workspaceId)
    path = _filters_path(root)
    published: list[dict[str, Any]] = []
    if path.is_file():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            published = loaded if isinstance(loaded, list) else []
        except (OSError, json.JSONDecodeError) as error:
            raise HTTPException(status_code=400, detail=f"filter_catalog.json is not valid JSON: {error}") from error
    luts_dir = _luts_dir(root)
    luts_dir.mkdir(parents=True, exist_ok=True)
    luts = [
        {
            "id": f"lut:{entry.stem}",
            "title": f"LUT · {entry.stem}",
            "filter": "lut",
            "lutPath": entry.relative_to(root).as_posix(),
            "params": {},
            "description": f".cube color LUT ({entry.name})",
            "lut": True,
        }
        for entry in sorted(luts_dir.glob("*.cube"))
    ]
    return {
        "filters": _apply_filter_flags(root, [*_BUILTIN_FILTERS, *published, *luts, *_discover_skills(root)]),
        "path": path.relative_to(root).as_posix(),
        "lutsDir": luts_dir.relative_to(root).as_posix(),
        "skillsDir": _skills_dir(root).relative_to(root).as_posix(),
        # The full vote ledger, including non-filter actors such as group
        # selectors (select:unique, select:spread, ...).
        "votes": (_load_filter_flags(root).get("votes") if isinstance(_load_filter_flags(root).get("votes"), dict) else {}),
    }


def _filter_flags_path(root: Path) -> Path:
    return _imports_root(root) / "filter_flags.json"


def _load_filter_flags(root: Path) -> dict[str, Any]:
    path = _filter_flags_path(root)
    if path.is_file():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                return loaded
        except (OSError, json.JSONDecodeError):
            pass
    return {}


def _apply_filter_flags(root: Path, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Annotate entries with their historical vote score and order the view:
    active filters sort by votes (desc, stable), excluded ones (scan-flagged
    retinters + manually disabled) sink to the bottom."""
    flags = _load_filter_flags(root)
    retinters = set(flags.get("retinters") or [])
    disabled = set(flags.get("disabled") or [])
    votes = flags.get("votes") if isinstance(flags.get("votes"), dict) else {}
    kept: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for entry in entries:
        entry_id = entry.get("id")
        score = int(votes.get(str(entry_id), 0) or 0)
        if entry_id in disabled:
            excluded.append({**entry, "votes": score, "excluded": True, "disabled": True,
                             "title": f"{entry['title']} (disabled)"})
        elif entry_id in retinters:
            excluded.append({**entry, "votes": score, "retinter": True, "excluded": True,
                             "title": f"{entry['title']} (retinter — excluded)"})
        else:
            kept.append({**entry, "votes": score})
    kept.sort(key=lambda item: -int(item.get("votes") or 0))
    excluded.sort(key=lambda item: -int(item.get("votes") or 0))
    return [*kept, *excluded]


@router.post("/filters/vote")
def vote_filter(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Up/downvote one filter. Votes accumulate as history in
    filter_flags.json and drive the ordering of the combo and the gallery."""
    workspace_id = str(body.get("workspaceId") or "")
    filter_id = str(body.get("filterId") or "")
    delta = max(-10, min(10, int(body.get("delta") or 0)))
    if not workspace_id or not filter_id or not delta:
        raise HTTPException(status_code=400, detail="workspaceId, filterId, and a non-zero delta are required")
    root = _workspace_root(workspace_id)
    flags = _load_filter_flags(root)
    votes = flags.get("votes") if isinstance(flags.get("votes"), dict) else {}
    votes[filter_id] = int(votes.get(filter_id, 0) or 0) + delta
    flags["votes"] = votes
    _filter_flags_path(root).write_text(json.dumps(flags, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"filterId": filter_id, "votes": votes[filter_id], "filters": list_filters(workspace_id)["filters"]}


@router.post("/filters/disable")
def set_filter_disabled(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Disable or re-enable one filter by id — e.g. straight from its output
    tile in the gallery. Re-enabling also clears a retinter scan flag."""
    workspace_id = str(body.get("workspaceId") or "")
    filter_id = str(body.get("filterId") or "")
    disabled = bool(body.get("disabled"))
    if not workspace_id or not filter_id:
        raise HTTPException(status_code=400, detail="workspaceId and filterId are required")
    root = _workspace_root(workspace_id)
    flags = _load_filter_flags(root)
    disabled_set = set(flags.get("disabled") or [])
    retinter_set = set(flags.get("retinters") or [])
    votes = flags.get("votes") if isinstance(flags.get("votes"), dict) else {}
    if disabled:
        disabled_set.add(filter_id)
        # Choosing to exclude a filter is an extreme downvote in its history.
        votes[filter_id] = int(votes.get(filter_id, 0) or 0) - 10
    else:
        disabled_set.discard(filter_id)
        retinter_set.discard(filter_id)
    flags["disabled"] = sorted(disabled_set)
    flags["retinters"] = sorted(retinter_set)
    flags["votes"] = votes
    _filter_flags_path(root).write_text(json.dumps(flags, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"filterId": filter_id, "disabled": disabled, "filters": list_filters(workspace_id)["filters"]}


@router.post("/filters/classify-retinters")
def classify_retinters(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Find filters that are just proportional mass retinters and flag them.

    Test: render each filter against two probes — the complex test card and a
    structure probe. A filter is a *retinter* when its output is (almost)
    purely a pointwise color remap: every input color maps to one output
    color (low per-color output variance) AND edge structure is preserved,
    i.e. it adds/removes no spatial content. Flags persist in
    filter_flags.json; flagged filters are excluded from the active set.

    Runs as a job — poll /extract/status; the finished job carries
    ``retinters`` (flagged ids) and ``details``."""
    workspace_id = str(body.get("workspaceId") or "")
    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspaceId is required")
    root = _workspace_root(workspace_id)
    from PIL import Image  # noqa: PLC0415
    import numpy as np  # noqa: PLC0415

    path = _filters_path(root)
    published: list[dict[str, Any]] = []
    if path.is_file():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            published = loaded if isinstance(loaded, list) else []
        except (OSError, json.JSONDecodeError):
            published = []
    luts_dir = _luts_dir(root)
    lut_entries = [
        {"id": f"lut:{entry.stem}", "title": f"LUT · {entry.stem}", "filter": "lut",
         "lutPath": entry.relative_to(root).as_posix(), "params": {}}
        for entry in sorted(luts_dir.glob("*.cube"))
    ] if luts_dir.is_dir() else []
    entries = [entry for entry in [*_BUILTIN_FILTERS, *published, *lut_entries, *_discover_skills(root)]
               if not entry.get("broken")]
    base = _complex_test_card()
    base.thumbnail((240, 240))
    base_array = np.asarray(base, dtype=np.float64)

    def edge_energy(array: "Any") -> float:
        gray = array.mean(axis=2)
        gx = np.abs(np.diff(gray, axis=1)).mean()
        gy = np.abs(np.diff(gray, axis=0)).mean()
        return float(gx + gy)

    base_edges = edge_energy(base_array)
    # Quantized input colors -> is the output a single color per input color?
    quantized = (base_array // 16).astype(np.int32)
    color_keys = quantized[:, :, 0] * 10000 + quantized[:, :, 1] * 100 + quantized[:, :, 2]

    job_id = uuid.uuid4().hex[:12]
    job: dict[str, Any] = {
        "id": job_id, "state": "running", "done": 0, "total": len(entries),
        "elapsedSeconds": 0.0, "etaSeconds": round(len(entries) * 0.2, 1),
        "retinters": [], "details": [], "error": None,
    }
    _extract_jobs[job_id] = job

    def work() -> None:
        started = time.monotonic()
        retinters: list[str] = []
        details: list[dict[str, Any]] = []
        try:
            for entry in entries:
                if job.get("cancel"):
                    break
                record: dict[str, Any] = {"id": entry["id"], "title": entry["title"]}
                try:
                    spec = {
                        "filter": entry.get("filter"), "params": entry.get("params") or {},
                        "lutPath": entry.get("lutPath"), "skillPath": entry.get("skillPath"),
                        "colors": (entry.get("params") or {}).get("colors"),
                        "scale": (entry.get("params") or {}).get("scale"),
                    }
                    _, transform = _resolve_transform(root, spec)
                    out = transform(base.copy()).convert("RGB")
                    out_array = np.asarray(out.resize(base.size), dtype=np.float64)
                    # 1. pointwise-ness: variance of output color per input color
                    spreads: list[float] = []
                    for key in np.unique(color_keys)[:160]:
                        mask = color_keys == key
                        if int(mask.sum()) < 8:
                            continue
                        spreads.append(float(out_array[mask].std(axis=0).mean()))
                    pointwise = float(np.mean(spreads)) if spreads else 255.0
                    # 2. structure preserved: edge energy stays in proportion
                    out_edges = edge_energy(out_array)
                    edge_ratio = out_edges / max(1e-6, base_edges)
                    # 3. it must actually change something
                    changed = float(np.abs(out_array - base_array).mean()) > 2.0
                    is_retinter = changed and pointwise < 6.0 and 0.35 <= edge_ratio <= 3.0
                    record.update({
                        "pointwiseSpread": round(pointwise, 2),
                        "edgeRatio": round(edge_ratio, 2),
                        "retinter": is_retinter,
                    })
                    if is_retinter:
                        retinters.append(str(entry["id"]))
                except Exception as error:  # noqa: BLE001 - one bad filter must not sink the scan
                    record["error"] = str(error)
                details.append(record)
                elapsed = time.monotonic() - started
                job["done"] = len(details)
                job["elapsedSeconds"] = round(elapsed, 1)
                job["etaSeconds"] = round(max(0.0, (len(entries) - len(details)) * (elapsed / max(1, len(details)))), 1)
            flags = _load_filter_flags(root)
            flags["retinters"] = sorted(retinters)
            flags["classifiedAt"] = _utc_now()
            _filter_flags_path(root).write_text(json.dumps(flags, indent=2, ensure_ascii=False), encoding="utf-8")
            job.update({
                "state": "done", "retinters": retinters, "details": details,
                "etaSeconds": 0.0, "interrupted": bool(job.get("cancel")),
            })
        except Exception as error:  # noqa: BLE001 - surfaced via the job record
            job.update({"state": "error", "error": str(error)})

    threading.Thread(target=work, name=f"retinter-scan-{job_id}", daemon=True).start()
    return {"jobId": job_id, "count": len(entries)}


@router.post("/filters")
def publish_filter(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Publish one custom filter (a named base-filter + parameter preset)."""
    workspace_id = str(body.get("workspaceId") or "")
    title = str(body.get("title") or "").strip()
    base = str(body.get("filter") or "")
    if not workspace_id or not title:
        raise HTTPException(status_code=400, detail="workspaceId and title are required")
    if base not in {"cartoon", "pixelate", "downscale"}:
        raise HTTPException(status_code=400, detail="filter must be cartoon, pixelate, or downscale")
    params = body.get("params") if isinstance(body.get("params"), dict) else {}
    entry = {
        "id": _slug(title),
        "title": title,
        "filter": base,
        "params": {
            "colors": max(2, min(64, int(params.get("colors") or 8))),
            "scale": max(2, min(32, int(params.get("scale") or 8))),
        },
        "description": str(body.get("description") or "").strip(),
        "publishedAt": _utc_now(),
    }
    root = _workspace_root(workspace_id)
    path = _filters_path(root)
    published: list[dict[str, Any]] = []
    if path.is_file():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            published = loaded if isinstance(loaded, list) else []
        except (OSError, json.JSONDecodeError):
            published = []
    published = [item for item in published if item.get("id") != entry["id"]]
    published.append(entry)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(published, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"filters": [*_BUILTIN_FILTERS, *published], "published": entry}


def _apply_prepass_filter(image: "Any", filter_name: str, colors: int, scale: int) -> "Any":
    """One frame through a prepass filter (PIL Image in → PIL Image out).

    cartoon    quantized flat-color regions with darkened edges
    pixelate   blocky low-res + reduced palette (turtle-program friendly)
    downscale  generic resolution decrease by 1/scale, nothing else
    """
    from PIL import Image, ImageFilter, ImageOps  # noqa: PLC0415

    if filter_name == "downscale":
        width, height = image.size
        return image.resize((max(1, width // scale), max(1, height // scale)), Image.LANCZOS)
    if filter_name == "pixelate":
        width, height = image.size
        small = image.resize((max(1, width // scale), max(1, height // scale)), Image.BILINEAR)
        blocky = small.quantize(colors=max(2, colors)).convert("RGB")
        return blocky.resize((width, height), Image.NEAREST)
    if filter_name == "cartoon":
        flat = image.convert("RGB").quantize(colors=max(2, colors)).convert("RGB")
        edges = ImageOps.invert(image.convert("L").filter(ImageFilter.FIND_EDGES))
        edges = edges.point(lambda value: 0 if value < 200 else 255)
        from PIL import ImageChops  # noqa: PLC0415

        return ImageChops.multiply(flat, Image.merge("RGB", (edges, edges, edges)))
    raise ValueError(f"unknown filter: {filter_name}")


def _skills_dir(root: Path) -> Path:
    return _imports_root(root) / "filter_skills"


_EXAMPLE_SKILL = '''"""Example image-editing skill: grayscale + posterize.

A skill is a plain Python file the workbench calls directly (no LLM in the
loop): declare SKILL metadata and an apply(image, params) function that takes
and returns a PIL Image. Drop more .py files beside this one to publish them.
"""

from PIL import Image, ImageOps

SKILL = {
    "title": "Grayscale posterize",
    "description": "Grayscale the frame, then posterize to a few tone bands.",
    "params": {"bits": 3},
}


def apply(image: Image.Image, params: dict) -> Image.Image:
    bits = max(1, min(8, int(params.get("bits") or 3)))
    return ImageOps.posterize(image.convert("L").convert("RGB"), bits)
'''


def _discover_skills(root: Path) -> list[dict[str, Any]]:
    """Filter skills: Python files in filter_skills/, called by the workbench
    itself (never through a model)."""
    directory = _skills_dir(root)
    directory.mkdir(parents=True, exist_ok=True)
    example = directory / "grayscale_posterize.py"
    if not any(directory.glob("*.py")):
        example.write_text(_EXAMPLE_SKILL, encoding="utf-8")
    skills: list[dict[str, Any]] = []
    for entry in sorted(directory.glob("*.py")):
        meta: dict[str, Any] = {}
        try:
            module = _load_skill_module(entry)
            declared = getattr(module, "SKILL", None)
            if isinstance(declared, dict):
                meta = declared
        except Exception as error:  # noqa: BLE001 - a broken skill still lists
            meta = {"title": entry.stem, "description": f"failed to load: {error}", "broken": True}
        skills.append({
            "id": f"skill:{entry.stem}",
            "title": str(meta.get("title") or entry.stem),
            "filter": "skill",
            "skillPath": entry.relative_to(root).as_posix(),
            "params": meta.get("params") if isinstance(meta.get("params"), dict) else {},
            # Optional per-param choice lists — the UI renders these as combos.
            "paramChoices": meta.get("paramChoices") if isinstance(meta.get("paramChoices"), dict) else {},
            # Optional per-param candidate grids for permutation runs.
            "paramGrid": meta.get("paramGrid") if isinstance(meta.get("paramGrid"), dict) else {},
            "description": str(meta.get("description") or f"Python skill ({entry.name})"),
            "skill": True,
            **({"broken": True} if meta.get("broken") else {}),
        })
    # A skill whose params have exactly one choice-list also expands into one
    # entry per choice, so the main filter combo offers every setting directly.
    expanded: list[dict[str, Any]] = []
    for skill in skills:
        choices = skill.get("paramChoices") or {}
        if len(choices) == 1 and not skill.get("broken"):
            key, values = next(iter(choices.items()))
            for value in values:
                expanded.append({
                    **skill,
                    "id": f"{skill['id']}:{value}",
                    "title": f"{skill['title']} · {value}",
                    "params": {**(skill.get("params") or {}), key: value},
                })
    return [*skills, *expanded]


def _load_skill_module(path: Path) -> Any:
    import importlib.util  # noqa: PLC0415

    spec = importlib.util.spec_from_file_location(f"video_filter_skill_{path.stem}_{uuid.uuid4().hex[:6]}", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load skill: {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _resolve_transform(root: Path, body: dict[str, Any]) -> tuple[str, Any]:
    """Build the frame transform for a /filter request.

    Returns (label, transform) where transform is PIL Image -> PIL Image.
    Built-ins run in-process; LUTs are .cube files; skills are Python files
    the workbench calls directly.
    """
    filter_name = str(body.get("filter") or "")
    colors = max(2, min(64, int(body.get("colors") or 8)))
    scale = max(2, min(32, int(body.get("scale") or 8)))
    if filter_name in {"cartoon", "pixelate", "downscale"}:
        return filter_name, lambda image: _apply_prepass_filter(image, filter_name, colors, scale)
    if filter_name == "lut":
        lut_rel = str(body.get("lutPath") or "")
        if not lut_rel:
            raise HTTPException(status_code=400, detail="lutPath is required for the lut filter")
        lut_path = _safe_workspace_child(root, lut_rel)
        if not lut_path.is_file():
            raise HTTPException(status_code=404, detail=f"LUT not found: {lut_rel}")
        return f"lut-{lut_path.stem}", lambda image: _apply_cube_lut(image, lut_path)
    if filter_name == "skill":
        skill_rel = str(body.get("skillPath") or "")
        if not skill_rel:
            raise HTTPException(status_code=400, detail="skillPath is required for the skill filter")
        skill_path = _safe_workspace_child(root, skill_rel)
        if not skill_path.is_file():
            raise HTTPException(status_code=404, detail=f"skill not found: {skill_rel}")
        module = _load_skill_module(skill_path)
        if not callable(getattr(module, "apply", None)):
            raise HTTPException(status_code=400, detail=f"skill {skill_path.name} exports no apply(image, params)")
        params = body.get("params") if isinstance(body.get("params"), dict) else {}
        return f"skill-{skill_path.stem}", lambda image: module.apply(image, dict(params))
    raise HTTPException(status_code=400, detail="filter must be cartoon, pixelate, downscale, lut, or skill")


@router.post("/filter")
def apply_filter(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Apply a prepass filter to a whole video or to the extracted frames.

    Video mode re-encodes into a new imported video (a job — poll
    /extract/status); frames mode writes filtered copies beside the originals
    and returns the new frame paths immediately.
    """
    workspace_id = str(body.get("workspaceId") or "")
    apply_to = str(body.get("applyTo") or "frames")
    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspaceId is required")
    root = _workspace_root(workspace_id)
    label, transform = _resolve_chain(root, body)
    from PIL import Image  # noqa: PLC0415

    if apply_to == "frames":
        frame_paths = body.get("frames")
        if not isinstance(frame_paths, list) or not frame_paths:
            raise HTTPException(status_code=400, detail="frames must be a non-empty list of paths")
        results: list[dict[str, Any]] = []
        for frame_rel in frame_paths:
            source = _safe_workspace_child(root, str(frame_rel))
            if not source.is_file():
                raise HTTPException(status_code=404, detail=f"frame not found: {frame_rel}")
            filtered_dir = source.parent / f"filtered_{label}"
            filtered_dir.mkdir(parents=True, exist_ok=True)
            target = filtered_dir / source.name
            with Image.open(source) as image:
                rendered = transform(image.convert("RGB"))
                provenance = _save_image_with_provenance(
                    root,
                    rendered,
                    target,
                    operation="apply_filter_chain",
                    parent_image=source,
                    source={"filter": label},
                    transform={"filter": label},
                )
            results.append({"source": str(frame_rel), "path": target.relative_to(root).as_posix(), "provenance": provenance["provenance"]})
        return {"filter": label, "frames": results, "count": len(results)}

    # applyTo == "video": re-encode the whole video through the filter.
    video_rel = str(body.get("video") or "")
    if not video_rel:
        raise HTTPException(status_code=400, detail="video is required when applyTo is video")
    root, video_path = _resolve_video(workspace_id, video_rel)
    _, meta = _video_meta(video_path)
    duration = meta.get("duration") or _probe_duration_seconds(video_path) or 60.0
    title = f"{meta.get('title') or video_path.parent.name}-{label}"
    container = _imports_root(root)
    directory = container / _slug(title)
    if directory.exists():
        directory = container / f"{_slug(title)}-{uuid.uuid4().hex[:6]}"
    job_id = uuid.uuid4().hex[:12]
    job: dict[str, Any] = {
        "id": job_id, "state": "running", "done": 0, "total": max(1, int(duration)),
        "elapsedSeconds": 0.0, "etaSeconds": round(float(duration) * 0.6, 1), "frames": [],
        "error": None, "resultPath": None,
    }
    _extract_jobs[job_id] = job

    def work() -> None:
        import imageio  # noqa: PLC0415
        import numpy as np  # noqa: PLC0415

        started = time.monotonic()
        try:
            directory.mkdir(parents=True, exist_ok=True)
            target = directory / "video.mp4"
            reader = imageio.get_reader(str(video_path))
            try:
                fps = float(reader.get_meta_data().get("fps") or 24.0)
                writer = None
                try:
                    for index, frame in enumerate(reader):
                        if job.get("cancel"):
                            break
                        filtered = transform(Image.fromarray(frame).convert("RGB"))
                        data = np.asarray(filtered.convert("RGB"))
                        if writer is None:
                            writer = imageio.get_writer(str(target), fps=fps, codec="libx264", quality=7)
                        writer.append_data(data)
                        elapsed = time.monotonic() - started
                        processed = (index + 1) / fps
                        job["done"] = int(processed)
                        job["elapsedSeconds"] = round(elapsed, 1)
                        job["etaSeconds"] = round(max(0.0, (float(duration) - processed) * (elapsed / max(0.1, processed))), 1)
                finally:
                    if writer is not None:
                        writer.close()
            finally:
                reader.close()
            (directory / "video.json").write_text(
                json.dumps({
                    "title": title,
                    "source": f"{label} filter of {video_rel}",
                    "duration": duration,
                    "filter": {"name": label},
                    "imported_at": _utc_now(),
                }, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            job.update({
                "state": "done", "done": job["total"], "etaSeconds": 0.0,
                "elapsedSeconds": round(time.monotonic() - started, 1),
                "resultPath": target.relative_to(root).as_posix(),
                "interrupted": bool(job.get("cancel")),
            })
            _update_catalog_for_video(root, video_path, {}, extraction={
                "kind": f"filter:{label}",
                "resultPath": target.relative_to(root).as_posix(),
                "at": _utc_now(),
            })
        except Exception as error:  # noqa: BLE001 - surfaced via the job record
            shutil.rmtree(directory, ignore_errors=True)
            job.update({"state": "error", "error": str(error)})

    threading.Thread(target=work, name=f"video-filter-{job_id}", daemon=True).start()
    return {"jobId": job_id, "title": title}


def _complex_test_card(size: tuple[int, int] = (480, 300)) -> "Any":
    """A generated 'complex' sample image for filter previews: gradients,
    overlapping shapes, thin lines, and text-like ticks — enough structure to
    show what a prepass does before touching real frames."""
    import numpy as np  # noqa: PLC0415
    from PIL import Image, ImageDraw  # noqa: PLC0415

    width, height = size
    x = np.linspace(0, 1, width, dtype=np.float32)
    y = np.linspace(0, 1, height, dtype=np.float32)[:, None]
    red = (np.tile(x, (height, 1)) * 255)
    green = (np.tile(y, (1, width)) * 255)
    blue = ((np.sin(np.tile(x, (height, 1)) * 12.0) * 0.5 + 0.5) * 255)
    base = np.stack([red, green, blue], axis=-1).astype(np.uint8)
    image = Image.fromarray(base, "RGB")
    draw = ImageDraw.Draw(image)
    draw.ellipse([30, 40, 170, 180], fill=(220, 60, 50), outline=(0, 0, 0), width=3)
    draw.rectangle([120, 100, 300, 220], fill=(40, 90, 200), outline=(255, 255, 255), width=2)
    draw.polygon([(330, 40), (450, 90), (390, 200), (310, 150)], fill=(60, 180, 90), outline=(0, 0, 0))
    for offset in range(0, width, 24):
        draw.line([(offset, height - 40), (offset + 18, height - 8)], fill=(0, 0, 0), width=2)
    for tick in range(12):
        draw.rectangle([10 + tick * 38, 10, 32 + tick * 38, 22], fill=((tick * 40) % 255, 255 - (tick * 30) % 255, (tick * 70) % 255))
    return image


def _resolve_chain(root: Path, body: dict[str, Any]) -> tuple[str, Any]:
    """Resolve either one filter spec or a ``chain`` of them into a single
    composed transform (applied in order)."""
    chain = body.get("chain")
    if not isinstance(chain, list) or not chain:
        return _resolve_transform(root, body)
    steps = [_resolve_transform(root, dict(spec)) for spec in chain if isinstance(spec, dict)]
    if not steps:
        raise HTTPException(status_code=400, detail="chain held no valid filter specs")

    def composed(image: "Any") -> "Any":
        for _, transform in steps:
            image = transform(image.convert("RGB") if hasattr(image, "convert") else image)
        return image

    label = "+".join(label for label, _ in steps)
    return label, composed


@router.post("/filter-preview")
def preview_filter(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Apply a prepass (or a whole chain) to ONE image; return before/after.

    The source is, in order of preference: an explicit ``image`` path, the
    frame of ``video`` at ``atSeconds`` (pick any frame on the player), or a
    generated complex test card so filters can be previewed before any frames
    exist.
    """
    workspace_id = str(body.get("workspaceId") or "")
    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspaceId is required")
    root = _workspace_root(workspace_id)
    label, transform = _resolve_chain(root, body)
    from PIL import Image  # noqa: PLC0415

    previews_dir = _imports_root(root) / "previews"
    previews_dir.mkdir(parents=True, exist_ok=True)
    image_rel = str(body.get("image") or "")
    video_rel = str(body.get("video") or "")
    at_seconds = body.get("atSeconds")
    base_parent_path: Path | None = None
    base_source: dict[str, Any] = {}
    if image_rel:
        source_path = _safe_workspace_child(root, image_rel)
        if not source_path.is_file():
            raise HTTPException(status_code=404, detail=f"preview image not found: {image_rel}")
        with Image.open(source_path) as loaded:
            source = loaded.convert("RGB")
        before_path = source_path
        before_rel = image_rel
    elif video_rel and at_seconds is not None:
        # Grab the exact frame under the player's time cursor.
        import imageio  # noqa: PLC0415

        _, video_path = _resolve_video(workspace_id, video_rel)
        reader = imageio.get_reader(str(video_path))
        try:
            fps = float(reader.get_meta_data().get("fps") or 24.0)
            index = max(0, int(float(at_seconds) * fps))
            try:
                frame = reader.get_data(index)
            except (IndexError, ValueError) as error:
                raise HTTPException(status_code=400, detail=f"no frame at {at_seconds}s: {error}") from error
        finally:
            reader.close()
        source = Image.fromarray(frame).convert("RGB")
        before_path = previews_dir / "source_frame.png"
        _save_image_with_provenance(
            root,
            source,
            before_path,
            operation="preview_video_frame",
            source={"sourceVideo": video_rel, "atSeconds": float(at_seconds), "videoFrameIndex": index},
            image_format="PNG",
        )
        before_rel = before_path.relative_to(root).as_posix()
    else:
        source = _complex_test_card()
        before_path = previews_dir / "testcard.png"
        _save_image_with_provenance(root, source, before_path, operation="generate_filter_test_card", image_format="PNG")
        before_rel = before_path.relative_to(root).as_posix()
    filtered = transform(source).convert("RGB")
    after_path = previews_dir / f"preview_{_slug(label)[:60]}.png"
    provenance = _save_image_with_provenance(
        root,
        filtered,
        after_path,
        operation="preview_filter_chain",
        parent_image=before_path,
        source={"filter": label},
        transform={"filter": label},
        image_format="PNG",
    )
    return {
        "filter": label,
        "before": before_rel,
        "after": after_path.relative_to(root).as_posix(),
        "provenance": provenance["provenance"],
    }


_BUILTIN_PARAM_GRIDS: dict[str, dict[str, list[Any]]] = {
    "cartoon": {"colors": [4, 8, 16, 32], "scale": [2, 4, 8]},
    "pixelate": {"scale": [4, 8, 12, 20]},
    "downscale": {"scale": [2, 4, 8, 16]},
}


def _param_permutations(entry: dict[str, Any], cap: int = 64) -> list[dict[str, Any]]:
    """Concrete parameter permutations for one filter entry.

    Candidate values per param come from, in order: an explicit ``paramGrid``
    (entry field, fed from a skill's SKILL dict), the built-in grids, a
    ``paramChoices`` list, then a numeric half/default/double fallback."""
    import itertools  # noqa: PLC0415

    params = entry.get("params") if isinstance(entry.get("params"), dict) else {}
    grid_field = entry.get("paramGrid") if isinstance(entry.get("paramGrid"), dict) else {}
    choices = entry.get("paramChoices") if isinstance(entry.get("paramChoices"), dict) else {}
    builtin_grid = _BUILTIN_PARAM_GRIDS.get(str(entry.get("filter") or "")) if entry.get("builtin") or str(entry.get("filter") or "") in _BUILTIN_PARAM_GRIDS else {}
    grid: dict[str, list[Any]] = {}
    keys = list(dict.fromkeys([*params.keys(), *grid_field.keys(), *(builtin_grid or {}).keys(), *choices.keys()]))
    for key in keys:
        if isinstance(grid_field.get(key), list) and grid_field[key]:
            grid[key] = list(grid_field[key])
        elif builtin_grid and isinstance(builtin_grid.get(key), list):
            grid[key] = list(builtin_grid[key])
        elif isinstance(choices.get(key), list) and choices[key]:
            grid[key] = list(choices[key])
        else:
            default = params.get(key)
            try:
                number = float(default)
            except (TypeError, ValueError):
                continue
            halved = number / 2 if number / 2 >= 1 else number / 2
            doubled = number * 2
            candidates = []
            for value in (halved, number, doubled):
                rounded = int(round(value)) if float(value).is_integer() or isinstance(default, int) else round(value, 2)
                if rounded not in candidates:
                    candidates.append(rounded)
            grid[key] = candidates
    if not grid:
        return []
    ordered_keys = sorted(grid)
    permutations: list[dict[str, Any]] = []
    for combo in itertools.product(*[grid[key] for key in ordered_keys]):
        permutations.append(dict(zip(ordered_keys, combo)))
        if len(permutations) >= cap:
            break
    return permutations


@router.post("/filter-gallery")
def filter_gallery(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Render one thumbnail per registered filter (built-ins, published
    presets, LUTs, skills and their expanded settings) from the chosen
    preview image — the browsable "what would every filter do" grid.

    Runs as a job (poll /extract/status); the finished job carries a
    ``gallery`` list of {id, title, path|error} entries."""
    workspace_id = str(body.get("workspaceId") or "")
    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspaceId is required")
    root = _workspace_root(workspace_id)
    from PIL import Image  # noqa: PLC0415

    # The same source preference as /filter-preview.
    image_rel = str(body.get("image") or "")
    video_rel = str(body.get("video") or "")
    at_seconds = body.get("atSeconds")
    if image_rel:
        source_path = _safe_workspace_child(root, image_rel)
        if not source_path.is_file():
            raise HTTPException(status_code=404, detail=f"preview image not found: {image_rel}")
        with Image.open(source_path) as loaded:
            base = loaded.convert("RGB")
        base_parent_path = source_path
    elif video_rel and at_seconds is not None:
        import imageio  # noqa: PLC0415

        _, video_path = _resolve_video(workspace_id, video_rel)
        reader = imageio.get_reader(str(video_path))
        try:
            fps = float(reader.get_meta_data().get("fps") or 24.0)
            index = max(0, int(float(at_seconds) * fps))
            try:
                frame = reader.get_data(index)
            except (IndexError, ValueError) as error:
                raise HTTPException(status_code=400, detail=f"no frame at {at_seconds}s: {error}") from error
        finally:
            reader.close()
        base = Image.fromarray(frame).convert("RGB")
        base_source = {"sourceVideo": video_rel, "atSeconds": float(at_seconds), "videoFrameIndex": index}
    else:
        base = _complex_test_card()
        base_source = {"generated": "complex_test_card"}
    # Thumbnail size keeps 100+ transforms quick.
    base_input_size = base.size
    base.thumbnail((320, 320))
    # scope: "included" (active set, default), "excluded" (flagged/disabled
    # only), or "all" — the operator can always still run anything.
    scope = str(body.get("scope") or "included")
    filter_id = str(body.get("filterId") or "")
    all_entries = [entry for entry in list_filters(workspace_id)["filters"] if not entry.get("broken")]
    if filter_id:
        # Permutation mode: one tile per parameter permutation of ONE filter.
        base_entry = next((entry for entry in all_entries if entry.get("id") == filter_id), None)
        if base_entry is None:
            raise HTTPException(status_code=404, detail=f"unknown filter: {filter_id}")
        permutations = _param_permutations(base_entry)
        if not permutations:
            raise HTTPException(status_code=400, detail=f"filter '{filter_id}' has no parameters to permute")
        entries = [
            {
                **base_entry,
                "id": f"{filter_id}#p{index}",
                "baseId": filter_id,
                "title": " · ".join([str(base_entry.get("title") or filter_id).split(" (")[0],
                                     *[f"{key}={value}" for key, value in permutation.items()]]),
                "params": {**(base_entry.get("params") or {}), **permutation},
            }
            for index, permutation in enumerate(permutations)
        ]
    elif scope == "excluded":
        entries = [entry for entry in all_entries if entry.get("excluded")]
    elif scope == "all":
        entries = all_entries
    else:
        entries = [entry for entry in all_entries if not entry.get("excluded")]
    if not entries:
        raise HTTPException(status_code=400, detail=f"no filters in scope '{scope}'")
    gallery_dir = _imports_root(root) / "previews" / "gallery"
    if gallery_dir.is_dir():
        shutil.rmtree(gallery_dir, ignore_errors=True)
    gallery_dir.mkdir(parents=True, exist_ok=True)
    gallery_base_path = gallery_dir / "source.png"
    _save_image_with_provenance(
        root,
        base,
        gallery_base_path,
        operation="prepare_filter_gallery_source",
        parent_image=base_parent_path,
        source=base_source,
        transform={
            "sourceDimensions": {"width": base_input_size[0], "height": base_input_size[1]},
            "thumbnailBounds": {"width": 320, "height": 320},
        },
        image_format="PNG",
    )
    job_id = uuid.uuid4().hex[:12]
    job: dict[str, Any] = {
        "id": job_id, "state": "running", "done": 0, "total": len(entries),
        "elapsedSeconds": 0.0, "etaSeconds": round(len(entries) * 0.2, 1),
        "gallery": [], "error": None,
    }
    _extract_jobs[job_id] = job

    def work() -> None:
        started = time.monotonic()
        results: list[dict[str, Any]] = []
        try:
            for entry in entries:
                if job.get("cancel"):
                    break
                spec = {
                    "filter": entry.get("filter"),
                    "params": entry.get("params") or {},
                    "lutPath": entry.get("lutPath"),
                    "skillPath": entry.get("skillPath"),
                    "colors": (entry.get("params") or {}).get("colors"),
                    "scale": (entry.get("params") or {}).get("scale"),
                }
                record: dict[str, Any] = {"id": entry["id"], "title": entry["title"]}
                if entry.get("baseId"):
                    record["baseId"] = entry["baseId"]
                    record["params"] = entry.get("params") or {}
                try:
                    _, transform = _resolve_transform(root, spec)
                    rendered = transform(base.copy()).convert("RGB")
                    name = f"{_slug(str(entry['id']))[:70]}.png"
                    target = gallery_dir / name
                    provenance = _save_image_with_provenance(
                        root,
                        rendered,
                        target,
                        operation="render_filter_gallery_item",
                        parent_image=gallery_base_path,
                        source={"filterId": entry["id"], "filterTitle": entry["title"]},
                        transform={"filter": spec},
                        image_format="PNG",
                    )
                    record["path"] = target.relative_to(root).as_posix()
                    record["provenance"] = provenance["provenance"]
                except Exception as error:  # noqa: BLE001 - one bad filter must not sink the grid
                    record["error"] = str(error)
                results.append(record)
                elapsed = time.monotonic() - started
                job["done"] = len(results)
                job["elapsedSeconds"] = round(elapsed, 1)
                job["etaSeconds"] = round(max(0.0, (len(entries) - len(results)) * (elapsed / max(1, len(results)))), 1)
            job.update({"state": "done", "gallery": results, "etaSeconds": 0.0, "interrupted": bool(job.get("cancel"))})
        except Exception as error:  # noqa: BLE001 - surfaced via the job record
            job.update({"state": "error", "error": str(error)})

    threading.Thread(target=work, name=f"filter-gallery-{job_id}", daemon=True).start()
    return {"jobId": job_id, "count": len(entries)}


@router.post("/select-group")
def select_group(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Group selectors over a set of images.

    selector="unique": the N most mutually distinct images (greedy
    farthest-point sampling over downsampled grayscale features).
    selector="like-original" / "unlike-original": rank prepass outputs by
    distance to their originals (``pairs`` of {image, original}) and return
    the N originals whose outputs changed least / most."""
    workspace_id = str(body.get("workspaceId") or "")
    selector = str(body.get("selector") or "unique")
    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspaceId is required")
    root = _workspace_root(workspace_id)
    try:
        import numpy as np  # noqa: PLC0415
        from PIL import Image  # noqa: PLC0415
    except ImportError as error:
        raise HTTPException(status_code=500, detail="numpy/PIL are not installed in the server environment") from error

    def feature(image_rel: str) -> "Any":
        image_path = _safe_workspace_child(root, str(image_rel))
        if not image_path.is_file():
            raise HTTPException(status_code=404, detail=f"image not found: {image_rel}")
        with Image.open(image_path) as loaded:
            return np.asarray(loaded.convert("L").resize((32, 32)), dtype=np.float64).ravel() / 255.0

    if selector in {"like-original", "unlike-original"}:
        pairs = body.get("pairs")
        if not isinstance(pairs, list) or not pairs:
            raise HTTPException(status_code=400, detail="pairs of {image, original} are required for this selector")
        count = max(1, min(len(pairs), int(body.get("count") or 6)))
        scored: list[tuple[float, str]] = []
        for pair in pairs:
            if not isinstance(pair, dict):
                continue
            image_rel = str(pair.get("image") or "")
            original_rel = str(pair.get("original") or "")
            if not image_rel or not original_rel:
                continue
            distance = float(np.abs(feature(image_rel) - feature(original_rel)).mean())
            scored.append((distance, original_rel))
        if not scored:
            raise HTTPException(status_code=400, detail="no valid pairs supplied")
        scored.sort(key=lambda item: item[0], reverse=(selector == "unlike-original"))
        picked = scored[:count]
        return {
            "selected": [original for _, original in picked],
            "distances": {original: round(distance, 4) for distance, original in picked},
            "selector": selector,
            "count": count,
        }

    images = body.get("images")
    if not isinstance(images, list) or len(images) < 2:
        raise HTTPException(status_code=400, detail="at least 2 images are required")
    count = max(1, min(len(images), int(body.get("count") or 6)))
    if selector != "unique":
        raise HTTPException(status_code=400, detail=f"unknown group selector: {selector}")
    features: list["Any"] = [feature(str(image_rel)) for image_rel in images]
    matrix = np.stack(features)
    # Pairwise squared distances via the norms identity (no giant broadcast).
    norms = (matrix * matrix).sum(axis=1)
    distances = np.maximum(0.0, norms[:, None] + norms[None, :] - 2.0 * (matrix @ matrix.T))
    # Seed with the image farthest from the mean, then greedily add whichever
    # image is farthest from everything already chosen (max-min).
    start = int(np.argmax(((matrix - matrix.mean(axis=0)) ** 2).sum(axis=1)))
    chosen = [start]
    while len(chosen) < count:
        min_distance = distances[:, chosen].min(axis=1)
        min_distance[chosen] = -1.0
        chosen.append(int(np.argmax(min_distance)))
    selected = [str(images[index]) for index in sorted(chosen)]
    return {"selected": selected, "selector": selector, "count": count}


@router.post("/materialize")
def materialize_recording(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Lay the annotated frames out as an ARC3-style playable recording.

    Every frame after the first becomes one move whose action encodes the
    character diff against the previous frame: names added, names removed,
    the resulting cast, and the head count (named + unnamed).
    """
    workspace_id = str(body.get("workspaceId") or "")
    game_id = str(body.get("gameId") or "").strip()
    frames = body.get("frames")
    if not workspace_id or not game_id:
        raise HTTPException(status_code=400, detail="workspaceId and gameId are required")
    if not isinstance(frames, list) or len(frames) < 1:
        raise HTTPException(status_code=400, detail="frames must be a non-empty list")
    root = _workspace_root(workspace_id)
    game_dir = _game_slug(game_id)
    container = _game_write_dir(root, game_dir)
    saved_name = _next_ranked_saved_dir_name(container)
    level_dir = container / saved_name
    level_dir.mkdir(parents=True, exist_ok=True)

    def cast_of(frame: dict[str, Any]) -> tuple[list[str], int]:
        names = [str(name).strip() for name in (frame.get("characters") or []) if str(name).strip()]
        anonymous = max(0, int(frame.get("anonymous") or 0))
        return names, len(names) + anonymous

    def write_frame(directory: Path, frame: dict[str, Any], *, incoming: str | None,
                    action_data: dict[str, Any], ordinal: int | None) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        source_rel = str(frame.get("path") or "")
        source = _safe_workspace_child(root, source_rel)
        if not source.is_file():
            raise HTTPException(status_code=400, detail=f"frame image not found: {source_rel}")
        shutil.copyfile(source, directory / "image.png")
        png = (directory / "image.png").read_bytes()
        names, count = cast_of(frame)
        payload = {
            "kind": "video_import_frame",
            "game_id": game_id,
            "game_directory": game_dir,
            "state": "NOT_FINISHED",
            "level": "1",
            "image_hash": hashlib.sha256(png).hexdigest()[:16],
            "incoming_action": incoming,
            "action_directory": str(ordinal) if ordinal is not None else None,
            "action_data": action_data,
            "parent_node": ".." if ordinal is not None else None,
            "action_path": [str(index) for index in range(ordinal + 1)] if ordinal is not None else [],
            "characters": names,
            "character_count": count,
            "source_frame": source_rel,
            "at_seconds": frame.get("atSeconds"),
            "recorded_at": _utc_now(),
        }
        (directory / "state.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    first = frames[0]
    first_names, first_count = cast_of(first)
    write_frame(level_dir, first, incoming=None, ordinal=None, action_data={
        "characters": first_names, "count": first_count,
        "added": first_names, "removed": [],
    })
    moves: list[dict[str, Any]] = []
    previous_names, previous_count = first_names, first_count
    for ordinal, frame in enumerate(frames[1:]):
        names, count = cast_of(frame)
        added = [name for name in names if name not in previous_names]
        removed = [name for name in previous_names if name not in names]
        delta = count - previous_count
        action = "ADD_CHARACTER" if delta > 0 else "REMOVE_CHARACTER" if delta < 0 else "FRAME"
        action_data = {
            "characters": names,
            "count": count,
            "delta": delta,
            "added": added,
            "removed": removed,
        }
        write_frame(level_dir / str(ordinal), frame, incoming=action, ordinal=ordinal, action_data=action_data)
        moves.append({
            "index": ordinal,
            "action": action,
            "data": action_data,
            "directory": (level_dir / str(ordinal)).relative_to(root).as_posix(),
            "state": "NOT_FINISHED",
            "level": "1",
            "recorded_at": _utc_now(),
        })
        previous_names, previous_count = names, count
    manifest = {
        "kind": "arc3_play_recording",
        "source": "video_import",
        "session_id": None,
        "game_id": game_id,
        "game_directory": game_dir,
        "level": "1",
        "level_directory": level_dir.relative_to(root).as_posix(),
        "started_at": _utc_now(),
        "updated_at": _utc_now(),
        "last_event": "video_import",
        "moves": moves,
    }
    (level_dir / "recording.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return {
        "levelDir": level_dir.relative_to(root).as_posix(),
        "gameDirectory": game_dir,
        "moveCount": len(moves),
    }
