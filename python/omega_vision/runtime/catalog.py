from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Any, Mapping

from omega_vision.core.memory import SingleWriter
from omega_vision.core.models import (
    CommittedAtom,
    EncounterRecord,
    EvidenceRecord,
    InstanceParameters,
    ProvenanceRef,
)
from omega_vision.runtime.replay import SemanticRecordCodec
from omega_vision.core.store import SymbolicStore


@dataclass(frozen=True)
class IdentityCatalogEntry:
    identity_id: str
    instance: InstanceParameters
    registry_fact: str | None = None
    evidence: tuple[EvidenceRecord, ...] = ()
    provenance: tuple[str, ...] = ()


@dataclass(frozen=True)
class SemanticIdentityCatalog:
    """Portable durable identities for explicit reuse across examples."""

    entries: tuple[IdentityCatalogEntry, ...]
    source: str
    schema_version: str = "1.0.0"

    @classmethod
    def from_store(
        cls,
        store: SymbolicStore,
        *,
        source: str,
        registry: Mapping[str, str] | None = None,
    ) -> "SemanticIdentityCatalog":
        resolved = {
            account.candidate_id: account
            for account in store.values("recognition_accounts")
            if account.stored_identity_id is not None
            and account.decision_source != "unresolved"
        }
        histories: dict[str, list[Any]] = {}
        evidence_by_identity: dict[str, dict[str, EvidenceRecord]] = {}
        for encounter in store.encounters.records():
            identity_id = encounter.object_identity_id
            if identity_id is None and encounter.candidate_identity_id in resolved:
                account = resolved[encounter.candidate_identity_id]
                identity_id = account.stored_identity_id
                for evidence_id in (
                    *account.supporting_evidence_ids,
                    *account.contradicting_evidence_ids,
                ):
                    evidence = store.get("evidence", evidence_id)
                    if evidence is not None:
                        evidence_by_identity.setdefault(identity_id, {})[
                            evidence_id
                        ] = evidence
            if identity_id is not None:
                histories.setdefault(identity_id, []).append(encounter)
        entries = []
        for identity_id, encounters in sorted(histories.items()):
            best = max(
                encounters,
                key=lambda item: (
                    item.instance.visibility,
                    -item.instance.noise_score,
                    len(item.instance.appearance),
                    len(item.instance.geometry),
                    item.encounter_id,
                ),
            )
            entries.append(
                IdentityCatalogEntry(
                    identity_id=identity_id,
                    instance=best.instance,
                    registry_fact=(registry or {}).get(identity_id),
                    evidence=tuple(
                        evidence_by_identity.get(identity_id, {})[evidence_id]
                        for evidence_id in sorted(
                            evidence_by_identity.get(identity_id, {})
                        )
                    ),
                    provenance=tuple(
                        dict.fromkeys(
                            (
                                best.encounter_id,
                                best.observation_id,
                                best.action_tree_node,
                                source,
                            )
                        )
                    ),
                )
            )
        return cls(tuple(entries), source)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True) + "\n"

    @classmethod
    def from_json(cls, value: str) -> "SemanticIdentityCatalog":
        raw = json.loads(value)
        codec = SemanticRecordCodec()
        entries = []
        for item in raw.get("entries") or ():
            instance = codec.decode(
                "encounter",
                {
                    "encounter_id": "catalog-decode",
                    "observation_id": "catalog-decode",
                    "action_tree_node": "catalog-decode",
                    "deterministic_hash": "catalog-decode",
                    "instance": item["instance"],
                },
            ).instance
            evidence = tuple(codec.decode("evidence", record) for record in item.get("evidence") or ())
            entries.append(
                IdentityCatalogEntry(
                    identity_id=str(item["identity_id"]),
                    instance=instance,
                    registry_fact=item.get("registry_fact"),
                    evidence=evidence,
                    provenance=tuple(item.get("provenance") or ()),
                )
            )
        return cls(
            entries=tuple(entries),
            source=str(raw["source"]),
            schema_version=str(raw.get("schema_version", "1.0.0")),
        )

    def import_into(
        self, store: SymbolicStore, *, writer: SingleWriter | None = None
    ) -> tuple[EncounterRecord, ...]:
        imported = []
        for entry in self.entries:
            provenance = ProvenanceRef.create(
                source_id=self.source,
                provider="semantic_identity_catalog",
                metadata={"identity_id": entry.identity_id},
            )
            encounter = EncounterRecord.create(
                observation_id=f"catalog:{self.source}",
                action_tree_node=f"catalog://{self.source}",
                object_identity_id=entry.identity_id,
                instance=entry.instance,
                provenance=(provenance,),
            )
            store.put_encounter(encounter)
            imported.append(encounter)
            if writer is not None:
                if writer.memory.get(entry.identity_id) is None:
                    writer.commit(
                        CommittedAtom(
                            entry.identity_id,
                            "object",
                            {"authority": "cross_example_catalog"},
                            provenance=entry.provenance,
                        )
                    )
                for evidence in entry.evidence:
                    writer.apply_evidence(entry.identity_id, evidence)
                    store.put_evidence(evidence)
        return tuple(imported)

    def install_registry(self, action_tree_store: Any) -> Mapping[str, str]:
        """Merge exact exported friendly facts into another level registry."""

        registry = dict(action_tree_store.registry_identities())
        for entry in self.entries:
            if entry.registry_fact is None:
                continue
            existing = registry.get(entry.identity_id)
            if existing is not None and existing != entry.registry_fact:
                raise ValueError(
                    f"Registry identity conflict for {entry.identity_id!r}"
                )
            registry[entry.identity_id] = entry.registry_fact
        if registry:
            action_tree_store.write_registry(registry)
        return registry
