# `omega_vision.catalog`

> [← Project README](../../README.md)

## Classes

### `class IdentityCatalogEntry`

Fields:
- `identity_id: str`
- `instance: InstanceParameters`
- `registry_fact: str | None`
- `evidence: tuple[EvidenceRecord, ...]`
- `provenance: tuple[str, ...]`


### `class SemanticIdentityCatalog`

Portable durable identities for explicit reuse across examples.

Fields:
- `entries: tuple[IdentityCatalogEntry, ...]`
- `source: str`
- `schema_version: str`

- `import_into(self, store: 'SymbolicStore', *, writer: 'SingleWriter | None' = None) -> 'tuple[EncounterRecord, ...]'`
- `install_registry(self, action_tree_store: 'Any') -> 'Mapping[str, str]'` — Merge exact exported friendly facts into another level registry.
- `to_json(self) -> 'str'`
