from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict, is_dataclass
from enum import Enum
from pathlib import Path
import re
from typing import Any, Mapping

from .models import (
    ArtifactRef,
    CommittedAtom,
    ConfidenceHistoryRecord,
    EncounterRecord,
    EvidencePolarity,
    EvidenceRecord,
    InstanceParameters,
    MatchProposal,
    Observation,
    ObjectChange,
    ProvenanceRef,
    RecognitionAccount,
    ResidualCandidate,
    ResidualDisposition,
    TurtleProgramRef,
)
from .store import SymbolicStore


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    return value


def _provenance(value: Mapping[str, Any]) -> ProvenanceRef:
    return ProvenanceRef(
        source_id=str(value["source_id"]),
        provider=str(value["provider"]),
        action_tree_node=value.get("action_tree_node"),
        artifact_id=value.get("artifact_id"),
        sequence=value.get("sequence"),
        metadata=dict(value.get("metadata") or {}),
        schema_version=str(value.get("schema_version", "2.0.0")),
    )


def _artifact(value: Mapping[str, Any]) -> ArtifactRef:
    return ArtifactRef(
        artifact_id=str(value["artifact_id"]),
        artifact_type=str(value["artifact_type"]),
        uri=str(value["uri"]),
        content_hash=value.get("content_hash"),
        media_type=value.get("media_type"),
        provenance=tuple(_provenance(item) for item in value.get("provenance") or ()),
        schema_version=str(value.get("schema_version", "2.0.0")),
    )


def _turtle(value: Mapping[str, Any]) -> TurtleProgramRef:
    return TurtleProgramRef(
        artifact=_artifact(value["artifact"]),
        language=str(value.get("language", "turtle_dsl")),
        entrypoint=value.get("entrypoint"),
        fit_score=value.get("fit_score"),
        distance=value.get("distance"),
        residual_score=value.get("residual_score"),
        description_length=value.get("description_length"),
        schema_version=str(value.get("schema_version", "2.0.0")),
    )


def _instance(value: Mapping[str, Any]) -> InstanceParameters:
    geometry = dict(value.get("geometry") or {})
    if "boundary_cells" in geometry:
        geometry["boundary_cells"] = tuple(
            tuple(cell) for cell in geometry.get("boundary_cells") or ()
        )
    topology = dict(value.get("topology") or {})
    if "holes" in topology:
        topology["holes"] = tuple(
            tuple(tuple(cell) for cell in hole)
            for hole in topology.get("holes") or ()
        )
    return InstanceParameters(
        position=tuple(value.get("position") or ()),
        orientation=value.get("orientation"),
        scale=tuple(value.get("scale") or (1.0,)),
        appearance=dict(value.get("appearance") or {}),
        supported_transformations=tuple(value.get("supported_transformations") or ()),
        reflection=value.get("reflection"),
        visibility=float(value.get("visibility", 1.0)),
        noise_score=float(value.get("noise_score", 0.0)),
        geometry=geometry,
        topology=topology,
        relationships=tuple(
            dict(item) for item in value.get("relationships") or ()
        ),
        schema_version=str(value.get("schema_version", "2.0.0")),
    )


def _changed_properties(value: Mapping[str, Any]) -> dict[str, Any]:
    def tuplify(item: Any) -> Any:
        if isinstance(item, list):
            return tuple(tuplify(value) for value in item)
        if isinstance(item, Mapping):
            return {key: tuplify(value) for key, value in item.items()}
        return item

    restored: dict[str, Any] = {}
    for field, change in value.items():
        if isinstance(change, Mapping) and {"from", "to"}.issubset(change):
            restored[field] = {
                key: (
                    tuplify(item)
                    if field
                    in {"position", "scale", "geometry", "topology", "relationships"}
                    else item
                )
                for key, item in change.items()
            }
        else:
            restored[field] = change
    return restored


