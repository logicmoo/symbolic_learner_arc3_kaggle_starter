from __future__ import annotations

import random

from _runtime import configure_runtime_home

PROJECT_ROOT = configure_runtime_home(__file__)

import arc_agi
from arcengine import GameState


def main() -> None:
    arc = arc_agi.Arcade()
    env = arc.make("ls20", render_mode="human")
    if env is None:
        raise SystemExit("Failed to create environment")

    for step in range(100):
        action = random.choice(env.action_space)
        action_data = {}
        if action.is_complex():
            action_data = {
                "x": random.randint(0, 63),
                "y": random.randint(0, 63),
            }

        obs = env.step(action, data=action_data)
        if obs and obs.state == GameState.WIN:
            print(f"Game won at step {step}!")
            break
        if obs and obs.state == GameState.GAME_OVER:
            env.reset()

    scorecard = arc.get_scorecard()
    if scorecard:
        print(f"Final Score: {scorecard.score}")


if __name__ == "__main__":
    main()
