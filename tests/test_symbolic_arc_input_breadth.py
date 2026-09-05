"""Input-breadth tests for the symbolic_arc recognizer (Phase 2 gap #5): general
raster images / video frames are quantized + downscaled into the flat-colour grid
the recognizer expects, while genuine flat-colour grids decode unchanged."""
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

_SERVER = Path(__file__).resolve().parents[1] / "workbench" / "server" / "generative_vision" / "prolog"
sys.path.insert(0, str(_SERVER))

import symbolic_arc as sa  # noqa: E402


def _save(arr, path):
    Image.fromarray(arr.astype(np.uint8)).save(path)
    return str(path)


def test_flat_colour_grid_decodes_unchanged(tmp_path):
    """A clean ARC-style flat grid keeps its exact cells + palette (no quantize)."""
    g = np.zeros((80, 80, 3), np.uint8)
    pal = [(200, 0, 0), (0, 120, 255), (0, 0, 0)]
    for r in range(10):
        for c in range(10):
            g[r * 8:(r + 1) * 8, c * 8:(c + 1) * 8] = pal[(r + c) % 3]
    idx, hexpal, cols, rows = sa.decode_grid(_save(g, tmp_path / "grid.png"))
    assert (cols, rows) == (10, 10)
    assert len(hexpal) == 3


def test_raster_gradient_is_quantized_and_downscaled(tmp_path):
    """A smooth-gradient photo (thousands of colours) becomes a small flat grid."""
    y, x = np.mgrid[0:256, 0:256]
    gr = np.stack([x, y, (x + y) // 2], axis=-1)
    idx, hexpal, cols, rows = sa.decode_grid(_save(gr, tmp_path / "gradient.png"))
    assert max(cols, rows) <= 64      # downscaled
    assert 1 < len(hexpal) <= 16      # quantized to a small flat palette


def test_raster_frame_recognizes_a_region(tmp_path):
    """A noisy raster frame still yields extractable objects via extract_frame."""
    rng = np.random.default_rng(0)
    img = rng.integers(0, 40, (200, 200, 3)) + np.array([10, 10, 10])
    img[60:140, 60:140] = np.array([230, 40, 40]) + rng.integers(0, 20, (80, 80, 3))
    res = sa.extract_frame(_save(img, tmp_path / "frame.png"), "test")
    assert res["nparts"] >= 1         # the red block survives quantization as a part


def _frame_png(tmp_path, name, block_x):
    """A simple 'video' frame: a red block on a flat background at column block_x."""
    g = np.full((48, 96, 3), 12, np.uint8)
    g[16:32, block_x:block_x + 16] = (220, 30, 30)
    return _save(g, tmp_path / name)


def test_simple_video_extracts_and_tracks_object_across_frames(tmp_path):
    """A simple multi-frame video (a block moving right) is extracted per frame and
    the moving block keeps ONE stable object identity across the sequence rather
    than being re-minted each frame (Phase-2: extract from simple video inputs)."""
    frames = [_frame_png(tmp_path, f"v{i}.png", 8 + i * 16) for i in range(4)]
    mem = str(tmp_path / "mem")
    seq = sa.extract_sequence(frames, "clip", mem_dir=mem, write=True)
    assert len(seq) == 4
    assert all(fr["nparts"] >= 1 for fr in seq)          # object found in every frame
    # the moving block is one committed identity, not four
    block_color = sa._cname("#dc1e1e")                    # (220,30,30) -> its colour name
    ids = sa.registry_snapshot(mem)["scopes"].get("clip", {}).get("identities", [])
    block_ids = [o for o in ids if any(v["color"] == block_color for v in o.get("variations", []))]
    assert len(block_ids) == 1                            # tracked as ONE object
    assert block_ids[0]["seen"] == 1                      # one encounter (one clip)


def test_scene_split_segments_a_cut(tmp_path):
    """A simple video with a hard cut splits into two scenes (video breadth)."""
    a = [_frame_png(tmp_path, f"a{i}.png", 8 + i * 4) for i in range(3)]
    g = np.full((48, 96, 3), 200, np.uint8)              # very different frame = a cut
    b = [_save(g, tmp_path / f"b{i}.png") for i in range(3)]
    ss = __import__("scene_split")
    cuts = set(ss.scene_cuts(a + b))
    assert 3 in cuts                                       # boundary at the a->b cut

