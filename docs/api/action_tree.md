# `action_tree`

> [← Project README](../../README.md)

## Classes

### `class ActionTreeStore`

Filesystem-backed deterministic action tree.

- `__init__(self, root: 'str | Path', game_id: 'str', level: 'str | int') -> 'None'`
- `action_path(self, path: 'Path') -> 'list[str]'`
- `child_nodes(self, node: 'StateNode') -> 'list[tuple[str, StateNode]]'` — Return direct child action directories that contain captured states.
- `create_initial(self, png_bytes: 'bytes', state_payload: 'Mapping[str, Any]') -> 'StateNode'` — Create or reuse the level-root initial state.
- `create_transition(self, parent: 'StateNode', action: 'str', action_data: 'Mapping[str, Any]', png_bytes: 'bytes', state_payload: 'Mapping[str, Any]') -> 'StateNode'` — Create or reuse the child directory named by the action.
- `identity_facts(self, source: 'str') -> 'dict[str, str]'` — Extract canonical object_identity/3 declarations.
- `image_hash(png_bytes: 'bytes') -> 'str'`
- `link_prediction_history(self, node: 'StateNode', semantic_store: 'Any', prediction_id: 'str') -> 'Path'` — Materialize one prediction-before-outcome audit trail in this node.
- `link_semantic_record(self, node: 'StateNode', *, record_type: 'str', record_id: 'str', artifact_path: 'str | Path', schema_version: 'str', deterministic_hash: 'str') -> 'Path'` — Link a Phase 2/3 record to a node without embedding it in state.json.
- `metadata(self, node: 'StateNode') -> 'dict[str, Any]'`
- `new_identity_facts(self, source: 'str') -> 'dict[str, str]'` — Convert new_object_identity/3 candidates into canonical declarations.
- `opaque_tokens(self, source: 'str') -> 'list[str]'` — Return opaque numbered object tokens appearing anywhere in Prolog.
- `parent_node(self, node: 'StateNode') -> 'StateNode | None'`
- `record_semantic_identity_decision(self, *, identity_id: 'str', encounter_id: 'str', decision_id: 'str', status: 'str', evidence_ids: 'tuple[str, ...]' = ()) -> 'Path'` — Append authoritative Phase 2 history for an existing friendly identity.
- `refresh_readme(self: 'ActionTreeStore', node: 'Any')`
- `registry_decisions(self) -> 'tuple[dict[str, str], ...]'`
- `registry_identities(self) -> 'dict[str, str]'`
- `registry_reference(self, node: 'StateNode') -> 'str'` — Relative Prolog path from a node to the level-wide registry.
- `registry_text(self) -> 'str'`
- `update_registry_from_objects(self, node: 'StateNode') -> 'Path'` — Merge only newly declared identities; state files remain identity-light.
- `validate_friendly_objects(self, source: 'str', node: 'StateNode') -> 'None'` — Validate either the registry itself or a registry-backed node file.
- `write_registry(self, registry: 'Mapping[str, str]') -> 'Path'`

### `class StateNode`

Fields:
- `path: Path`
- `image_hash: str`
