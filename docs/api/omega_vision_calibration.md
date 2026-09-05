# `omega_vision.calibration`

> [← Project README](../../README.md)

## Classes

### `class CalibrationPoint`

Fields:
- `upper_confidence: float`
- `probability: float`
- `sample_count: int`


### `class RecognitionCalibrationPolicy`

Serializable monotone mapping learned from authoritative outcomes.

Fields:
- `scope: str`
- `sample_count: int`
- `points: tuple[CalibrationPoint, ...]`
- `method: str`

- `calibrate(self, confidence: 'float') -> 'float'`
- `to_dict(self) -> 'dict[str, Any]'`

### `class RecognitionCalibrationReport`

Fields:
- `scope: str`
- `sample_count: int`
- `brier_score: float | None`
- `bins: tuple[ReliabilityBin, ...]`


### `class RecognitionCalibrator`

Measure pre-decision confidence against later authority outcomes.

- `calibrated_report(self, accounts: 'Iterable[RecognitionAccount]', policy: 'RecognitionCalibrationPolicy', *, bin_count: 'int' = 10) -> 'RecognitionCalibrationReport'`
- `fit(self, accounts: 'Iterable[RecognitionAccount]', *, scope: 'str') -> 'RecognitionCalibrationPolicy'` — Fit a deterministic pool-adjacent-violators isotonic policy.
- `report(self, accounts: 'Iterable[RecognitionAccount]', *, scope: 'str' = 'all', bin_count: 'int' = 10) -> 'RecognitionCalibrationReport'`

### `class ReliabilityBin`

Fields:
- `lower: float`
- `upper: float`
- `count: int`
- `mean_confidence: float`
- `acceptance_rate: float`
- `brier_score: float`
