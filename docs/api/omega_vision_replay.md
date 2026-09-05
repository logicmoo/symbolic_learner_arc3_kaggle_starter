# `omega_vision.replay`

> [← Project README](../../README.md)

## Classes

### `class ActionTreeSemanticReplay`

Rebuild a semantic store from the exact records linked by an action tree.

- `replay(self, action_tree_root: 'Path', store: 'SymbolicStore') -> 'SymbolicStore'`

### `class AtomSpaceSemanticBackend`

Exact semantic records stored as queryable ``semantic_record`` Atoms.

- `__init__(self, transport: 'AtomSpaceTransport | None' = None, *, path: 'Path | None' = None) -> 'None'`
- `get(self, namespace: 'str', record_id: 'str') -> 'Any | None'`
- `values(self, namespace: 'str') -> 'tuple[Any, ...]'`
- `write_once(self, namespace: 'str', record_id: 'str', value: 'Any') -> 'Any'`

### `class AtomSpaceTransport(Protocol)`

Transport boundary for a MeTTa/OpenCog AtomSpace implementation.

- `__init__(self, *args, **kwargs)`
- `assert_expression(self, expression: 'str') -> 'None'`
- `query(self, head: 'str') -> 'Iterable[str]'`

### `class MettaFileAtomSpaceTransport`

Durable AtomSpace transport using an inspectable MeTTa expression file.

- `__init__(self, path: 'Path') -> 'None'`
- `assert_expression(self, expression: 'str') -> 'None'`
- `query(self, head: 'str') -> 'tuple[str, ...]'`

### `class PrologSemanticBackend`

Durable exact-record backend represented as inspectable SWI-Prolog facts.

- `__init__(self, path: 'Path') -> 'None'`
- `get(self, namespace: 'str', record_id: 'str') -> 'Any | None'`
- `values(self, namespace: 'str') -> 'tuple[Any, ...]'`
- `write_once(self, namespace: 'str', record_id: 'str', value: 'Any') -> 'Any'`

### `class SemanticRecordCodec`

Decode exact JSON artifacts emitted by the semantic capture observer.

- `decode(record_type: 'str', value: 'Mapping[str, Any]') -> 'Any'`
- `decode_namespace(namespace: 'str', value: 'Mapping[str, Any]') -> 'Any'`
