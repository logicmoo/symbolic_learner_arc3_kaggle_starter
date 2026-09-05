# `omega_vision.adapters`

> [← Project README](../../README.md)

## Classes

### `class GridAdapter(PerceptionAdapter)`

Thin adapter around an existing grid object extractor.

- `__init__(self, extractor: 'Any', provider: 'Any', role_provider: 'Any | None' = None) -> 'None'`
- `candidate_detail(self, candidate_id: 'str') -> 'Mapping[str, Any]'`
- `normalize(self, *, observation_id: 'str', grid: 'Any', action_tree_node: 'str', artifact_uri: 'str') -> 'GridPerceptionBatch'` — Wrap the established extractor result in Phase 2 contracts.
- `propose_candidates(self, observation: 'Any') -> 'Iterable[CandidateObject]'`

### `class GridPerceptionBatch`

Fields:
- `observation: Observation`
- `candidates: tuple[CandidateObject, ...]`
- `extractor_details: Mapping[str, Mapping[str, Any]]`


### `class ImageAdapter(PerceptionAdapter)`

Normalize raster extractor output without prescribing segmentation.

- `__init__(self, extractor: 'Any', provider: 'Any', role_provider: 'Any | None' = None) -> 'None'`
- `candidate_detail(self, candidate_id: 'str') -> 'Mapping[str, Any]'`
- `normalize(self, *, observation_id: 'str', image: 'Any', action_tree_node: 'str', artifact_uri: 'str', sequence: 'int | None' = None) -> 'MediaPerceptionBatch'`
- `propose_candidates(self, observation: 'Any') -> 'Iterable[CandidateObject]'`

### `class LearnedPartRoleProvider`

Infer semantic component roles from labeled structural examples.

- `__init__(self, examples: 'Iterable[Mapping[str, Any]]') -> 'None'`
- `infer_part_roles(self, _item: 'Mapping[str, Any]', components: 'tuple[tuple[tuple[int, int], ...], ...]') -> 'tuple[Mapping[str, Any], ...]'`

### `class MediaPerceptionBatch`

Fields:
- `observation: Observation`
- `candidates: tuple[CandidateObject, ...]`
- `extractor_details: Mapping[str, Mapping[str, Any]]`


### `class PerceptionAdapter(ABC)`

Domain seam; core code must not import ARC or raster assumptions.

- `propose_candidates(self, observation: 'Any') -> 'Iterable[CandidateObject]'`

### `class SimpleVideoAdapter(PerceptionAdapter)`

Adapt an ordered iterable of decoded frames through an ImageAdapter.

- `__init__(self, image_adapter: 'ImageAdapter') -> 'None'`
- `normalize(self, *, observation_id: 'str', frames: 'Iterable[Any]', action_tree_node: 'str', artifact_uri: 'str') -> 'tuple[MediaPerceptionBatch, ...]'`
- `propose_candidates(self, observation: 'Any') -> 'Iterable[CandidateObject]'`

## Functions

### `normalize_grid_structure(item: 'Mapping[str, Any]', role_provider: 'Any | None' = None) -> 'Mapping[str, Any]'`

Normalize extractor-specific grid structure into one semantic contract.

### `normalize_image_structure(item: 'Mapping[str, Any]', role_provider: 'Any | None' = None) -> 'Mapping[str, Any]'`

Preserve provider raster semantics in the shared normalized contract.
