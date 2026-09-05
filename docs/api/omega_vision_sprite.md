# `omega_vision.sprite`

> [← Project README](../../README.md)

## Classes

### `class AlphaContourProvider`

Extract transparent sprites and exact pixel-boundary vector contours.


### `class SpriteAdapter(ImageAdapter)`

Image adapter preconfigured for transparent sprite sheets.

- `__init__(self, provider: 'Any', extractor: 'Any | None' = None) -> 'None'`
- `candidate_detail(self, candidate_id: 'str') -> 'Mapping[str, Any]'`
- `normalize(self, *, observation_id: 'str', image: 'Any', action_tree_node: 'str', artifact_uri: 'str', sequence: 'int | None' = None) -> 'MediaPerceptionBatch'`
- `propose_candidates(self, observation: 'Any') -> 'Iterable[CandidateObject]'`
