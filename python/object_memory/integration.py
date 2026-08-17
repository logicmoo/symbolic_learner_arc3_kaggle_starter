from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Mapping

from .learning import (
    GameLearningPipeline,
    LearningStepResult,
    TransformationCandidate,
    TransformationLearner,
    TransitionAnalyzer,
    TransitionRecord,
)
from .models import ExecutionMode, NormalizedResult
from .store import SymbolicStore


GAME_OBJECT_LEARNER_SCHEMA_VERSION = "1.0.0"


def _plain(value: Any) -> Any:
    if is_dataclass(value):
        return _plain(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(item) for item in value]
    return value


@dataclass(frozen=True)
class GameObjectLearnerPayload:
    state_id: str
    objects: tuple[Mapping[str, Any], ...]
    correspondences: tuple[Mapping[str, Any], ...] = ()
    transitions: tuple[Mapping[str, Any], ...] = ()
    provenance: tuple[str, ...] = ()
    observation_id: str | None = None
    encounter_ids: tuple[str, ...] = ()
    artifacts: tuple[Mapping[str, Any], ...] = ()
    evidence: tuple[Mapping[str, Any], ...] = ()
    schema_version: str = GAME_OBJECT_LEARNER_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return _plain(self)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "GameObjectLearnerPayload":
        return cls(
            state_id=str(value["state_id"]),
            objects=tuple(dict(item) for item in value.get("objects") or ()),
            correspondences=tuple(
                dict(item) for item in value.get("correspondences") or ()
            ),
            transitions=tuple(dict(item) for item in value.get("transitions") or ()),
            provenance=tuple(str(item) for item in value.get("provenance") or ()),
            observation_id=value.get("observation_id"),
            encounter_ids=tuple(str(item) for item in value.get("encounter_ids") or ()),
            artifacts=tuple(dict(item) for item in value.get("artifacts") or ()),
            evidence=tuple(dict(item) for item in value.get("evidence") or ()),
            schema_version=str(
                value.get("schema_version", GAME_OBJECT_LEARNER_SCHEMA_VERSION)
            ),
        )


@dataclass(frozen=True)
class GameObjectLearnerResult:
    state_id: str
    learning_step: LearningStepResult | None = None
    prediction_id: str | None = None
    recommendation: Any = None


class IntegrationError(ValueError):
    pass


class GameObjectLearnerSchema:
    """Small stable contract; providers may add metadata without changing it."""

    required_object_fields = frozenset({"id"})
    version = GAME_OBJECT_LEARNER_SCHEMA_VERSION


class IntegrationValidator:
    def __init__(self, schema: GameObjectLearnerSchema | None = None) -> None:
        self.schema = schema or GameObjectLearnerSchema()

    def validate(self, payload: GameObjectLearnerPayload) -> GameObjectLearnerPayload:
        if not payload.state_id:
            raise IntegrationError("state_id is required")
        if payload.schema_version != self.schema.version:
            raise IntegrationError(
                f"unsupported learner payload schema: {payload.schema_version!r}"
            )
        seen: set[str] = set()
        for item in payload.objects:
            missing = self.schema.required_object_fields.difference(item)
            if missing:
                raise IntegrationError(f"object is missing fields: {sorted(missing)}")
            object_id = str(item["id"])
            if object_id in seen:
                raise IntegrationError(f"duplicate object id: {object_id}")
            seen.add(object_id)
        encounter_ids = set(payload.encounter_ids)
        evidence_ids = {str(item.get("evidence_id")) for item in payload.evidence}
        artifact_ids = {str(item.get("artifact_id")) for item in payload.artifacts}
        for item in payload.objects:
            encounter_id = item.get("encounter_id")
            if encounter_id is not None and str(encounter_id) not in encounter_ids:
                raise IntegrationError(
                    f"object references missing encounter: {encounter_id}"
                )
            for evidence_id in item.get("evidence_ids") or ():
                if str(evidence_id) not in evidence_ids:
                    raise IntegrationError(
                        f"object references missing evidence: {evidence_id}"
                    )
            for artifact_id in item.get("turtle_artifact_ids") or ():
                if str(artifact_id) not in artifact_ids:
                    raise IntegrationError(
                        f"object references missing Turtle artifact: {artifact_id}"
                    )
        for item in payload.correspondences:
            for evidence_id in item.get("evidence_ids") or ():
                if str(evidence_id) not in evidence_ids:
                    raise IntegrationError(
                        f"correspondence references missing evidence: {evidence_id}"
                    )
        return payload


