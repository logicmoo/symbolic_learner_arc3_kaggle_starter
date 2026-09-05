# `omega_vision.providers`

> [← Project README](../../README.md)

## Classes

### `class ArtifactProvider(ABC)`

One stable contract with backend-specific implementations.

- `capabilities(self) -> 'ProviderCapabilities'`
- `get_candidate_part(self, candidate: 'CandidateObject', name: 'str') -> 'NormalizedResult'`

### `class GptArtifactProvider(ArtifactProvider)`

Reads GPT-generated or cached artifacts; it does not emulate native analysis.

- `__init__(self, node_path: 'str | Path') -> 'None'`
- `capabilities(self) -> 'ProviderCapabilities'`
- `get_candidate_part(self, candidate: 'CandidateObject', name: 'str') -> 'NormalizedResult'`

### `class PrologProvider(ArtifactProvider)`

Delegates symbolic queries to SWI-Prolog through an injected query function.

- `__init__(self, query: 'Callable[[str, Mapping[str, Any]], Any]') -> 'None'`
- `capabilities(self) -> 'ProviderCapabilities'`
- `get_candidate_part(self, candidate: 'CandidateObject', name: 'str') -> 'NormalizedResult'`
- `get_semantic_records(self, name: 'str', filters: 'Mapping[str, Any] | None' = None) -> 'NormalizedResult'` — Query one normalized semantic namespace through the Prolog adapter.

### `class ProviderCapabilities`

Fields:
- `mode: ExecutionMode`
- `candidate_parts: tuple[str, ...]`
- `semantic_record_families: tuple[str, ...]`
- `dynamic_candidate_parts: bool`

- `supports_candidate_part(self, name: 'str') -> 'bool'`

### `class PythonProvider(ArtifactProvider)`

One stable contract with backend-specific implementations.

- `__init__(self, resolvers: 'Mapping[str, Callable[[CandidateObject], Any]]') -> 'None'`
- `capabilities(self) -> 'ProviderCapabilities'`
- `get_candidate_part(self, candidate: 'CandidateObject', name: 'str') -> 'NormalizedResult'`

### `class UnsupportedProviderCapability(KeyError)`

Machine-readable failure for a capability the provider does not expose.

- `__init__(self, *, mode: 'ExecutionMode', capability_kind: 'str', requested: 'str', available: 'tuple[str, ...]') -> 'None'`
- `as_dict(self) -> 'dict[str, Any]'`
