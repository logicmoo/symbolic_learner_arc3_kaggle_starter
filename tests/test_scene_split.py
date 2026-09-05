"""Scene-segmentation tests for the deterministic video -> scenes -> images
front-end (Phase 2 input breadth, gap #5)."""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

_SERVER = Path(__file__).resolve().parents[1] / "workbench" / "server" / "generative_vision" / "prolog"
sys.path.insert(0, str(_SERVER))

import scene_split as ss  # noqa: E402


def _frame(tmp, name, base, jitter, rng):
    img = np.clip(base + rng.integers(-jitter, jitter + 1, (48, 48, 3)), 0, 255)
    p = tmp / name
    Image.fromarray(img.astype(np.uint8)).save(p)
    return str(p)


def _make_two_scene_video(tmp):
    rng = np.random.default_rng(1)
    a = np.full((48, 48, 3), np.array([30, 30, 200]), dtype=int)   # scene A: blue
    b = np.full((48, 48, 3), np.array([220, 200, 20]), dtype=int)  # scene B: yellow
    frames = [_frame(tmp, f"f{i:02d}.png", a, 3, rng) for i in range(3)]
    frames += [_frame(tmp, f"f{i:02d}.png", b, 3, rng) for i in range(3, 6)]
    return frames


def test_scene_cut_detected_between_shots(tmp_path):
    frames = _make_two_scene_video(tmp_path)
    assert ss.scene_cuts(frames) == [3]           # cut where blue -> yellow


def test_split_into_two_scenes_with_keyframes(tmp_path):
    frames = _make_two_scene_video(tmp_path)
    scenes = ss.split_scenes(frames)
    assert len(scenes) == 2
    assert (scenes[0]["start"], scenes[0]["end"]) == (0, 2)
    assert (scenes[1]["start"], scenes[1]["end"]) == (3, 5)
    kf = ss.keyframes(frames)                      # one representative image per scene
    assert len(kf) == 2
    assert kf[0] in frames[0:3] and kf[1] in frames[3:6]


def test_single_scene_when_no_cut(tmp_path):
    rng = np.random.default_rng(2)
    base = np.full((48, 48, 3), np.array([100, 100, 100]), dtype=int)
    frames = [_frame(tmp_path, f"s{i:02d}.png", base, 3, rng) for i in range(5)]
    assert ss.scene_cuts(frames) == []
    assert len(ss.split_scenes(frames)) == 1
