from PIL import Image

from omega_vision import (
    PerceptionFixture,
    ProviderAblationRunner,
    PythonProvider,
    SpriteAdapter,
    TranscriptScorer,
)


def test_provider_ablation_runs_the_same_materialized_fixture_set() -> None:
    image = Image.new("RGBA", (2, 1), (255, 0, 0, 255))
    fixtures = (PerceptionFixture("one", image, 1),)
    result = ProviderAblationRunner(
        {
            "alpha/default": SpriteAdapter(PythonProvider({})),
            "alpha/repeat": SpriteAdapter(PythonProvider({})),
        }
    ).run(fixtures)

    assert tuple(result) == ("alpha/default", "alpha/repeat")
    assert all(values[0].count_score == 1.0 for values in result.values())


def test_transcript_scorer_reports_membership_order_and_exactness() -> None:
    expected = [{"event": "capture", "id": 1}, {"event": "predict", "id": 2}]
    actual = [{"id": 1, "event": "capture"}, {"event": "extra"}, {"id": 2, "event": "predict"}]

    score = TranscriptScorer().compare(expected, actual)

    assert score.exact_matches == 2
    assert score.ordered_prefix_matches == 1
    assert score.event_recall == 1.0
    assert score.exact is False
