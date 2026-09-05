"""SoW Appendix A.2 ``adapters/`` — the domain seam (SoW §3.2, §6, A.6).

Adapters propose perceptual candidates and implement the domain-specific
``GenerativeForm``; the core imports no ARC/raster/domain assumption. The primary
adapters live in :mod:`object_memory`; the SoW registry candidate-provider names
(``GridIndividuator``, ``RasterSegmenter``) and the §16 future stubs are laid out
here.
"""

from object_memory.adapters import PerceptionAdapter

from .anime_sketch import AnimeRegionProposer
from .grid import GridAdapter, GridIndividuator
from .robot3d import RGBDObjectProposer, Robot3DAdapter
from .sprite import (
    AlphaContourProvider,
    ImageAdapter,
    RasterSegmenter,
    SimpleVideoAdapter,
    SpriteAdapter,
)

__all__ = [
    "PerceptionAdapter",
    "GridAdapter",
    "GridIndividuator",
    "SpriteAdapter",
    "ImageAdapter",
    "SimpleVideoAdapter",
    "AlphaContourProvider",
    "RasterSegmenter",
    "AnimeRegionProposer",
    "Robot3DAdapter",
    "RGBDObjectProposer",
]
