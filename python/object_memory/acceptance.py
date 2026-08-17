from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class AcceptanceReport:
    accepted: bool
    checks: Mapping[str, bool]
    evidence: Mapping[str, Any]

    def to_json(self) -> str:
        return json.dumps(
            {
                "accepted": self.accepted,
                "checks": self.checks,
                "evidence": self.evidence,
            },
            indent=2,
            sort_keys=True,
        ) + "\n"

    def to_markdown(self) -> str:
        lines = [
            "# Phase 2 Acceptance Report",
            "",
            f"Overall: **{'ACCEPTED' if self.accepted else 'NOT ACCEPTED'}**",
            "",
            "## Checks",
            "",
        ]
        lines.extend(
            f"- [{'x' if passed else ' '}] `{name}`"
            for name, passed in sorted(self.checks.items())
        )
        lines.extend(("", "## Evidence", ""))
        for name, value in sorted(self.evidence.items()):
            lines.append(f"- `{name}`: `{value}`")
        lines.extend(("", "[← Back to top-level README](../../../README.md)", ""))
        return "\n".join(lines)


def build_acceptance_report(
    *,
    object_memory: Mapping[str, Any],
    environment_progression: Mapping[str, Any],
    test_result: str,
    commit: str,
) -> AcceptanceReport:
    environments = environment_progression.get("environments") or {}
    checks = {
        "stable_identity": bool(object_memory.get("recognized_identity")),
        "exact_reconstruction": int(object_memory.get("exact_reconstructions", 0)) > 0,
        "deterministic_replay": bool(object_memory.get("replay_hash")),
        "prediction_or_change_evidence": bool(object_memory.get("object_changes")),
        "rendered_arcade": int(environments.get("rendered_arcade", 0)) > 0,
        "fixed_camera_physics": int(environments.get("fixed_camera_physics", 0)) > 0,
        "top_down_manipulation": int(environments.get("top_down_manipulation", 0)) > 0,
        "environment_benchmark": environment_progression.get("accepted") is True,
        "regression_tests": "passed" in test_result.lower(),
        "repository_commit": bool(commit.strip()),
    }
    evidence = {
        "commit": commit,
        "test_result": test_result,
        "object_memory_summary": object_memory.get("summary", "provided mapping"),
        "environment_summary": environment_progression.get(
            "summary", "provided mapping"
        ),
        "replay_hash": object_memory.get("replay_hash"),
        "recognized_identity": object_memory.get("recognized_identity"),
        "environment_fixtures": environment_progression.get("fixtures"),
    }
    return AcceptanceReport(all(checks.values()), checks, evidence)


def write_acceptance_report(report: AcceptanceReport, output_root: Path) -> tuple[Path, Path]:
    output_root.mkdir(parents=True, exist_ok=True)
    json_path = output_root / "phase2_acceptance_report.json"
    markdown_path = output_root / "PHASE2_ACCEPTANCE_REPORT.md"
    json_path.write_text(report.to_json(), encoding="utf-8")
    markdown_path.write_text(report.to_markdown(), encoding="utf-8")
    return json_path, markdown_path
