from PIL import Image

from object_memory import (
    PerceptionBenchmarkRunner,
    PythonProvider,
    RasterPerturbationGenerator,
    SpriteAdapter,
)


def _fixture() -> Image.Image:
    image = Image.new("RGBA", (8, 4), (0, 0, 0, 0))
    for cell in ((0, 0), (1, 0), (0, 1), (5, 1), (6, 1), (5, 2), (6, 2)):
        image.putpixel(cell, (255, 0, 0, 255))
    return image


def test_perturbations_are_deterministic_and_preserve_the_source() -> None:
    source = _fixture()
    generator = RasterPerturbationGenerator(seed=19)

    first = generator.noise(source, probability=0.5)
    second = generator.noise(source, probability=0.5)
    occluded = generator.occlude(source, (0, 0, 1, 1))

    assert first.tobytes() == second.tobytes()
    assert source.getpixel((0, 0))[3] == 255
    assert occluded.getpixel((0, 0))[3] == 0


def test_benchmark_runner_scores_clean_noise_and_partial_occlusion() -> None:
    fixtures = RasterPerturbationGenerator(seed=3).partial_occlusion_dataset(
        "two-sprites",
        _fixture(),
        expected_count=2,
        occlusion=(1, 0, 2, 1),
    )

    results = PerceptionBenchmarkRunner(SpriteAdapter(PythonProvider({}))).run(fixtures)

    assert [result.degradation for result in results] == [
        "none",
        "modest_noise",
        "partial_occlusion",
    ]
    assert all(result.detected_count == 2 for result in results)
    assert all(result.count_score == 1.0 for result in results)
