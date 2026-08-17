from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _runtime import configure_runtime_home
except ModuleNotFoundError:
    from scripts._runtime import configure_runtime_home

configure_runtime_home(__file__)

from object_memory import build_acceptance_report, write_acceptance_report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify demo summaries and generate Phase 2 acceptance evidence."
    )
    parser.add_argument("--object-memory-summary", type=Path, required=True)
    parser.add_argument("--environment-summary", type=Path, required=True)
    parser.add_argument("--test-result", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    object_memory = json.loads(args.object_memory_summary.read_text(encoding="utf-8"))
    environment = json.loads(args.environment_summary.read_text(encoding="utf-8"))
    object_memory["summary"] = str(args.object_memory_summary.resolve())
    environment["summary"] = str(args.environment_summary.resolve())
    report = build_acceptance_report(
        object_memory=object_memory,
        environment_progression=environment,
        test_result=args.test_result,
        commit=args.commit,
    )
    paths = write_acceptance_report(report, args.output)
    print(report.to_json(), end="")
    print("reports=" + ",".join(str(path.resolve()) for path in paths))
    raise SystemExit(0 if report.accepted else 1)


if __name__ == "__main__":
    main()
