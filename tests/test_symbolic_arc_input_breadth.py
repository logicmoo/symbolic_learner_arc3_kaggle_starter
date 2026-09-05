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
