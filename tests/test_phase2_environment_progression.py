from scripts.phase2_environment_progression_demo import run_demo


def test_environment_progression_demo_is_reproducible(tmp_path) -> None:
    first = run_demo(tmp_path / "first")
    second = run_demo(tmp_path / "second")

    assert first["accepted"] is True
    assert first["environments"] == {
        "rendered_arcade": 1,
        "fixed_camera_physics": 3,
        "top_down_manipulation": 3,
    }
    assert first["fixtures"] == 7
    assert first["perfect_count_scores"] == 7
    assert first["results"] == second["results"]
