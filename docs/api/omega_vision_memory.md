# `omega_vision.memory`

> [← Project README](../../README.md)

## Classes

### `class EncounterLog`

Append-only semantic encounters with deterministic, idempotent replay.

- `__init__(self) -> 'None'`
- `append(self, encounter: 'EncounterRecord') -> 'EncounterRecord'`
- `deterministic_hash(self) -> 'str'`
- `for_object(self, object_identity_id: 'str') -> 'tuple[EncounterRecord, ...]'`
- `get(self, encounter_id: 'str') -> 'EncounterRecord | None'`
- `records(self) -> 'tuple[EncounterRecord, ...]'`
- `replay(self, encounters: 'tuple[EncounterRecord, ...]') -> "'EncounterLog'"`

### `class ResidualGate`

Deterministic admission policy; thresholds remain configuration choices.

- `evaluate(self, residual: 'ResidualCandidate') -> 'ResidualDisposition'`

### `class SingleWriter`

Only mutation path for committed atoms and their evidence.

- `__init__(self, memory: 'SymbolicMemory', checkpoint_sink: 'Callable[[IdentityMemoryCheckpoint], Any] | None' = None) -> 'None'`
- `accrue_evidence(self, handle: 'str', confidence: 'float', evidence: 'str') -> 'CommittedAtom'` — Compatibility path for legacy callers with pre-calibrated evidence.
- `apply_evidence(self, handle: 'str', evidence: 'EvidenceRecord') -> 'CommittedAtom'` — Derive calibrated confidence from attributable signed evidence.
- `commit(self, atom: 'CommittedAtom') -> 'CommittedAtom'`
- `commit_residual(self, residual: 'ResidualCandidate', atom: 'CommittedAtom', gate: 'ResidualGate') -> 'CommittedAtom'` — Commit only a residual that the configured gate admits.
- `demote(self, handle: 'str', reason: 'str', *, checkpoint: 'bool' = True) -> 'CommittedAtom'`
- `merge_identities(self, decision: 'MergeDecision', resulting_atom: 'CommittedAtom') -> 'CommittedAtom'`
- `reverse_identity_decision(self, decision_id: 'str', reason: 'str') -> 'None'`
- `split_identity(self, decision: 'SplitDecision', resulting_atoms: 'tuple[CommittedAtom, ...]') -> 'tuple[CommittedAtom, ...]'`
- `tombstone(self, handle: 'str', reason: 'str') -> 'CommittedAtom'`

### `class SymbolicMemory`

Small in-memory reference store; durable stores may implement this API.

- `__init__(self) -> 'None'`
- `all_atoms(self) -> 'tuple[CommittedAtom, ...]'`
- `checkpoints(self) -> 'tuple[IdentityMemoryCheckpoint, ...]'`
- `confidence_history(self, handle: 'str') -> 'tuple[ConfidenceHistoryRecord, ...]'`
- `events(self) -> 'tuple[dict[str, Any], ...]'`
- `evidence_for(self, handle: 'str') -> 'tuple[EvidenceRecord, ...]'`
- `get(self, handle: 'str') -> 'CommittedAtom | None'`
- `identity_decision(self, decision_id: 'str') -> 'MergeDecision | SplitDecision | None'`
- `restore(self, checkpoint: 'IdentityMemoryCheckpoint') -> "'SymbolicMemory'"` — Restore an exact writer state from one durable checkpoint.
