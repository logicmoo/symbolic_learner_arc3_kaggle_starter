"""Continuously learn by playing randomly selected ARC3 games."""

from __future__ import annotations

import argparse
import json
import sys

from _runtime import configure_runtime_home

ROOT = configure_runtime_home(__file__)
sys.path.insert(0, str(ROOT / "python"))

from arc3_random_player import RandomArc3Player


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds-per-game", type=float, default=600.0)
    parser.add_argument("--max-games", type=int, default=None)
    parser.add_argument("--max-steps-per-game", type=int, default=None)
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    workspace = ROOT / "workbench" / "workspaces" / "arc3_random_player"
    player = RandomArc3Player(
        workspace,
        seconds_per_game=args.seconds_per_game,
        seed=args.seed,
    )
    for summary in player.run(
        max_games=args.max_games,
        max_steps_per_game=args.max_steps_per_game,
    ):
        print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
