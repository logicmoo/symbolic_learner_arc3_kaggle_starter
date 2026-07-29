from __future__ import annotations

from _runtime import configure_runtime_home

PROJECT_ROOT = configure_runtime_home(__file__)

import arc_agi
from arcengine import GameAction


def main() -> None:
    arc = arc_agi.Arcade()
    env = arc.make("ls20", render_mode="terminal")
    if env is None:
        raise SystemExit("Failed to create environment")

    print(env.action_space)
    env.step(GameAction.ACTION1)
    print(arc.get_scorecard())


if __name__ == "__main__":
    main()
