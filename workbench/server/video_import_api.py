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

import hashlib
import json
import re
import shutil
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Iterator

from fastapi import APIRouter, Body, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import Response, StreamingResponse

from arc3_play_api import (
    _game_slug,
    _game_write_dir,
    _next_ranked_saved_dir_name,
    _safe_workspace_child,
    _utc_now,
    _workspace_root,
)

router = APIRouter(prefix="/video-import", tags=["video-import"])

_VIDEO_SUFFIXES = {".mp4", ".webm", ".mkv", ".mov", ".avi", ".m4v"}

# Running/finished frame-extraction jobs, polled for the progress bar.
_extract_jobs: dict[str, dict[str, Any]] = {}


def _imports_root(root: Path) -> Path:
    return root / "data" / "VideoImports"


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", value).strip("-").lower()
    return cleaned or uuid.uuid4().hex[:8]


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
    """Loose video files dropped by hand into data/VideoImports/importables/.

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
    path = _imports_root(_workspace_root(workspaceId)) / "page_state.json"
    if not path.is_file():
        return {"state": None}
    try:
        return {"state": json.loads(path.read_text(encoding="utf-8"))}
    except (OSError, json.JSONDecodeError):
        return {"state": None}


@router.post("/page-state")
def save_page_state(payload: dict[str, Any]) -> dict[str, Any]:
    """Persist the page's exact-state JSON into data/VideoImports/page_state.json."""
    workspace_id = str(payload.get("workspaceId") or "")
    state = payload.get("state")
    if not workspace_id or not isinstance(state, dict):
        raise HTTPException(status_code=400, detail="workspaceId and a state object are required")
    container = _imports_root(_workspace_root(workspace_id))
    container.mkdir(parents=True, exist_ok=True)
    path = container / "page_state.json"
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return {"saved": True, "path": str(path)}


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
                frames_dir = directory / "frames"
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
    """Download one video URL into data/VideoImports/<slug>/.

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
        raise HTTPException(status_code=500, detail="download completed but produced no video file")
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

    The file is copied into data/VideoImports/<slug>/ so every imported video
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
    (data/VideoImports/importables/<slug>/video.<ext>) so hand-sent files are
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


@router.post("/extract")
def extract_frames(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Start extracting frames (one PNG every N seconds, optionally within a
    start/end window chosen on the timeline). Returns a job id plus a frame
    and time estimate; poll /extract/status for the progress bar."""
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
    scene_targets: list[float] = []
    if mode == "scenes":
        markers = [float(marker.get("atSeconds") or 0) for marker in (meta.get("scenes") or []) if isinstance(marker, dict)]
        if not markers:
            raise HTTPException(status_code=400, detail="no scene markers saved yet — run Detect scenes first")
        boundaries = [start_seconds, *[marker for marker in sorted(markers) if marker > start_seconds]]
        if window_end is not None:
            boundaries = [boundary for boundary in boundaries if boundary < window_end]
            boundaries.append(window_end)
        elif duration:
            boundaries.append(float(duration))
        for scene_index in range(len(boundaries) - 1):
            scene_start, scene_end = boundaries[scene_index], boundaries[scene_index + 1]
            length = max(0.0, scene_end - scene_start - scene_offset)
            spacing = length / per_scene if per_scene > 1 else 0.0
            for shot in range(per_scene):
                at = scene_start + scene_offset + shot * spacing
                if at < scene_end:
                    scene_targets.append(round(at, 3))
        scene_targets = sorted(set(scene_targets))[:max_frames]
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
        frames_dir = video_path.parent / "frames"
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
                    if mode == "scenes":
                        # Grab the first frame at or past each scene target.
                        if target_cursor >= len(scene_targets):
                            break
                        if at < scene_targets[target_cursor]:
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
                    Image.fromarray(frame).save(frames_dir / name)
                    frames.append({
                        "path": (frames_dir / name).relative_to(root).as_posix(),
                        "index": ordinal,
                        "atSeconds": round(at, 2),
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
            meta["lastExtract"] = {
                "count": len(frames),
                "elapsedSeconds": round(elapsed, 1),
                "secondsPerFrame": round(elapsed / len(frames), 3) if frames else None,
                "at": _utc_now(),
            }
            if duration and not meta.get("duration"):
                meta["duration"] = duration
            try:
                meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
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
    frames_dir = video_path.parent / "frames"
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
        Image.fromarray(frame).save(frames_dir / name)
    finally:
        reader.close()
    return {
        "path": (frames_dir / name).relative_to(root).as_posix(),
        "atSeconds": round(at_seconds, 2),
        "index": index,
    }


@router.post("/member-cut")
def member_cut(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Cut one identified member out of a scene as a TRANSPARENT GIF: the
    member's polygon keeps its pixels, everything else is transparent. The
    member is then erased from the scene (border-median fill) so the
    extraction loop can continue on the reduced scene."""
    workspace_id = str(body.get("workspaceId") or "")
    image_rel = str(body.get("image") or "")
    name = str(body.get("name") or "member")
    step = max(1, int(body.get("step") or 1))
    polygon_raw = body.get("polygon")
    box_raw = body.get("box")
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
        from PIL import Image, ImageDraw, ImageFilter  # noqa: PLC0415
    except ImportError as error:
        raise HTTPException(status_code=500, detail="numpy/PIL are not installed in the server environment") from error
    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    # Accept a polygon outline; a box is tolerated and becomes a rectangle.
    points: list[tuple[int, int]] = []
    if isinstance(polygon_raw, list) and len(polygon_raw) >= 3:
        for point in polygon_raw:
            if isinstance(point, (list, tuple)) and len(point) == 2:
                x = max(0, min(width - 1, int(round(float(point[0])))))
                y = max(0, min(height - 1, int(round(float(point[1])))))
                points.append((x, y))
    elif isinstance(box_raw, list) and len(box_raw) == 4:
        bx0, by0, bx1, by1 = (int(round(float(value))) for value in box_raw)
        bx0, bx1 = sorted((max(0, min(width - 1, bx0)), max(1, min(width, bx1))))
        by0, by1 = sorted((max(0, min(height - 1, by0)), max(1, min(height, by1))))
        points = [(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)]
    if len(points) < 3:
        raise HTTPException(status_code=400, detail="polygon (>= 3 [x, y] points) or box is required")
    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).polygon(points, fill=255)
    bbox = mask.getbbox()
    if not bbox or (bbox[2] - bbox[0]) < 2 or (bbox[3] - bbox[1]) < 2:
        raise HTTPException(status_code=400, detail=f"polygon too small after clamping to {width}x{height}")
    x0, y0, x1, y1 = bbox
    members_dir = image_path.parent / f"{image_path.stem}_members"
    members_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug(name)[:24] or f"member{step}"
    # The cutout: member pixels opaque, the rest transparent, saved as GIF.
    rgba = image.convert("RGBA")
    rgba.putalpha(mask)
    cut = rgba.crop(bbox)
    cutout_path = members_dir / f"cut_{step:02d}_{slug}.gif"
    palette_image = cut.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=255)
    transparent_where = cut.getchannel("A").point(lambda alpha: 255 if alpha <= 128 else 0)
    palette_image.paste(255, mask=transparent_where)
    palette_image.save(cutout_path, "GIF", transparency=255)
    # Erase the member from the scene. `fill` picks the removal method:
    # median inpaint (default), blur fill, or a transparent hole.
    fill_mode = str(body.get("fill") or "median")
    array = np.array(image)
    mask_array = np.array(mask) > 0
    if fill_mode == "hole":
        rgba_scene = image.convert("RGBA")
        alpha_channel = np.full((height, width), 255, dtype=np.uint8)
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
    scene_image.save(scene_path)
    return {
        "cutout": cutout_path.relative_to(root).as_posix(),
        "scene": scene_path.relative_to(root).as_posix(),
        "box": [x0, y0, x1, y1],
        "name": name,
        "fill": fill_mode,
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
    scene.save(returned_path)
    return {"scene": returned_path.relative_to(root).as_posix()}


def _video_meta(video_path: Path) -> tuple[Path, dict[str, Any]]:
    meta_path = video_path.parent / "video.json"
    meta: dict[str, Any] = {}
    if meta_path.is_file():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            meta = {}
    return meta_path, meta


def _resolve_video(workspace_id: str, video_rel: str) -> tuple[Path, Path]:
    root = _workspace_root(workspace_id)
    try:
        video_path = _safe_workspace_child(root, video_rel)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not video_path.is_file():
        raise HTTPException(status_code=404, detail=f"video not found: {video_rel}")
    return root, video_path


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
    threshold = float(body.get("threshold") or 28.0)
    start_seconds = max(0.0, float(body.get("startSeconds") or 0.0))
    max_markers = max(1, min(400, int(body.get("maxMarkers") or 120)))
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
                sample_step = max(1, round(fps / 4.0))  # ~4 samples per second
                first_index = int(start_seconds * fps)
                previous: Any = None
                for index, frame in enumerate(reader):
                    if job.get("cancel"):
                        break
                    if index < first_index or index % sample_step:
                        continue
                    small = np.asarray(frame, dtype=np.int16)[::4, ::4]
                    if previous is not None and small.shape == previous.shape:
                        score = float(np.abs(small - previous).mean())
                        if score >= threshold:
                            markers.append({"atSeconds": round(index / fps, 2), "score": round(score, 1)})
                            if len(markers) >= max_markers:
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
            meta["scenes"] = merged
            meta["lastScenes"] = {
                "count": len(merged),
                "newThisRun": len(markers),
                "resumedFromSeconds": start_seconds,
                "elapsedSeconds": round(elapsed, 1),
                "secondsPerVideoSecond": round(elapsed / window, 4) if window else None,
                "threshold": threshold,
                "at": _utc_now(),
            }
            if duration and not meta.get("duration"):
                meta["duration"] = duration
            try:
                meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
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
    meta_path, meta = _video_meta(video_path)
    meta["scenes"] = cleaned
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
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
    meta_path, meta = _video_meta(video_path)
    meta["segments"] = cleaned
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
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
    .cube LUTs dropped into data/VideoImports/luts/ (e.g. from LUT sites)."""
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
                transform(image.convert("RGB")).save(target)
            results.append({"source": str(frame_rel), "path": target.relative_to(root).as_posix()})
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
    if image_rel:
        source_path = _safe_workspace_child(root, image_rel)
        if not source_path.is_file():
            raise HTTPException(status_code=404, detail=f"preview image not found: {image_rel}")
        with Image.open(source_path) as loaded:
            source = loaded.convert("RGB")
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
        source.save(before_path)
        before_rel = before_path.relative_to(root).as_posix()
    else:
        source = _complex_test_card()
        before_path = previews_dir / "testcard.png"
        source.save(before_path)
        before_rel = before_path.relative_to(root).as_posix()
    filtered = transform(source).convert("RGB")
    after_path = previews_dir / f"preview_{_slug(label)[:60]}.png"
    filtered.save(after_path)
    return {
        "filter": label,
        "before": before_rel,
        "after": after_path.relative_to(root).as_posix(),
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
    else:
        base = _complex_test_card()
    # Thumbnail size keeps 100+ transforms quick.
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
                    rendered.save(gallery_dir / name)
                    record["path"] = (gallery_dir / name).relative_to(root).as_posix()
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
