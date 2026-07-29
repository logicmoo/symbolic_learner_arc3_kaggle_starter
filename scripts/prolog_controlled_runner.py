from __future__ import annotations

from _runtime import configure_runtime_home

PROJECT_ROOT = configure_runtime_home(__file__)

from arc3_runner import Arc3Runner
from swipl_bridge import SWIPrologBridge


def main() -> None:
    runner = Arc3Runner("ls20", render_mode="terminal")
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
