from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Mapping

from .learning import GameLearningPipeline, LearningStepResult
from .models import ExecutionMode, NormalizedResult


@dataclass(frozen=True)
class GameObjectLearnerPayload:
    state_id: str
    objects: tuple[Mapping[str, Any], ...]
    correspondences: tuple[Mapping[str, Any], ...] = ()
    transitions: tuple[Mapping[str, Any], ...] = ()
    provenance: tuple[str, ...] = ()


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


class IntegrationValidator:
    def __init__(self, schema: GameObjectLearnerSchema | None = None) -> None:
        self.schema = schema or GameObjectLearnerSchema()

    def validate(self, payload: GameObjectLearnerPayload) -> GameObjectLearnerPayload:
        if not payload.state_id:
            raise IntegrationError("state_id is required")
        seen: set[str] = set()
        for item in payload.objects:
            missing = self.schema.required_object_fields.difference(item)
            if missing:
                raise IntegrationError(f"object is missing fields: {sorted(missing)}")
            object_id = str(item["id"])
            if object_id in seen:
                raise IntegrationError(f"duplicate object id: {object_id}")
            seen.add(object_id)
        return payload


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
