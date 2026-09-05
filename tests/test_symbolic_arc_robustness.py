"""Regression tests for the LLM-free noise/degradation recognition helpers added
to symbolic_arc: denoise_cells (keep the largest connected component) and
downscale_cells (majority-vote binning to recover a degraded, down-scaled shape).
"""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workbench" / "server" / "generative_vision" / "prolog"))

import symbolic_arc as sa  # noqa: E402


def test_denoise_keeps_largest_component_and_recovers_identity():
    base = [(0, 0), (0, 1), (0, 2), (1, 2)]          # L-tetromino
    noisy = base + [(4, 0), (5, 3), (3, 5)]          # scattered specks
    cleaned = list(sa.denoise_cells(noisy))
    assert set(cleaned) == set(sa._norm(base))
    assert sa._identity_name(cleaned) == sa._identity_name(base)
    # the noisy blob on its own is NOT the base identity
    assert sa._identity_name(list(sa._norm(noisy))) != sa._identity_name(base)


def test_downscale_recovers_degraded_shape():
    base = [(0, 0), (1, 0), (2, 0), (1, 1)]          # T-tetromino
    scaled = [(x * 3 + dx, y * 3 + dy) for (x, y) in base for dx in range(3) for dy in range(3)]
    degraded = [c for i, c in enumerate(sorted(scaled)) if i % 6 != 0]  # drop ~1/6 of cells
    recovered = list(sa.downscale_cells(degraded, 3))
    assert sa._identity_name(recovered) == sa._identity_name(base)


def test_denoise_and_downscale_handle_empty():
    assert sa.denoise_cells([]) == ()
    assert sa.downscale_cells([], 3) == ()
