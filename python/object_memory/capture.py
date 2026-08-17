from __future__ import annotations

from dataclasses import asdict, is_dataclass
from enum import Enum
from hashlib import sha256
from pathlib import Path
import json
from typing import Any, Callable, Mapping

from .adapters import GridAdapter
from .models import ArtifactRef, EncounterRecord, InstanceParameters, TurtleProgramRef
from .recognition import EncounterChangeSession, RecognitionSession
from .store import InMemorySemanticBackend, SymbolicStore


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


class SemanticGridCaptureObserver:
    """External Arc3Runner observer that persists normalized Phase 2 records."""

    def __init__(
        self,
        adapter: GridAdapter,
        grid_selector: Callable[[Any], Any],
        symbolic_store: SymbolicStore | None = None,
    ) -> None:
        self.adapter = adapter
        self.grid_selector = grid_selector
        self.symbolic_store = symbolic_store or SymbolicStore(InMemorySemanticBackend())
        self.recognition = RecognitionSession(self.symbolic_store)
        self.changes = EncounterChangeSession(self.symbolic_store)
        self._latest_by_candidate: dict[str, str] = {}
        self._latest_observation_id: str | None = None

    @staticmethod
    def _write_record(path: Path, value: Any) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        source = json.dumps(_jsonable(value), indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        if path.exists() and path.read_text(encoding="utf-8") != source:
            raise RuntimeError(f"Semantic record conflict at {path}")
        path.write_text(source, encoding="utf-8")
        return path

    def on_state_captured(
        self,
        *,
        runner: Any,
        store: Any,
        node: Any,
        previous_node: Any,
        action: str | None,
        data: Mapping[str, Any],
    ) -> None:
        del previous_node
        relative_node = node.path.resolve().relative_to(store.level_root.resolve()).as_posix()
        source_id = f"{store.game_id}:{store.level}:{relative_node or 'initial'}"
        batch = self.adapter.normalize(
            observation_id=source_id,
            grid=self.grid_selector(runner),
            action_tree_node=str(node.path),
            artifact_uri=str(node.state_path),
        )
        semantic_dir = node.path / "semantic"
        observation_path = self._write_record(
            semantic_dir / f"{batch.observation.observation_id}.observation.json",
            batch.observation,
        )
        self.symbolic_store.put_observation(batch.observation)
        store.link_semantic_record(
            node,
            record_type="observation",
            record_id=batch.observation.observation_id,
            artifact_path=observation_path,
            schema_version=batch.observation.schema_version,
            deterministic_hash=batch.observation.observation_id.rsplit("-", 1)[-1],
        )

        for candidate in batch.candidates:
            details = batch.extractor_details[candidate.candidate_id]
            turtle_path = semantic_dir / f"{candidate.candidate_id}.turtle.pl"
            turtle_source = str(details.get("turtleProgram") or "")
            turtle_path.parent.mkdir(parents=True, exist_ok=True)
            if turtle_path.exists() and turtle_path.read_text(encoding="utf-8") != turtle_source:
                raise RuntimeError(f"Turtle artifact conflict at {turtle_path}")
            turtle_path.write_text(turtle_source, encoding="utf-8")
            turtle_artifact = ArtifactRef.create(
                artifact_type="turtle_program",
                uri=str(turtle_path),
                content_hash=f"sha256:{sha256(turtle_source.encode('utf-8')).hexdigest()}",
                provenance=batch.observation.provenance,
            )
            bounds = tuple(details.get("bounds") or (0, 0, 1, 1))
            origin_x, origin_y = float(bounds[0]), float(bounds[1])
            geometry = details.get("geometry") or {}
            topology = details.get("topology") or {}
            normalized_geometry = {
                "width": geometry.get("width"),
                "height": geometry.get("height"),
                "boundary_cells": tuple(
                    (float(cell[0]) - origin_x, float(cell[1]) - origin_y)
                    for cell in geometry.get("boundaryCells") or ()
                ),
                "line_thickness": details.get("lineThickness"),
            }
            normalized_topology = {
                "connected_components": topology.get("connectedComponents"),
                "hole_count": topology.get("holeCount"),
                "holes": tuple(
                    tuple(
                        (float(cell[0]) - origin_x, float(cell[1]) - origin_y)
                        for cell in hole
                    )
                    for hole in topology.get("holes") or ()
                ),
            }
            encounter = EncounterRecord.create(
                observation_id=batch.observation.observation_id,
                action_tree_node=str(node.path),
                candidate_identity_id=candidate.candidate_id,
                instance=InstanceParameters(
                    position=(float(bounds[0]), float(bounds[1])),
                    scale=(float(bounds[2]), float(bounds[3])),
                    appearance={
                        "color": details.get("colorName"),
                        "shape": details.get("shape"),
                    },
                    supported_transformations=("translation", "recolor"),
                    geometry=normalized_geometry,
                    topology=normalized_topology,
                ),
                turtle_programs=(TurtleProgramRef(turtle_artifact),),
                previous_encounter_id=self._latest_by_candidate.get(candidate.candidate_id),
                matched_properties=tuple(
                    item for item in ("color", "shape") if details.get(item if item != "color" else "colorName") is not None
                ),
                provenance=batch.observation.provenance,
                changed_properties={"action": action, "action_data": dict(data)},
            )
            self.symbolic_store.put_encounter(encounter)
            self._latest_by_candidate[candidate.candidate_id] = encounter.encounter_id
            encounter_path = self._write_record(
                semantic_dir / f"{encounter.encounter_id}.encounter.json",
                encounter,
            )
            store.link_semantic_record(
                node,
                record_type="encounter",
                record_id=encounter.encounter_id,
                artifact_path=encounter_path,
                schema_version=encounter.schema_version,
                deterministic_hash=encounter.deterministic_hash,
            )
            if self.recognition.latest_known_instances():
                proposals = self.recognition.propose(encounter.encounter_id)
                for proposal in proposals:
                    proposal_path = self._write_record(
                        semantic_dir / f"{proposal.proposal_id}.match-proposal.json",
                        proposal,
                    )
                    store.link_semantic_record(
                        node,
                        record_type="match_proposal",
                        record_id=proposal.proposal_id,
                        artifact_path=proposal_path,
                        schema_version=proposal.schema_version,
                        deterministic_hash=proposal.proposal_id.rsplit("-", 1)[-1],
                    )
                    for evidence_id in proposal.evidence_ids:
                        evidence = self.symbolic_store.get("evidence", evidence_id)
                        if evidence is None:
                            continue
                        evidence_path = self._write_record(
                            semantic_dir / f"{evidence.evidence_id}.evidence.json",
                            evidence,
                        )
                        store.link_semantic_record(
                            node,
                            record_type="evidence",
                            record_id=evidence.evidence_id,
                            artifact_path=evidence_path,
                            schema_version=evidence.schema_version,
                            deterministic_hash=evidence.evidence_id.rsplit("-", 1)[-1],
                        )
                account = self.recognition.unresolved_account(candidate.candidate_id)
                if account is not None:
                    account_path = self._write_record(
                        semantic_dir / f"{account.account_id}.recognition-account.json",
                        account,
                    )
                    store.link_semantic_record(
                        node,
                        record_type="recognition_account",
                        record_id=account.account_id,
                        artifact_path=account_path,
                        schema_version=account.schema_version,
                        deterministic_hash=account.account_id.rsplit("-", 1)[-1],
                    )
        if self._latest_observation_id is not None:
            proposals, changes, residuals = self.changes.detect(
                self._latest_observation_id,
                batch.observation.observation_id,
            )
            for proposal in proposals:
                proposal_path = self._write_record(
                    semantic_dir / f"{proposal.proposal_id}.match-proposal.json",
                    proposal,
                )
                store.link_semantic_record(
                    node,
                    record_type="match_proposal",
                    record_id=proposal.proposal_id,
                    artifact_path=proposal_path,
                    schema_version=proposal.schema_version,
                    deterministic_hash=proposal.proposal_id.rsplit("-", 1)[-1],
                )
                for evidence_id in proposal.evidence_ids:
                    evidence = self.symbolic_store.get("evidence", evidence_id)
                    if evidence is None:
                        continue
                    evidence_path = self._write_record(
                        semantic_dir / f"{evidence.evidence_id}.evidence.json",
                        evidence,
                    )
                    store.link_semantic_record(
                        node,
                        record_type="evidence",
                        record_id=evidence.evidence_id,
                        artifact_path=evidence_path,
                        schema_version=evidence.schema_version,
                        deterministic_hash=evidence.evidence_id.rsplit("-", 1)[-1],
                    )
            for change in changes:
                change_path = self._write_record(
                    semantic_dir / f"{change.change_id}.object-change.json",
                    change,
                )
                store.link_semantic_record(
                    node,
                    record_type="object_change",
                    record_id=change.change_id,
                    artifact_path=change_path,
                    schema_version=change.schema_version,
                    deterministic_hash=change.change_id.rsplit("-", 1)[-1],
                )
            for residual in residuals:
                residual_path = self._write_record(
                    semantic_dir / f"{residual.residual_id}.residual.json",
                    residual,
                )
                store.link_semantic_record(
                    node,
                    record_type="residual",
                    record_id=residual.residual_id,
                    artifact_path=residual_path,
                    schema_version="2.0.0",
                    deterministic_hash=residual.residual_id.rsplit("-", 1)[-1],
                )
        self._latest_observation_id = batch.observation.observation_id
