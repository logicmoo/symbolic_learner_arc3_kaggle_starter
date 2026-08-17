from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .models import (
    ArtifactRef,
    EncounterRecord,
    EvidencePolarity,
    EvidenceRecord,
    InstanceParameters,
    MatchProposal,
    Observation,
    ProvenanceRef,
    RecognitionAccount,
    TurtleProgramRef,
)
from .store import SymbolicStore


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
    return InstanceParameters(
        position=tuple(value.get("position") or ()),
        orientation=value.get("orientation"),
        scale=tuple(value.get("scale") or (1.0,)),
        appearance=dict(value.get("appearance") or {}),
        supported_transformations=tuple(value.get("supported_transformations") or ()),
        schema_version=str(value.get("schema_version", "2.0.0")),
    )


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
                changed_properties=dict(value.get("changed_properties") or {}),
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
                changed_properties=dict(value.get("changed_properties") or {}),
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
                changed_properties=dict(value.get("changed_properties") or {}),
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
        raise ValueError(f"unsupported semantic record type: {record_type!r}")


class ActionTreeSemanticReplay:
    """Rebuild a semantic store from the exact records linked by an action tree."""

    ORDER = ("observation", "encounter", "match_proposal", "recognition_account", "evidence")

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
