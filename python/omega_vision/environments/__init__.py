"""SoW Appendix A.2 ``environments/`` / §14 — the four-rung testbed ladder.

Each rung is a runnable, gradable system (SoW §14):

* ``arc_grids`` (rung 1) — clean discrete cells the engine reads directly.
* ``arcade_synthetic`` (rung 2) — rendered arcade; where raster begins.
* ``physics_fixed_cam`` (rung 3) — a bouncing ball / pendulum under camera noise.
* ``manipulation`` (rung 4) — top-down tabletop; the direct occlusion test.

The runnable fixtures live in :mod:`object_memory.environment_fixtures`; they are
re-exported here under the SoW rung names.
"""

from object_memory.environment_fixtures import (
    EnvironmentProgressionFixtures,
    environment_progression_fixtures,
    fixed_camera_physics_fixtures,
    rendered_arcade_fixtures,
    top_down_manipulation_fixtures,
)

# SoW §14 rung -> fixture provider
arcade_synthetic_fixtures = rendered_arcade_fixtures       # rung 2
physics_fixed_cam_fixtures = fixed_camera_physics_fixtures  # rung 3
manipulation_fixtures = top_down_manipulation_fixtures      # rung 4

__all__ = [
    "EnvironmentProgressionFixtures",
    "environment_progression_fixtures",
    "rendered_arcade_fixtures",
    "fixed_camera_physics_fixtures",
    "top_down_manipulation_fixtures",
    "arcade_synthetic_fixtures",
    "physics_fixed_cam_fixtures",
    "manipulation_fixtures",
]
