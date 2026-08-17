import json

from object_memory import build_acceptance_report, write_acceptance_report


def _summaries():
    return (
        {
            "recognized_identity": "known_shape",
            "exact_reconstructions": 4,
            "replay_hash": "sha256:replay",
            "object_changes": ["moved"],
            "summary": "runtime/object-summary.json",
        },
        {
            "accepted": True,
            "fixtures": 7,
            "environments": {
                "rendered_arcade": 1,
                "fixed_camera_physics": 3,
                "top_down_manipulation": 3,
            },
            "summary": "runtime/environment-summary.json",
        },
    )


def test_acceptance_report_requires_and_renders_all_evidence(tmp_path) -> None:
    object_memory, environment = _summaries()
    report = build_acceptance_report(
        object_memory=object_memory,
        environment_progression=environment,
        test_result="502 passed",
        commit="dfe4a7de",
    )
    json_path, markdown_path = write_acceptance_report(report, tmp_path)

    assert report.accepted is True
    assert all(report.checks.values())
    assert json.loads(json_path.read_text(encoding="utf-8"))["accepted"] is True
    markdown = markdown_path.read_text(encoding="utf-8")
    assert "**ACCEPTED**" in markdown
    assert "`fixed_camera_physics`" in markdown


def test_acceptance_report_rejects_missing_environment_evidence() -> None:
    object_memory, environment = _summaries()
    environment["environments"]["top_down_manipulation"] = 0

    report = build_acceptance_report(
        object_memory=object_memory,
        environment_progression=environment,
        test_result="502 passed",
        commit="dfe4a7de",
    )

    assert report.accepted is False
    assert report.checks["top_down_manipulation"] is False
