import json
from pathlib import Path

from scripts.phase2_object_memory_demo import run_demo


def test_phase2_demo_runs_capture_authorization_reconstruction_and_replay(
    tmp_path: Path,
) -> None:
    summary = run_demo(tmp_path / "demo")

    assert summary["observations"] == 2
    assert summary["encounters"] == 4
    assert summary["turtle_programs"] == 4
    assert summary["exact_reconstructions"] == 4
    assert summary["match_proposals"] >= 4
    assert summary["evidence_records"] >= 4
    assert summary["resolved_accounts"] == 2
    assert summary["recognized_identity"] == "known_shape"
    assert "moved" in summary["object_changes"]
    assert len(summary["replay_hash"]) == 64
    stored = json.loads(Path(summary["summary"]).read_text(encoding="utf-8"))
    assert stored["recognized_identity"] == "known_shape"
    assert Path(summary["action_tree"], "README.md").is_file()