class SemanticRecordCodec:
    """Decode exact JSON artifacts emitted by the semantic capture observer."""

    @staticmethod
    def decode(record_type: str, value: Mapping[str, Any]) -> Any:
        if record_type == "observation":
            return Observation(
                observation_id=str(value["observation_id"]),
                source_modality=str(value["source_modality"]),
                artifacts=tuple(_artifact(item) for item in value.get("artifacts") or ()),
                dimensions=tuple(value.get("dimensions") or ()),
                coordinate_contract=str(value.get("coordinate_contract", "")),
                candidate_object_ids=tuple(value.get("candidate_object_ids") or ()),
                action_tree_node=value.get("action_tree_node"),
                provenance=tuple(_provenance(item) for item in value.get("provenance") or ()),
                schema_version=str(value.get("schema_version", "2.0.0")),
            )
        if record_type == "encounter":
            return EncounterRecord(
                encounter_id=str(value["encounter_id"]),
                observation_id=str(value["observation_id"]),
                action_tree_node=str(value["action_tree_node"]),
                object_identity_id=value.get("object_identity_id"),
                candidate_identity_id=value.get("candidate_identity_id"),
                instance=_instance(value.get("instance") or {}),
                matched_properties=tuple(value.get("matched_properties") or ()),
                changed_properties=_changed_properties(value.get("changed_properties") or {}),
                turtle_programs=tuple(_turtle(item) for item in value.get("turtle_programs") or ()),
                reconstruction_artifacts=tuple(
                    _artifact(item) for item in value.get("reconstruction_artifacts") or ()
                ),
                residual_ids=tuple(value.get("residual_ids") or ()),
                confidence=float(value.get("confidence", 0.0)),
                evidence_ids=tuple(value.get("evidence_ids") or ()),
                previous_encounter_id=value.get("previous_encounter_id"),
                next_encounter_id=value.get("next_encounter_id"),
                provenance=tuple(_provenance(item) for item in value.get("provenance") or ()),
                deterministic_hash=str(value.get("deterministic_hash", "")),
                schema_version=str(value.get("schema_version", "2.0.0")),
            )
        if record_type == "match_proposal":
            return MatchProposal(
                proposal_id=str(value["proposal_id"]),
                candidate_id=str(value["candidate_id"]),
                stored_identity_id=str(value["stored_identity_id"]),
                matched_properties=tuple(value.get("matched_properties") or ()),
                changed_properties=_changed_properties(value.get("changed_properties") or {}),
                allowed_transformations=tuple(value.get("allowed_transformations") or ()),
                similarity=value.get("similarity"),
                evidence_ids=tuple(value.get("evidence_ids") or ()),
                provenance=tuple(_provenance(item) for item in value.get("provenance") or ()),
                schema_version=str(value.get("schema_version", "2.0.0")),
            )
        if record_type == "recognition_account":
            return RecognitionAccount(
                account_id=str(value["account_id"]),
                candidate_id=str(value["candidate_id"]),
                stored_identity_id=value.get("stored_identity_id"),
                matched_properties=tuple(value.get("matched_properties") or ()),
                changed_properties=_changed_properties(value.get("changed_properties") or {}),
                allowed_transformations=tuple(value.get("allowed_transformations") or ()),
                turtle_reconstruction_fit=value.get("turtle_reconstruction_fit"),
                residual_score=value.get("residual_score"),
                supporting_evidence_ids=tuple(value.get("supporting_evidence_ids") or ()),
                contradicting_evidence_ids=tuple(value.get("contradicting_evidence_ids") or ()),
                rival_proposal_ids=tuple(value.get("rival_proposal_ids") or ()),
                calibrated_confidence=float(value.get("calibrated_confidence", 0.0)),
                decision_source=str(value.get("decision_source", "unresolved")),
                provenance=tuple(_provenance(item) for item in value.get("provenance") or ()),
                schema_version=str(value.get("schema_version", "2.0.0")),
            )
        if record_type == "evidence":
            return EvidenceRecord(
                evidence_id=str(value["evidence_id"]),
                subject_id=str(value["subject_id"]),
                polarity=EvidencePolarity(str(value["polarity"])),
                source=_provenance(value["source"]),
                weight=float(value.get("weight", 1.0)),
                detail=dict(value.get("detail") or {}),
                created_sequence=int(value.get("created_sequence", 0)),
                schema_version=str(value.get("schema_version", "2.0.0")),
            )
        if record_type == "object_change":
            return ObjectChange(
                change_id=str(value["change_id"]),
                kind=str(value["kind"]),
                before_identity_ids=tuple(value.get("before_identity_ids") or ()),
                after_candidate_ids=tuple(value.get("after_candidate_ids") or ()),
                properties=_changed_properties(value.get("properties") or {}),
                evidence_ids=tuple(value.get("evidence_ids") or ()),
                provenance=tuple(_provenance(item) for item in value.get("provenance") or ()),
                schema_version=str(value.get("schema_version", "2.0.0")),
            )
        if record_type == "residual":
            return ResidualCandidate(
                residual_id=str(value["residual_id"]),
                source_candidate_id=str(value["source_candidate_id"]),
                disposition=ResidualDisposition(str(value["disposition"])),
                residual_length=float(value["residual_length"]),
                structured=bool(value.get("structured", False)),
                recurrence_count=int(value.get("recurrence_count", 0)),
                prediction_gain=float(value.get("prediction_gain", 0.0)),
                provenance=tuple(value.get("provenance") or ()),
            )
        raise ValueError(f"unsupported semantic record type: {record_type!r}")

    @staticmethod
    def decode_namespace(namespace: str, value: Mapping[str, Any]) -> Any:
        record_types = {
            "observations": "observation",
            "encounters": "encounter",
            "match_proposals": "match_proposal",
            "recognition_accounts": "recognition_account",
            "evidence": "evidence",
            "object_changes": "object_change",
            "residuals": "residual",
        }
        if namespace in record_types:
            return SemanticRecordCodec.decode(record_types[namespace], value)
        if namespace == "artifacts":
            return _artifact(value)
        if namespace == "turtle_programs":
            return _turtle(value)
        if namespace == "atoms":
            return CommittedAtom(
                handle=str(value["handle"]),
                atom_type=str(value["atom_type"]),
                payload=dict(value.get("payload") or {}),
                confidence=float(value.get("confidence", 0.0)),
                provenance=tuple(value.get("provenance") or ()),
                lifecycle_state=str(value.get("lifecycle_state", "active")),
            )
        if namespace == "confidence_history":
            return ConfidenceHistoryRecord(
                sequence=int(value["sequence"]),
                handle=str(value["handle"]),
                confidence=float(value["confidence"]),
                lifecycle_state=str(value["lifecycle_state"]),
                event=str(value["event"]),
                reference_id=value.get("reference_id"),
            )
        raise ValueError(f"unsupported semantic namespace: {namespace!r}")


