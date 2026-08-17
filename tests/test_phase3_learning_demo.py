from scripts.phase3_learning_demo import run_demo


def test_phase3_learning_demo_covers_predict_grade_update_and_replay(tmp_path) -> None:
    summary = run_demo(tmp_path)

    assert summary["transition_changes"] == ["moved_right"]
    assert summary["transformation_candidates"] == ["move-right"]
    assert summary["rules"] == ["rule-move-right"]
    assert summary["prediction_recorded_before_outcome"] is True
    assert summary["independent_grade"] == 1.0
    assert summary["grade_evidence"] == ["independent_outcome"]
    assert summary["calibrated_probability"] == 2.0 / 3.0
    assert summary["probability_source"] == "verified_prediction_history"
    assert summary["replayed_prediction"] is True
    assert summary["replayed_grade"] is True
