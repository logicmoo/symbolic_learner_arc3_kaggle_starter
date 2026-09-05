from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from _runtime import configure_runtime_home
except ModuleNotFoundError:
    from scripts._runtime import configure_runtime_home

configure_runtime_home(__file__)

from omega_vision import (
    PerceptionBenchmarkRunner,
    PythonProvider,
    SpriteAdapter,
    environment_progression_fixtures,
)


def run_demo(output_root: Path) -> dict[str, Any]:
    fixtures = environment_progression_fixtures()
    results = PerceptionBenchmarkRunner(SpriteAdapter(PythonProvider({}))).run(
        fixtures.all()
    )
    environments = {
        "rendered_arcade": len(fixtures.rendered_arcade),
        "fixed_camera_physics": len(fixtures.fixed_camera),
        "top_down_manipulation": len(fixtures.top_down_manipulation),
    }
    summary = {
        "environments": environments,
        "fixtures": len(results),
        "perfect_count_scores": sum(item.count_score == 1.0 for item in results),
        "accepted": bool(results) and all(item.count_score == 1.0 for item in results),
        "results": [
            {
                "fixture_id": item.fixture_id,
                "degradation": item.degradation,
                "expected_count": item.expected_count,
                "detected_count": item.detected_count,
                "count_score": item.count_score,
            }
            for item in results
        ],
    }
    output_root = output_root.expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    summary_path = output_root / "environment_progression_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    summary["summary"] = str(summary_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run deterministic Phase 2 environment progression fixtures."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("runtime") / "phase2_environment_progression",
    )
    args = parser.parse_args()
    print(json.dumps(run_demo(args.output), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
