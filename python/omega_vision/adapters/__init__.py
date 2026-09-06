"""omega_vision.adapters - Perception adapters and candidate providers (SoW A.2 adapters/)."""

from .anime_sketch import AnimeRegionProposer
from .robot3d import RGBDObjectProposer, Robot3DAdapter

__all__ = ["AnimeRegionProposer", "RGBDObjectProposer", "Robot3DAdapter"]
