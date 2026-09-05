"""SoW Appendix A.2 ``adapters/robot3d/`` — future adapter (stub only, §16).

A.8 task 9 names ``Robot3DAdapter``; A.6 names ``RGBDObjectProposer``. Both are
tabletop 3D robotics future work (SoW §16) — importable stubs only.
"""

from ..._future import future_component

Robot3DAdapter = future_component(
    "Robot3DAdapter", "§16", "tabletop 3D robotics adapter (RGB-D, SE(3) instances)"
)
RGBDObjectProposer = future_component(
    "RGBDObjectProposer", "§16", "RGB-D object candidate proposer for 3D robotics"
)

__all__ = ["Robot3DAdapter", "RGBDObjectProposer"]
