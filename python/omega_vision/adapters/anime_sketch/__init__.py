"""SoW Appendix A.2 ``adapters/anime_sketch/`` — future adapter (stub only, §16)."""

from ..._future import future_component

AnimeRegionProposer = future_component(
    "AnimeRegionProposer", "§16", "region proposer for anime-style 2D games"
)

__all__ = ["AnimeRegionProposer"]
