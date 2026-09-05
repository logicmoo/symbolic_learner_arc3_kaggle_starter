"""scene_split.py -- deterministic, LLM-free video -> scenes -> images front-end
for the symbolic recognizer (Phase 2 input breadth, gap #5).

Pipeline order: a video is decoded to frames (ffmpeg), the frames are segmented
into SCENES at shot cuts (large frame-to-frame change), and each scene yields a
representative keyframe IMAGE. Those images then feed symbolic_arc.decode_grid /
extract_sequence. Everything here is deterministic (thumbnail difference), no LLM.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

_VIDEO_SUFFIXES = {".mp4", ".webm", ".mkv", ".mov", ".avi", ".m4v"}
_THUMB = 32              # thumbnail edge (px) used for frame comparison
_DEFAULT_CUT = 28.0      # mean abs grayscale diff (0..255) that marks a shot cut
# (grid-game moves are ~0..22; real scene changes are ~40+, so 28 avoids false
# cuts on continuous grids/animation while still catching genuine shot cuts.)


def _thumb(path: str) -> np.ndarray:
    """Small grayscale thumbnail of a frame for cheap, scale-robust comparison."""
    with Image.open(path) as im:
        g = im.convert("L").resize((_THUMB, _THUMB), Image.BOX)
        return np.asarray(g, dtype=np.float32)


def frame_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Mean absolute grayscale difference between two frame thumbnails (0..255)."""
    return float(np.abs(a - b).mean())


def scene_cuts(frame_paths: list[str], threshold: float | None = _DEFAULT_CUT) -> list[int]:
    """Indices i where frame i begins a new scene (a shot cut between i-1 and i).
    threshold=None uses an adaptive cut = mean + 2*std of the frame distances."""
    if len(frame_paths) < 2:
        return []
    thumbs = [_thumb(p) for p in frame_paths]
    dists = [frame_distance(thumbs[i - 1], thumbs[i]) for i in range(1, len(thumbs))]
    if threshold is None:
        arr = np.asarray(dists)
        threshold = float(arr.mean() + 2.0 * arr.std()) if arr.size else _DEFAULT_CUT
    return [i for i, d in enumerate(dists, start=1) if d >= threshold]


def split_scenes(frame_paths: list[str], threshold: float | None = _DEFAULT_CUT) -> list[dict]:
    """Group an ordered list of frames into scenes at the detected cuts. Each scene
    is {index, start, end, frames, keyframe} where keyframe is the middle frame --
    the representative IMAGE for that scene."""
    n = len(frame_paths)
    if n == 0:
        return []
    cuts = set(scene_cuts(frame_paths, threshold))
    scenes: list[dict] = []
    start = 0
    for i in range(1, n + 1):
        if i == n or i in cuts:
            frames = list(frame_paths[start:i])
            mid = start + (i - 1 - start) // 2
            scenes.append({"index": len(scenes), "start": start, "end": i - 1,
                           "frames": frames, "keyframe": frame_paths[mid]})
            start = i
    return scenes


def keyframes(frame_paths: list[str], threshold: float | None = _DEFAULT_CUT) -> list[str]:
    """One representative image per scene -- the 'scene -> images' output."""
    return [s["keyframe"] for s in split_scenes(frame_paths, threshold)]


def _ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg  # noqa: PLC0415
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError as e:  # pragma: no cover - environment dependent
        raise RuntimeError("ffmpeg is unavailable") from e


def video_to_frames(video_path: str, out_dir: str, fps: float = 2.0) -> list[str]:
    """Decode a video to frames at `fps` using ffmpeg (best effort). Returns the
    ordered list of extracted frame paths. This is the 'video -> ...' entry; the
    frames then go through split_scenes / keyframes."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    pattern = str(out / "frame_%06d.png")
    subprocess.run([_ffmpeg(), "-y", "-i", str(video_path), "-vf", f"fps={fps}", pattern],
                   check=True, capture_output=True)
    return sorted(str(p) for p in out.glob("frame_*.png"))


def video_to_scene_images(video_path: str, out_dir: str, fps: float = 2.0,
                          threshold: float | None = _DEFAULT_CUT) -> list[str]:
    """Full front-end: video -> frames -> scenes -> one keyframe image per scene."""
    return keyframes(video_to_frames(video_path, out_dir, fps), threshold)
