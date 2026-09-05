# `omega_vision.forms`

> [← Project README](../../README.md)

## Classes

### `class AbstractGenerativeForm(ABC)`

Abstract typed contract for a generative form (Turtle/LOGO and later raster).

- `canonicalize(self) -> 'str'`
- `distance(self, other: "'AbstractGenerativeForm'") -> 'float'`
- `fit_instance(self, candidate: 'Any') -> 'FitResult'`
- `render(self, params: 'dict[str, Any] | None' = None) -> 'Any'`

### `class FitResult`

Fields:
- `parameters: dict[str, Any]`
- `residual: float`


### `class GenerativeForm(AbstractGenerativeForm)`

Canonical Turtle/LOGO generative form over the existing DSL program.

- `__init__(self, program: 'str', renderer: 'Any | None' = None, swi_bridge: 'Any | None' = None) -> 'None'`
- `canonicalize(self) -> 'str'`
- `description_length(self) -> 'int'`
- `distance(self, other: 'AbstractGenerativeForm') -> 'float'`
- `fit_instance(self, candidate: 'Any') -> 'FitResult'`
- `render(self, params: 'dict[str, Any] | None' = None) -> 'Any'`
