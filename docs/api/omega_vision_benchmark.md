# `omega_vision.benchmark`

> [← Project README](../../README.md)

## Classes

### `class PerceptionBenchmarkResult`

Fields:
- `fixture_id: str`
- `expected_count: int`
- `detected_count: int`
- `count_score: float`
- `degradation: str`


### `class PerceptionBenchmarkRunner`

Evaluate any normalized image adapter against count-labeled fixtures.

- `__init__(self, adapter: 'ImageAdapter') -> 'None'`
- `run(self, fixtures: 'Iterable[PerceptionFixture]') -> 'tuple[PerceptionBenchmarkResult, ...]'`

### `class PerceptionFixture`

Fields:
- `fixture_id: str`
- `image: Image.Image`
- `expected_count: int`
- `degradation: str`


### `class ProviderAblationRunner`

Run identical fixtures across named provider/mode adapter variants.

- `__init__(self, adapters: 'Mapping[str, ImageAdapter]') -> 'None'`
- `run(self, fixtures: 'Iterable[PerceptionFixture]') -> 'Mapping[str, tuple[PerceptionBenchmarkResult, ...]]'`

### `class RasterPerturbationGenerator`

Create deterministic modest-noise and partial-occlusion fixtures.

- `__init__(self, seed: 'int' = 0) -> 'None'`
- `noise(self, image: 'Image.Image', probability: 'float' = 0.05) -> 'Image.Image'`
- `occlude(self, image: 'Image.Image', bounds: 'tuple[int, int, int, int]') -> 'Image.Image'`
- `partial_occlusion_dataset(self, fixture_id: 'str', image: 'Image.Image', *, expected_count: 'int', occlusion: 'tuple[int, int, int, int]') -> 'tuple[PerceptionFixture, ...]'`
