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
    RuleInducer,
    RuleExecutor,
    RuleRanker,
)
from .models import ExecutionMode, NormalizedResult, TransitionRule
from .prediction import RuleStore
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
    identity_ids: tuple[str, ...] = ()
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
            identity_ids=tuple(str(item) for item in value.get("identity_ids") or ()),
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
        identity_ids = set(payload.identity_ids)
        evidence_ids = {str(item.get("evidence_id")) for item in payload.evidence}
        artifact_ids = {str(item.get("artifact_id")) for item in payload.artifacts}
        candidate_ids: set[str] = set()
        referenced_provenance_ids: set[str] = set()

        def collect_provenance(values: Any) -> None:
            if isinstance(values, Mapping):
                if "source_id" in values and "provider" in values:
                    referenced_provenance_ids.add(str(values["source_id"]))
                for nested in values.values():
                    collect_provenance(nested)
            elif isinstance(values, (tuple, list)):
                for nested in values:
                    collect_provenance(nested)

        for item in payload.objects:
            candidate_id = item.get("candidate_identity_id")
            if candidate_id is not None:
                candidate_ids.add(str(candidate_id))
            identity_id = item.get("object_identity_id")
            if identity_id is not None and str(identity_id) not in identity_ids:
                raise IntegrationError(
                    f"object references missing registry identity: {identity_id}"
                )
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
            collect_provenance(item.get("provenance") or ())
        for item in payload.correspondences:
            candidate_id = str(item.get("candidate_id"))
            if candidate_id not in candidate_ids:
                raise IntegrationError(
                    f"correspondence references missing candidate: {candidate_id}"
                )
            stored_identity_id = item.get("stored_identity_id")
            if (
                stored_identity_id is not None
                and str(stored_identity_id) not in identity_ids
            ):
                raise IntegrationError(
                    "correspondence references missing registry identity: "
                    f"{stored_identity_id}"
                )
            for evidence_id in item.get("evidence_ids") or ():
                if str(evidence_id) not in evidence_ids:
                    raise IntegrationError(
                        f"correspondence references missing evidence: {evidence_id}"
                    )
            collect_provenance(item.get("provenance") or ())
        for item in payload.transitions:
            for identity_id in item.get("before_identity_ids") or ():
                if str(identity_id) not in identity_ids:
                    raise IntegrationError(
                        f"transition references missing registry identity: {identity_id}"
                    )
            for candidate_id in item.get("after_candidate_ids") or ():
                if str(candidate_id) not in candidate_ids:
                    raise IntegrationError(
                        f"transition references missing candidate: {candidate_id}"
                    )
            for evidence_id in item.get("evidence_ids") or ():
                if str(evidence_id) not in evidence_ids:
                    raise IntegrationError(
                        f"transition references missing evidence: {evidence_id}"
                    )
            collect_provenance(item.get("provenance") or ())
        collect_provenance(payload.artifacts)
        collect_provenance(payload.evidence)
        missing_provenance = referenced_provenance_ids.difference(payload.provenance)
        if missing_provenance:
            raise IntegrationError(
                "records reference missing provenance sources: "
                f"{sorted(missing_provenance)}"
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
        identity_ids.update(
            item.stored_identity_id
            for item in proposals
            if item.stored_identity_id is not None
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
            identity_ids=tuple(sorted(identity_ids)),
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
                source_state_id=transition.before_state_id,
                target_state_id=transition.after_state_id,
                action_or_event=transition.action_or_event,
                assumptions=("observed_transition_is_representative",),
                critiques=("requires_unseen_case_validation",),
                provenance=transition.provenance,
            )

    return TransformationLearner(learn)


def phase2_rule_inducer() -> RuleInducer:
    """Induce inspectable rival rules without treating one observation as proof."""

    def rule_identity(candidate: TransformationCandidate) -> str:
        value = {
            "action_or_event": _plain(candidate.action_or_event),
            "transformation": _plain(candidate.transformation),
            "assumptions": candidate.assumptions,
        }
        encoded = json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        return f"rule-{sha256(encoded).hexdigest()}"

    def induce(candidates):
        rule_ids = tuple(rule_identity(candidate) for candidate in candidates)
        for candidate, rule_id in zip(candidates, rule_ids):
            change = candidate.transformation
            before_identities = tuple(
                str(item) for item in change.get("before_identity_ids") or ()
            )
            assumptions = tuple(
                dict.fromkeys(
                    (
                        *candidate.assumptions,
                        *(f"identity_present:{item}" for item in before_identities),
                    )
                )
            )
            critiques = list(candidate.critiques)
            if not candidate.evidence:
                critiques.append("missing_attributable_evidence")
            critiques.append("single_observation_bootstrap")
            critiques.append("contradiction_check_pending")
            yield TransitionRule(
                rule_id=rule_id,
                preconditions=before_identities,
                action_or_event=candidate.action_or_event,
                predicted_effects=(change,),
                provenance=candidate.provenance,
                assumptions=assumptions,
                critiques=tuple(dict.fromkeys(critiques)),
                supporting_evidence_ids=tuple(str(item) for item in candidate.evidence),
                rival_rule_ids=tuple(item for item in rule_ids if item != rule_id),
                bootstrap_probability=0.5 if candidate.evidence else 0.25,
                probability_source="bootstrap",
                coverage=1.0,
            )

    return RuleInducer(induce)


def phase2_rule_ranker() -> RuleRanker:
    """Rank by verified history first, then evidence and explicit simplicity."""

    def score(rule: TransitionRule) -> float:
        verified = rule.calibrated_probability or 0.0
        prediction_rate = (
            rule.prediction_score_total / rule.prediction_attempts
            if rule.prediction_attempts
            else 0.0
        )
        simplicity = 1.0 / (
            1.0 + len(rule.preconditions) + len(rule.predicted_effects)
        )
        applicability = rule.applicability_precision or 0.0
        return (
            verified * 8.0
            + prediction_rate * 4.0
            + rule.coverage
            + applicability * 2.0
            + len(rule.supporting_evidence_ids) * 0.25
            - len(rule.contradicting_evidence_ids) * 0.5
            + simplicity
            + rule.bootstrap_probability * 0.1
        )

    return RuleRanker(score)


def phase2_rule_executor(
    store: RuleStore,
    action_or_event: Any,
) -> RuleExecutor:
    """Apply an induced object transformation relative to a new object state.

    Numeric ``from``/``to`` observations describe a delta, not an absolute
    destination.  This lets a translation learned at one location operate on
    an unseen object at another location.  Non-numeric changes use their
    observed ``to`` value.  The caller still has to supply the action/event
    that selects the rule; execution never silently ignores that condition.
    """

    def numeric_delta(before: Any, after: Any, current: Any) -> Any | None:
        if all(
            isinstance(item, (int, float)) and not isinstance(item, bool)
            for item in (before, after, current)
        ):
            return current + (after - before)
        if all(isinstance(item, (tuple, list)) for item in (before, after, current)):
            if not (len(before) == len(after) == len(current)):
                return None
            values = [
                numeric_delta(old, new, present)
                for old, new, present in zip(before, after, current)
            ]
            if any(item is None for item in values):
                return None
            return tuple(values) if isinstance(current, tuple) else values
        return None

    def effect_properties(rule: TransitionRule) -> tuple[Mapping[str, Any], ...]:
        return tuple(
            effect.get("properties")
            for effect in rule.predicted_effects
            if isinstance(effect, Mapping)
            and isinstance(effect.get("properties"), Mapping)
        )

    def checker(rule: TransitionRule, state: Any) -> bool:
        if _plain(rule.action_or_event) != _plain(action_or_event):
            return False
        if not isinstance(state, Mapping):
            return False
        properties = effect_properties(rule)
        return bool(properties) and all(
            field in state for group in properties for field in group
        )

    def execute(rule: TransitionRule, state: Any) -> dict[str, Any]:
        result = {str(key): _plain(value) for key, value in state.items()}
        for properties in effect_properties(rule):
            for field, specification in properties.items():
                if not isinstance(specification, Mapping) or "to" not in specification:
                    continue
                replacement = _plain(specification["to"])
                if "from" in specification:
                    relative = numeric_delta(
                        specification["from"],
                        specification["to"],
                        result[field],
                    )
                    if relative is not None:
                        replacement = relative
                result[str(field)] = replacement
        return result

    return RuleExecutor(store, checker, execute)


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
