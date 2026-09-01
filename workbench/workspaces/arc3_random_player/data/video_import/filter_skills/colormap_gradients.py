"""Colormap gradient-map skill: matplotlib's colormap registry applied as a
gradient map (grayscale luminance -> colormap RGB). Not a flat tint - every
pixel is remapped through the full gradient. The workbench calls this
directly - no LLM in the loop. params.cmap picks the colormap.
"""

import numpy as np
from PIL import Image

import matplotlib

# The full non-reversed registry (~85 maps: viridis, inferno, jet, ocean,
# terrain, twilight, tab20, ...). Reversed twins (*_r) are skipped to keep
# the list browsable.
_CMAPS = sorted(name for name in matplotlib.colormaps if not name.endswith("_r"))

SKILL = {
    "title": "Colormap gradient map",
    "description": "Applies one of matplotlib's ~85 colormaps as a gradient map over luminance (viridis, inferno, jet, ocean, terrain, twilight, ...).",
    "params": {"cmap": "viridis"},
    "paramChoices": {"cmap": _CMAPS},
}


def apply(image: Image.Image, params: dict) -> Image.Image:
    name = str(params.get("cmap") or "viridis")
    if name not in matplotlib.colormaps:
        raise ValueError(f"matplotlib has no colormap named '{name}'")
    colormap = matplotlib.colormaps[name]
    gray = np.asarray(image.convert("L"), dtype=np.float32) / 255.0
    mapped = colormap(gray)  # HxWx4 floats in 0..1
    return Image.fromarray((mapped[:, :, :3] * 255).astype(np.uint8), "RGB")
