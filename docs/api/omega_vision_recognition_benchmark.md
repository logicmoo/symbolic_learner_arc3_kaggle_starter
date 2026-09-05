# `omega_vision.recognition_benchmark`

> [← Project README](../../README.md)

## Classes

### `class RecognitionBenchmarkResult`

Fields:
- `fixture_id: str`
- `scope: str`
- `accounts: tuple[RecognitionAccount, ...]`


### `class RecognitionBenchmarkRunner`

Exercise the real matcher and retain outcomes for every rival proposal.

- `__init__(self, matcher: 'InstanceMatcher | None' = None) -> 'None'`
- `accounts(results: 'tuple[RecognitionBenchmarkResult, ...]', *, scope: 'str | None' = None) -> 'tuple[RecognitionAccount, ...]'`
- `run(self, fixtures: 'tuple[RecognitionFixture, ...]') -> 'tuple[RecognitionBenchmarkResult, ...]'`

### `class RecognitionFixture`

One authority-labeled candidate and its complete identity rival set.

Fields:
- `fixture_id: str`
- `scope: str`
- `current: InstanceParameters`
- `stored: Mapping[str, InstanceParameters]`
- `accepted_identity_id: str | None`
