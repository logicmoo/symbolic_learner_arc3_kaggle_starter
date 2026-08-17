from object_memory import (
    InstanceParameters,
    RecognitionBenchmarkRunner,
    RecognitionCalibrator,
    RecognitionFixture,
)


def _grid(
    cells,
    *,
    color="blue",
    visibility=1.0,
    noise_score=0.0,
):
    return InstanceParameters(
        geometry={"cells": tuple(cells)},
        appearance={"color": color, "shape": "bar"},
        visibility=visibility,
        noise_score=noise_score,
        supported_transformations=("translation", "partial_visibility", "noise"),
    )


def test_domain_fixtures_generate_labeled_rivals_and_fit_scoped_policy() -> None:
    blue = _grid(((0, 0), (1, 0), (2, 0)))
    red = _grid(((0, 0), (0, 1), (0, 2)), color="red")
    fixtures = (
        RecognitionFixture(
            "clean-blue",
            "grid/occlusion-v1",
            blue,
            {"blue": blue, "red": red},
            "blue",
        ),
        RecognitionFixture(
            "noisy-blue",
            "grid/occlusion-v1",
            _grid(((0, 0), (1, 0), (2, 0)), noise_score=0.15),
            {"blue": blue, "red": red},
            "blue",
        ),
        RecognitionFixture(
            "partial-blue",
            "grid/occlusion-v1",
            _grid(((0, 0), (1, 0)), visibility=0.67),
            {"blue": blue, "red": red},
            "blue",
        ),
    )

    runner = RecognitionBenchmarkRunner()
    results = runner.run(fixtures)
    accounts = runner.accounts(results, scope="grid/occlusion-v1")
    policy = RecognitionCalibrator().fit(accounts, scope="grid/occlusion-v1")
    report = RecognitionCalibrator().calibrated_report(accounts, policy, bin_count=2)

    assert len(results) == 3
    assert len(accounts) == 6
    assert sum(account.decision_outcome is True for account in accounts) == 3
    assert sum(account.decision_outcome is False for account in accounts) == 3
    assert all(
        account.decision_source == "benchmark_authority:grid/occlusion-v1"
        for account in accounts
    )
    assert policy.sample_count == 6
    assert report.sample_count == 6


def test_benchmark_retains_authoritative_no_match_outcomes() -> None:
    candidate = _grid(((5, 5),), color="green")
    result = RecognitionBenchmarkRunner().run(
        (
            RecognitionFixture(
                "unknown",
                "grid/open-set-v1",
                candidate,
                {"blue": _grid(((0, 0),)), "red": _grid(((0, 0),), color="red")},
                None,
            ),
        )
    )[0]

    assert result.accounts
    assert all(account.decision_outcome is False for account in result.accounts)
    assert all(account.stored_identity_id is None for account in result.accounts)
