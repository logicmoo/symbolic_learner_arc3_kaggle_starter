from __future__ import annotations

import argparse

from _runtime import configure_runtime_home

PROJECT_ROOT = configure_runtime_home(__file__)

from arc3_runner import Arc3Runner
from object_memory import standard_semantic_grid_observer
from swipl_bridge import SWIPrologBridge


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ARC3 through the SWI-Prolog controller")
    parser.add_argument("game_id", nargs="?", default="ls20")
    parser.add_argument("--no-semantic-capture", action="store_true")
    args = parser.parse_args()
    observers = () if args.no_semantic_capture else (standard_semantic_grid_observer(),)
    runner = Arc3Runner(
        args.game_id,
        render_mode="terminal",
        capture_observers=observers,
    )
    prolog = SWIPrologBridge(PROJECT_ROOT / "prolog" / "arc3_agent.pl")

    for _ in range(10):
        decision = prolog.choose_action(runner.summary_for_prolog())
        action = decision["action"]
        data = decision.get("data") or {}
        print("Prolog chose:", decision)
        runner.step(action, data=data)

        if runner.is_win() or runner.is_game_over():
            break


if __name__ == "__main__":
    main()
