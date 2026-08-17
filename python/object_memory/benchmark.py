from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Any, Iterable, Mapping

from PIL import Image

from .adapters import ImageAdapter


@dataclass(frozen=True)
class PerceptionFixture:
    fixture_id: str
    image: Image.Image
    expected_count: int
    degradation: str = "none"


@dataclass(frozen=True)
class PerceptionBenchmarkResult:
    fixture_id: str
    expected_count: int
    detected_count: int
    count_score: float
    degradation: str


class RasterPerturbationGenerator:
    """Create deterministic modest-noise and partial-occlusion fixtures."""

    def __init__(self, seed: int = 0) -> None:
        self.seed = seed

    def noise(self, image: Image.Image, probability: float = 0.05) -> Image.Image:
        if not 0.0 <= probability <= 1.0:
            raise ValueError("noise probability must be between 0 and 1")
        output = image.convert("RGBA")
        random = Random(self.seed)
        for y in range(output.height):
            for x in range(output.width):
                red, green, blue, alpha = output.getpixel((x, y))
                if alpha and random.random() < probability:
                    output.putpixel(
                        (x, y),
                        (255 - red, 255 - green, 255 - blue, alpha),
                    )
        return output

    def occlude(
        self, image: Image.Image, bounds: tuple[int, int, int, int]
    ) -> Image.Image:
        output = image.convert("RGBA")
        left, top, right, bottom = bounds
        for y in range(max(0, top), min(output.height, bottom)):
            for x in range(max(0, left), min(output.width, right)):
                output.putpixel((x, y), (0, 0, 0, 0))
        return output

    def partial_occlusion_dataset(
        self,
        fixture_id: str,
        image: Image.Image,
        *,
        expected_count: int,
        occlusion: tuple[int, int, int, int],
    ) -> tuple[PerceptionFixture, ...]:
        return (
            PerceptionFixture(f"{fixture_id}:clean", image.copy(), expected_count),
            PerceptionFixture(
                f"{fixture_id}:noise",
                self.noise(image),
                expected_count,
                "modest_noise",
            ),
            PerceptionFixture(
                f"{fixture_id}:occluded",
                self.occlude(image, occlusion),
                expected_count,
                "partial_occlusion",
            ),
        )


class PerceptionBenchmarkRunner:
    """Evaluate any normalized image adapter against count-labeled fixtures."""

    def __init__(self, adapter: ImageAdapter) -> None:
        self.adapter = adapter

    def run(
        self, fixtures: Iterable[PerceptionFixture]
    ) -> tuple[PerceptionBenchmarkResult, ...]:
        results = []
        for index, fixture in enumerate(fixtures):
            batch = self.adapter.normalize(
                observation_id=f"benchmark:{fixture.fixture_id}",
                image=fixture.image,
                action_tree_node=f"benchmark/{index:05d}",
                artifact_uri=f"memory://benchmark/{fixture.fixture_id}.png",
            )
            detected = len(batch.candidates)
            maximum = max(fixture.expected_count, detected, 1)
            results.append(
                PerceptionBenchmarkResult(
                    fixture_id=fixture.fixture_id,
                    expected_count=fixture.expected_count,
                    detected_count=detected,
                    count_score=1.0 - abs(fixture.expected_count - detected) / maximum,
                    degradation=fixture.degradation,
                )
            )
        return tuple(results)


class ProviderAblationRunner:
    """Run identical fixtures across named provider/mode adapter variants."""

    def __init__(self, adapters: Mapping[str, ImageAdapter]) -> None:
        if not adapters:
            raise ValueError("at least one provider/mode adapter is required")
        self.adapters = dict(adapters)

    def run(
        self, fixtures: Iterable[PerceptionFixture]
    ) -> Mapping[str, tuple[PerceptionBenchmarkResult, ...]]:
        materialized = tuple(fixtures)
        return {
            name: PerceptionBenchmarkRunner(adapter).run(materialized)
            for name, adapter in sorted(self.adapters.items())
        }
