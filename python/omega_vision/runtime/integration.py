from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Mapping

from omega_vision.core.learning import (
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
from omega_vision.core.models import ExecutionMode, NormalizedResult, TransitionRule
from omega_vision.core.prediction import RuleStore
from omega_vision.core.store import SymbolicStore


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


def _numeric_difference(before: Any, after: Any) -> Any | None:
    if all(
        isinstance(item, (int, float)) and not isinstance(item, bool)
        for item in (before, after)
    ):
        return after - before
    if isinstance(before, (tuple, list)) and isinstance(after, (tuple, list)):
        if len(before) != len(after):
            return None
        values = [_numeric_difference(old, new) for old, new in zip(before, after)]
        if any(item is None for item in values):
            return None
        return values
    return None


def _numeric_ratio(before: Any, after: Any) -> Any | None:
    if all(
        isinstance(item, (int, float)) and not isinstance(item, bool)
        for item in (before, after)
    ):
        return None if before == 0 else after / before
    if isinstance(before, (tuple, list)) and isinstance(after, (tuple, list)):
        if len(before) != len(after):
            return None
        values = [_numeric_ratio(old, new) for old, new in zip(before, after)]
        if any(item is None for item in values):
            return None
        return values
    return None


def _set_edit(before: Any, after: Any) -> Mapping[str, Any] | None:
    if not isinstance(before, (tuple, list)) or not isinstance(after, (tuple, list)):
        return None
    if not all(isinstance(item, str) for item in (*before, *after)):
        return None
    removed = [item for item in before if item not in after]
    added = [item for item in after if item not in before]
    return {"remove": removed, "add": added} if removed or added else None


def _relationship_edit(before: Any, after: Any) -> Mapping[str, Any] | None:
    if not isinstance(before, (tuple, list)) or not isinstance(after, (tuple, list)):
        return None
    if not all(isinstance(item, Mapping) for item in (*before, *after)):
        return None

    def key(item: Mapping[str, Any]) -> str:
        return json.dumps(
            _plain(item), ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )

    before_by_key = {key(item): _plain(item) for item in before}
    after_by_key = {key(item): _plain(item) for item in after}
    removed = [before_by_key[item] for item in sorted(before_by_key.keys() - after_by_key)]
    added = [after_by_key[item] for item in sorted(after_by_key.keys() - before_by_key)]
    return {"remove": removed, "add": added} if removed or added else None


def _mapping_edit(before: Any, after: Any) -> Mapping[str, Any] | None:
    """Describe a structural mapping rewrite without replacing unrelated keys."""

    if not isinstance(before, Mapping) or not isinstance(after, Mapping):
        return None
    removed = sorted(str(key) for key in before.keys() - after.keys())
    added_or_replaced: dict[str, Any] = {}
    nested: dict[str, Mapping[str, Any]] = {}
    for key in sorted(after):
        name = str(key)
        if key not in before:
            added_or_replaced[name] = _plain(after[key])
            continue
        if before[key] == after[key]:
            continue
        child = _mapping_edit(before[key], after[key])
        if child is None:
            added_or_replaced[name] = _plain(after[key])
        else:
            nested[name] = child
    if not (removed or added_or_replaced or nested):
        return None
    return {"remove": removed, "set": added_or_replaced, "update": nested}


def _numeric_sum(left: Any, right: Any) -> Any | None:
    if all(
        isinstance(item, (int, float)) and not isinstance(item, bool)
        for item in (left, right)
    ):
        return left + right
    if isinstance(left, (tuple, list)) and isinstance(right, (tuple, list)):
        if len(left) != len(right):
            return None
        values = [_numeric_sum(a, b) for a, b in zip(left, right)]
        if any(item is None for item in values):
            return None
        return tuple(values) if isinstance(left, tuple) else values
    return None


def _apply_mapping_edit(current: Mapping[str, Any], edit: Mapping[str, Any]) -> dict[str, Any]:
    result = {str(key): _plain(value) for key, value in current.items()}
    for key in edit.get("remove") or ():
        result.pop(str(key), None)
    result.update({str(key): _plain(value) for key, value in (edit.get("set") or {}).items()})
    for key, child in (edit.get("update") or {}).items():
        name = str(key)
        if isinstance(child, Mapping) and isinstance(result.get(name), Mapping):
            result[name] = _apply_mapping_edit(result[name], child)
    return result


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
    def __init__(
        self,
        schema: GameObjectLearnerSchema | None = None,
        *,
        registry_identity_ids: set[str] | frozenset[str] | None = None,
        provenance_source_ids: set[str] | frozenset[str] | None = None,
    ) -> None:
        self.schema = schema or GameObjectLearnerSchema()
        self.registry_identity_ids = (
            None if registry_identity_ids is None else frozenset(registry_identity_ids)
        )
        self.provenance_source_ids = (
            None if provenance_source_ids is None else frozenset(provenance_source_ids)
        )

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
        if self.registry_identity_ids is not None:
            missing_identities = identity_ids.difference(self.registry_identity_ids)
            if missing_identities:
                raise IntegrationError(
                    "payload registry identities are absent from durable memory: "
                    f"{sorted(missing_identities)}"
                )
        if self.provenance_source_ids is not None:
            missing_sources = set(payload.provenance).difference(
                self.provenance_source_ids
            )
            if missing_sources:
                raise IntegrationError(
                    "payload provenance sources are absent from durable memory: "
                    f"{sorted(missing_sources)}"
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
        durable_identity_ids = {
            item.handle for item in self.store.values("atoms")
        }
        durable_identity_ids.update(
            item.object_identity_id
            for item in self.store.encounters.records()
            if item.object_identity_id is not None
        )
        durable_identity_ids.update(
            item.candidate_identity_id
            for item in self.store.encounters.records()
            if item.candidate_identity_id is not None
        )
        durable_provenance_ids: set[str] = set()

        def collect_durable_provenance(value: Any) -> None:
            if isinstance(value, Mapping):
                if "source_id" in value and "provider" in value:
                    durable_provenance_ids.add(str(value["source_id"]))
                for nested in value.values():
                    collect_durable_provenance(nested)
            elif isinstance(value, (tuple, list)):
                for nested in value:
                    collect_durable_provenance(nested)

        for values in self.store.snapshot().values():
            collect_durable_provenance(_plain(values))
        return IntegrationValidator(
            registry_identity_ids=durable_identity_ids,
            provenance_source_ids=durable_provenance_ids,
        ).validate(payload)


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
    """Convert direct changes into evidence-linked competing interpretations."""

    def learn(transition: TransitionRecord):
        for change in transition.changes:
            plain = _plain(change)
            interpretations = [
                (
                    {**plain, "interpretation": "absolute_target"},
                    ("observed_transition_is_representative",),
                    ("may_overfit_observed_coordinates",),
                )
            ]
            deltas = {
                str(field): difference
                for field, specification in (plain.get("properties") or {}).items()
                if isinstance(specification, Mapping)
                and "from" in specification
                and "to" in specification
                and (
                    difference := _numeric_difference(
                        specification["from"], specification["to"]
                    )
                )
                is not None
            }
            if deltas:
                interpretations.append(
                    (
                        {
                            **plain,
                            "interpretation": "relative_delta",
                            "deltas": deltas,
                        },
                        (
                            "observed_transition_is_representative",
                            "numeric_change_is_relative",
                        ),
                        ("relative_generalization_requires_validation",),
                    )
                )
            properties = plain.get("properties") or {}
            position_change = properties.get("position")
            if isinstance(position_change, Mapping) and "to" in position_change:
                for reference_field in ("reference_position", "anchor_position"):
                    reference_change = properties.get(reference_field)
                    if not isinstance(reference_change, Mapping) or "to" not in reference_change:
                        continue
                    offset = _numeric_difference(
                        reference_change["to"], position_change["to"]
                    )
                    if offset is not None:
                        interpretations.append(
                            (
                                {
                                    **plain,
                                    "interpretation": "object_relative_position",
                                    "target_field": "position",
                                    "reference_field": reference_field,
                                    "offset": offset,
                                },
                                ("reference_identity_is_stable",),
                                ("reference_position_requires_identity_validation",),
                            )
                        )
                        break
            if str(plain.get("kind", "")).lower() in {"scaled", "resized", "scale_changed"}:
                factors = {
                    str(field): ratio
                    for field, specification in (plain.get("properties") or {}).items()
                    if isinstance(specification, Mapping)
                    and "from" in specification
                    and "to" in specification
                    and (ratio := _numeric_ratio(specification["from"], specification["to"]))
                    is not None
                }
                if factors:
                    interpretations.append(
                        (
                            {**plain, "interpretation": "multiplicative_scale", "factors": factors},
                            ("numeric_change_is_proportional",),
                            ("scale_factor_requires_validation",),
                        )
                    )
            toggles = tuple(
                str(field)
                for field, specification in (plain.get("properties") or {}).items()
                if isinstance(specification, Mapping)
                and isinstance(specification.get("from"), bool)
                and isinstance(specification.get("to"), bool)
                and specification["from"] is not specification["to"]
            )
            if toggles:
                interpretations.append(
                    (
                        {**plain, "interpretation": "boolean_toggle", "toggle_fields": toggles},
                        ("boolean_change_is_a_toggle",),
                        ("toggle_generalization_requires_validation",),
                    )
                )
            edits = {
                str(field): edit
                for field, specification in (plain.get("properties") or {}).items()
                if isinstance(specification, Mapping)
                and "from" in specification
                and "to" in specification
                and (edit := _set_edit(specification["from"], specification["to"]))
                is not None
            }
            if edits:
                interpretations.append(
                    (
                        {**plain, "interpretation": "set_edit", "set_edits": edits},
                        ("collection_change_is_membership_based",),
                        ("ordering_semantics_are_not_preserved",),
                    )
                )
            relationship_edits = {
                str(field): edit
                for field, specification in (plain.get("properties") or {}).items()
                if isinstance(specification, Mapping)
                and "from" in specification
                and "to" in specification
                and (
                    edit := _relationship_edit(
                        specification["from"], specification["to"]
                    )
                )
                is not None
            }
            if relationship_edits:
                interpretations.append(
                    (
                        {
                            **plain,
                            "interpretation": "relationship_edit",
                            "relationship_edits": relationship_edits,
                        },
                        ("relationship_change_is_symbolic",),
                        ("relationship_targets_require_identity_validation",),
                    )
                )
            topology_edits = {
                str(field): edit
                for field, specification in properties.items()
                if "topology" in str(field).lower()
                and isinstance(specification, Mapping)
                and "from" in specification
                and "to" in specification
                and (
                    edit := _mapping_edit(
                        specification["from"], specification["to"]
                    )
                )
                is not None
            }
            if topology_edits:
                interpretations.append(
                    (
                        {
                            **plain,
                            "interpretation": "structural_topology_rewrite",
                            "topology_edits": topology_edits,
                        },
                        ("topology_change_is_structural",),
                        ("unobserved_topology_keys_are_preserved",),
                    )
                )
            for interpretation, assumptions, critiques in interpretations:
                encoded = json.dumps(
                    interpretation,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
                yield TransformationCandidate(
                    candidate_id=f"transformation-{sha256(encoded).hexdigest()}",
                    transformation=interpretation,
                    evidence=tuple(
                        str(item) for item in plain.get("evidence_ids") or ()
                    ),
                    score=1.0,
                    source_state_id=transition.before_state_id,
                    target_state_id=transition.after_state_id,
                    action_or_event=transition.action_or_event,
                    assumptions=assumptions,
                    critiques=critiques,
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

    def numeric_scale(factor: Any, current: Any) -> Any | None:
        if all(
            isinstance(item, (int, float)) and not isinstance(item, bool)
            for item in (factor, current)
        ):
            return current * factor
        if isinstance(factor, (tuple, list)) and isinstance(current, (tuple, list)):
            if len(factor) != len(current):
                return None
            values = [numeric_scale(scale, value) for scale, value in zip(factor, current)]
            if any(item is None for item in values):
                return None
            return tuple(values) if isinstance(current, tuple) else values
        return None

    def effect_properties(
        rule: TransitionRule,
    ) -> tuple[tuple[Mapping[str, Any], Mapping[str, Any]], ...]:
        return tuple(
            (effect, effect["properties"])
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
            field in state for _effect, group in properties for field in group
        )

    def execute(rule: TransitionRule, state: Any) -> dict[str, Any]:
        result = {str(key): _plain(value) for key, value in state.items()}
        for effect, properties in effect_properties(rule):
            for field, specification in properties.items():
                if not isinstance(specification, Mapping) or "to" not in specification:
                    continue
                replacement = _plain(specification["to"])
                interpretation = effect.get("interpretation")
                if interpretation == "relative_delta" and "from" in specification:
                    relative = numeric_delta(
                        specification["from"],
                        specification["to"],
                        result[field],
                    )
                    if relative is not None:
                        replacement = relative
                elif interpretation == "multiplicative_scale":
                    scaled = numeric_scale(
                        (effect.get("factors") or {}).get(field), result[field]
                    )
                    if scaled is not None:
                        replacement = scaled
                elif interpretation == "boolean_toggle" and field in (
                    effect.get("toggle_fields") or ()
                ):
                    replacement = not bool(result[field])
                elif interpretation == "set_edit":
                    edit = (effect.get("set_edits") or {}).get(field)
                    if isinstance(edit, Mapping) and isinstance(result[field], (tuple, list)):
                        values = [
                            item
                            for item in result[field]
                            if item not in (edit.get("remove") or ())
                        ]
                        values.extend(
                            item
                            for item in edit.get("add") or ()
                            if item not in values
                        )
                        replacement = tuple(values) if isinstance(result[field], tuple) else values
                elif interpretation == "relationship_edit":
                    edit = (effect.get("relationship_edits") or {}).get(field)
                    if isinstance(edit, Mapping) and isinstance(result[field], (tuple, list)):
                        removed = {
                            json.dumps(
                                _plain(item),
                                ensure_ascii=False,
                                sort_keys=True,
                                separators=(",", ":"),
                            )
                            for item in edit.get("remove") or ()
                        }
                        values = [
                            _plain(item)
                            for item in result[field]
                            if json.dumps(
                                _plain(item),
                                ensure_ascii=False,
                                sort_keys=True,
                                separators=(",", ":"),
                            )
                            not in removed
                        ]
                        for item in edit.get("add") or ():
                            plain_item = _plain(item)
                            if plain_item not in values:
                                values.append(plain_item)
                        replacement = tuple(values) if isinstance(result[field], tuple) else values
                elif interpretation == "object_relative_position":
                    target_field = str(effect.get("target_field") or field)
                    reference_field = str(effect.get("reference_field") or "")
                    if field != target_field:
                        continue
                    if reference_field in result:
                        relative = _numeric_sum(result[reference_field], effect.get("offset"))
                        if relative is not None:
                            replacement = relative
                elif interpretation == "structural_topology_rewrite":
                    edit = (effect.get("topology_edits") or {}).get(field)
                    if isinstance(edit, Mapping) and isinstance(result[field], Mapping):
                        replacement = _apply_mapping_edit(result[field], edit)
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
