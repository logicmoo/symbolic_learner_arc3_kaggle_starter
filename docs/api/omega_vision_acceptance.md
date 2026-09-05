# `omega_vision.acceptance`

> [← Project README](../../README.md)

## Classes

### `class AcceptanceReport`

Fields:
- `accepted: bool`
- `checks: Mapping[str, bool]`
- `evidence: Mapping[str, Any]`

- `to_json(self) -> 'str'`
- `to_markdown(self) -> 'str'`

## Functions

### `build_acceptance_report(*, object_memory: 'Mapping[str, Any]', environment_progression: 'Mapping[str, Any]', phase3_learning: 'Mapping[str, Any]', test_result: 'str', commit: 'str') -> 'AcceptanceReport'`

### `write_acceptance_report(report: 'AcceptanceReport', output_root: 'Path') -> 'tuple[Path, Path]'`