class PrologSemanticBackend:
    """Durable exact-record backend represented as inspectable SWI-Prolog facts."""

    FACT = re.compile(r"^semantic_record\((.+?), (.+?), (.+)\)\.$")

    def __init__(self, path: Path) -> None:
        self.path = path
        self._records: dict[str, dict[str, Any]] = defaultdict(dict)
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        for line in self.path.read_text(encoding="utf-8").splitlines():
            match = self.FACT.match(line.strip())
            if match is None:
                continue
            namespace = json.loads(match.group(1))
            record_id = json.loads(match.group(2))
            payload_source = json.loads(match.group(3))
            payload = json.loads(payload_source)
            self._records[str(namespace)][str(record_id)] = (
                SemanticRecordCodec.decode_namespace(str(namespace), payload)
            )

    def _flush(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "% Durable Phase 2 semantic records. JSON payloads preserve exact contracts.",
            ":- dynamic semantic_record/3.",
            "",
        ]
        for namespace in sorted(self._records):
            for record_id in sorted(self._records[namespace]):
                payload = json.dumps(
                    _jsonable(self._records[namespace][record_id]),
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
                lines.append(
                    "semantic_record("
                    f"{json.dumps(namespace, ensure_ascii=False)}, "
                    f"{json.dumps(record_id, ensure_ascii=False)}, "
                    f"{json.dumps(payload, ensure_ascii=False)})."
                )
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text("\n".join(lines) + "\n", encoding="utf-8")
        temporary.replace(self.path)

    def write_once(self, namespace: str, record_id: str, value: Any) -> Any:
        existing = self._records[namespace].get(record_id)
        if existing is not None:
            if existing != value:
                raise ValueError(f"Semantic identity conflict for {namespace}/{record_id}")
            return existing
        self._records[namespace][record_id] = value
        self._flush()
        return value

    def get(self, namespace: str, record_id: str) -> Any | None:
        return self._records.get(namespace, {}).get(record_id)

    def values(self, namespace: str) -> tuple[Any, ...]:
        records = self._records.get(namespace, {})
        return tuple(records[item] for item in sorted(records))


class ActionTreeSemanticReplay:
    """Rebuild a semantic store from the exact records linked by an action tree."""

    ORDER = (
        "observation",
        "encounter",
        "match_proposal",
        "recognition_account",
        "evidence",
        "object_change",
        "residual",
    )

    def replay(self, action_tree_root: Path, store: SymbolicStore) -> SymbolicStore:
        records: dict[tuple[str, str], tuple[Path, Mapping[str, Any]]] = {}
        for manifest_path in sorted(action_tree_root.rglob("semantic_records.json")):
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            for entry in manifest.get("records") or ():
                record_type = str(entry["record_type"])
                if record_type not in self.ORDER:
                    continue
                artifact_path = (manifest_path.parent / str(entry["artifact"])).resolve()
                payload = json.loads(artifact_path.read_text(encoding="utf-8"))
                key = (record_type, str(entry["record_id"]))
                existing = records.get(key)
                if existing is not None and existing[1] != payload:
                    raise ValueError(f"conflicting action-tree semantic record: {key}")
                records[key] = (artifact_path, payload)
        writers = {
            "observation": store.put_observation,
            "match_proposal": store.put_match_proposal,
            "recognition_account": store.put_recognition,
            "evidence": store.put_evidence,
            "object_change": store.put_object_change,
            "residual": store.put_residual,
        }
        for record_type in self.ORDER:
            if record_type == "encounter":
                pending = {
                    key: SemanticRecordCodec.decode(record_type, records[key][1])
                    for key in sorted(item for item in records if item[0] == record_type)
                }
                while pending:
                    ready = [
                        key
                        for key, encounter in pending.items()
                        if encounter.previous_encounter_id is None
                        or store.encounters.get(encounter.previous_encounter_id) is not None
                    ]
                    if not ready:
                        missing = sorted(
                            {
                                encounter.previous_encounter_id
                                for encounter in pending.values()
                                if encounter.previous_encounter_id is not None
                            }
                        )
                        raise ValueError(
                            "action-tree encounter history has missing or cyclic predecessors: "
                            f"{missing}"
                        )
                    for key in ready:
                        store.put_encounter(pending.pop(key))
                continue
            for key in sorted(item for item in records if item[0] == record_type):
                writers[record_type](SemanticRecordCodec.decode(record_type, records[key][1]))
        return store