class Phase2LearnerPayloadBuilder:
    """Build the frozen learner handoff exclusively from exact Phase 2 records."""

    def __init__(self, store: SymbolicStore) -> None:
        self.store = store

    def for_observation(self, observation_id: str) -> GameObjectLearnerPayload:
        observation = self.store.get("observations", observation_id)
        if observation is None:
            raise KeyError(observation_id)
        encounters = tuple(
            item
            for item in self.store.encounters.records()
            if item.observation_id == observation_id
        )
        candidate_ids = {
            item.candidate_identity_id
            for item in encounters
            if item.candidate_identity_id is not None
        }
        identity_ids = {
            item.object_identity_id
            for item in encounters
            if item.object_identity_id is not None
        }
        proposals = tuple(
            item
            for item in self.store.values("match_proposals")
            if item.candidate_id in candidate_ids
        )
        changes = tuple(
            item
            for item in self.store.values("object_changes")
            if candidate_ids.intersection(item.after_candidate_ids)
            or identity_ids.intersection(item.before_identity_ids)
        )
        evidence_ids = {
            evidence_id
            for encounter in encounters
            for evidence_id in encounter.evidence_ids
        }
        evidence_ids.update(
            evidence_id for proposal in proposals for evidence_id in proposal.evidence_ids
        )
        evidence_ids.update(
            evidence_id for change in changes for evidence_id in change.evidence_ids
        )
        evidence = tuple(
            item
            for evidence_id in sorted(evidence_ids)
            if (item := self.store.get("evidence", evidence_id)) is not None
        )
        artifacts = {
            artifact.artifact_id: artifact for artifact in observation.artifacts
        }
        for encounter in encounters:
            for turtle in encounter.turtle_programs:
                artifacts[turtle.artifact.artifact_id] = turtle.artifact
            for artifact in encounter.reconstruction_artifacts:
                artifacts[artifact.artifact_id] = artifact
        objects = tuple(
            {
                "id": encounter.object_identity_id
                or encounter.candidate_identity_id
                or encounter.encounter_id,
                "encounter_id": encounter.encounter_id,
                "candidate_identity_id": encounter.candidate_identity_id,
                "object_identity_id": encounter.object_identity_id,
                "instance": _plain(encounter.instance),
                "relationships": _plain(encounter.instance.relationships),
                "matched_properties": list(encounter.matched_properties),
                "changed_properties": _plain(encounter.changed_properties),
                "residual_ids": list(encounter.residual_ids),
                "turtle_artifact_ids": [
                    turtle.artifact.artifact_id
                    for turtle in encounter.turtle_programs
                ],
                "evidence_ids": list(encounter.evidence_ids),
                "confidence": encounter.confidence,
                "provenance": [_plain(item) for item in encounter.provenance],
            }
            for encounter in encounters
        )
        payload = GameObjectLearnerPayload(
            state_id=observation_id,
            observation_id=observation_id,
            encounter_ids=tuple(item.encounter_id for item in encounters),
            objects=objects,
            correspondences=tuple(_plain(item) for item in proposals),
            transitions=tuple(_plain(item) for item in changes),
            artifacts=tuple(_plain(artifacts[key]) for key in sorted(artifacts)),
            evidence=tuple(_plain(item) for item in evidence),
            provenance=tuple(
                dict.fromkeys(
                    source.source_id
                    for source in (
                        *observation.provenance,
                        *(source for encounter in encounters for source in encounter.provenance),
                        *(source for proposal in proposals for source in proposal.provenance),
                        *(item.source for item in evidence),
                    )
                )
            ),
        )
        return IntegrationValidator().validate(payload)


def phase2_transition_analyzer() -> TransitionAnalyzer:
    """Analyze one real handoff using the direct Phase 2 change records."""

    def analyze(
        before: GameObjectLearnerPayload,
        action_or_event: Any,
        after: GameObjectLearnerPayload,
    ) -> TransitionRecord:
        IntegrationValidator().validate(before)
        IntegrationValidator().validate(after)
        return TransitionRecord(
            before_state_id=before.state_id,
            action_or_event=_plain(action_or_event),
            after_state_id=after.state_id,
            changes=after.transitions,
            provenance=tuple(dict.fromkeys((*before.provenance, *after.provenance))),
        )

    return TransitionAnalyzer(analyze)


def phase2_transformation_learner() -> TransformationLearner:
    """Convert every persisted direct change into an evidence-linked candidate."""

    def learn(transition: TransitionRecord):
        for change in transition.changes:
            plain = _plain(change)
            encoded = json.dumps(
                plain, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
            yield TransformationCandidate(
                candidate_id=f"transformation-{sha256(encoded).hexdigest()}",
                transformation=plain,
                evidence=tuple(str(item) for item in plain.get("evidence_ids") or ()),
                score=1.0,
            )

    return TransformationLearner(learn)


class GameObjectLearnerPlugin(ABC):
    """Phase 3 boundary; implementations consume normalized Phase 2 results."""

    @abstractmethod
    def consume_state(self, payload: GameObjectLearnerPayload) -> NormalizedResult:
        raise NotImplementedError

    @abstractmethod
    def consume_transition(
        self,
        before: GameObjectLearnerPayload,
        action_or_event: Any,
        after: GameObjectLearnerPayload,
    ) -> NormalizedResult:
        raise NotImplementedError

    def consume(self, payload: GameObjectLearnerPayload) -> NormalizedResult:
        """Backward-compatible alias for earlier single-state plugins."""
        return self.consume_state(payload)


class PipelineGameObjectLearnerPlugin(GameObjectLearnerPlugin):
    """Runnable integration of validated payloads with GameLearningPipeline."""

    def __init__(
        self,
        pipeline: GameLearningPipeline,
        *,
        mode: ExecutionMode = ExecutionMode.PYTHON,
        validator: IntegrationValidator | None = None,
    ) -> None:
        self.pipeline = pipeline
        self.mode = mode
        self.validator = validator or IntegrationValidator()

    def consume_state(self, payload: GameObjectLearnerPayload) -> NormalizedResult:
        valid = self.validator.validate(payload)
        return NormalizedResult(
            value=GameObjectLearnerResult(state_id=valid.state_id),
            mode=self.mode,
            source_refs=valid.provenance,
        )

    def consume_transition(
        self,
        before: GameObjectLearnerPayload,
        action_or_event: Any,
        after: GameObjectLearnerPayload,
    ) -> NormalizedResult:
        valid_before = self.validator.validate(before)
        valid_after = self.validator.validate(after)
        learning_step = self.pipeline.learn_transition(
            valid_before,
            action_or_event,
            valid_after,
        )
        return NormalizedResult(
            value=GameObjectLearnerResult(
                state_id=valid_after.state_id,
                learning_step=learning_step,
            ),
            mode=self.mode,
            source_refs=(*valid_before.provenance, *valid_after.provenance),
        )
