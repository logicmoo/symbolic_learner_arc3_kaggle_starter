from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, Sequence

from .models import (
    EvidencePolarity,
    EvidenceRecord,
    PredictionGradeRecord,
    PredictionRecord,
    ProvenanceRef,
    TransitionRule,
)
from .prediction import PredictionLedger, RuleStore


@dataclass(frozen=True)
class TransitionRecord:
    before_state_id: str
    action_or_event: Any
    after_state_id: str
    changes: tuple[Any, ...]
    provenance: tuple[str, ...] = ()


@dataclass(frozen=True)
class TransformationCandidate:
    candidate_id: str
    transformation: Any
    evidence: tuple[Any, ...] = ()
    score: float = 0.0
    source_state_id: str | None = None
    target_state_id: str | None = None
    action_or_event: Any = None
    assumptions: tuple[str, ...] = ()
    critiques: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()


@dataclass(frozen=True)
class RuleEvidence:
    rule_id: str
    confirming: tuple[Any, ...] = ()
    refuting: tuple[Any, ...] = ()


@dataclass(frozen=True)
class RuleRivalSet:
    rules: tuple[TransitionRule, ...]


@dataclass(frozen=True)
class PredictionGrade:
    score: float
    evidence: tuple[Any, ...] = ()


class TransitionAnalyzer:
    """Facade over a deterministic, Prolog, or GPT-backed transition analyzer."""

    def __init__(
        self,
        analyze: Callable[[Any, Any, Any], TransitionRecord],
    ) -> None:
        self._analyze = analyze

    def analyze(self, before: Any, action_or_event: Any, after: Any) -> TransitionRecord:
        return self._analyze(before, action_or_event, after)


class TransformationLearner:
    """Delegates candidate generation without fixing the learning algorithm."""

    def __init__(
        self,
        learn: Callable[[TransitionRecord], Iterable[TransformationCandidate]],
    ) -> None:
        self._learn = learn

    def learn(self, transition: TransitionRecord) -> tuple[TransformationCandidate, ...]:
        return tuple(self._learn(transition))


class RuleInducer:
    """Converts transformation candidates into normalized TransitionRule records."""

    def __init__(
        self,
        induce: Callable[[Sequence[TransformationCandidate]], Iterable[TransitionRule]],
    ) -> None:
        self._induce = induce

    def induce(
        self,
        candidates: Sequence[TransformationCandidate],
    ) -> tuple[TransitionRule, ...]:
        return tuple(self._induce(candidates))


class RuleRanker:
    def __init__(self, score: Callable[[TransitionRule], float]) -> None:
        self._score = score

    def rank(self, rules: Iterable[TransitionRule]) -> tuple[TransitionRule, ...]:
        return tuple(sorted(rules, key=self._score, reverse=True))


class RuleExecutor:
    """Applies stored rules through caller-supplied domain semantics."""

    def __init__(
        self,
        store: RuleStore,
        checker: Callable[[TransitionRule, Any], bool],
        executor: Callable[[TransitionRule, Any], Any],
    ) -> None:
        self.store = store
        self._checker = checker
        self._executor = executor

    def applicable(self, rule_id: str, state: Any) -> bool:
        return self.store.applicable(rule_id, state, self._checker)

    def apply(self, rule_id: str, state: Any) -> Any:
        if not self.applicable(rule_id, state):
            raise ValueError(f"Rule {rule_id!r} is not applicable")
        return self.store.apply(rule_id, state, self._executor)


class OutcomeChannel:
    """Independent observation channel used to grade a prior prediction."""

    def __init__(self, read: Callable[[], Any]) -> None:
        self._read = read

    def read(self) -> Any:
        return self._read()


class PredictionEvaluator:
    def __init__(
        self,
        compare: Callable[[Any, Any], PredictionGrade],
    ) -> None:
        self._compare = compare

    def evaluate(self, predicted: Any, observed: Any) -> PredictionGrade:
        return self._compare(predicted, observed)


@dataclass(frozen=True)
class LearningStepResult:
    transition: TransitionRecord
    candidates: tuple[TransformationCandidate, ...]
    rules: tuple[TransitionRule, ...]


class GameLearningPipeline:
    """Connected Phase 3 flow; algorithms remain replaceable providers."""

    def __init__(
        self,
        transition_analyzer: TransitionAnalyzer,
        transformation_learner: TransformationLearner,
        rule_inducer: RuleInducer,
        rule_ranker: RuleRanker,
        rule_store: RuleStore,
        prediction_ledger: PredictionLedger,
        semantic_store: Any | None = None,
    ) -> None:
        self.transition_analyzer = transition_analyzer
        self.transformation_learner = transformation_learner
        self.rule_inducer = rule_inducer
        self.rule_ranker = rule_ranker
        self.rule_store = rule_store
        self.prediction_ledger = prediction_ledger
        self.semantic_store = semantic_store

    def learn_transition(
        self,
        before: Any,
        action_or_event: Any,
        after: Any,
    ) -> LearningStepResult:
        transition = self.transition_analyzer.analyze(before, action_or_event, after)
        candidates = self.transformation_learner.learn(transition)
        rules = self.rule_ranker.rank(self.rule_inducer.induce(candidates))
        for rule in rules:
            self.rule_store.store(rule)
        return LearningStepResult(transition, candidates, rules)

    def predict(
        self,
        *,
        prediction_id: str,
        rule_id: str,
        source_state_id: str,
        state: Any,
        created_sequence: int,
        executor: RuleExecutor,
    ) -> tuple[Any, PredictionRecord]:
        predicted_state = executor.apply(rule_id, state)
        rule = self.rule_store.get(rule_id)
        record = PredictionRecord(
            prediction_id=prediction_id,
            rule_id=rule_id,
            source_state_id=source_state_id,
            predicted_effects=(predicted_state,),
            created_sequence=created_sequence,
            available_evidence_ids=tuple(
                dict.fromkeys(
                    (
                        *rule.supporting_evidence_ids,
                        *rule.contradicting_evidence_ids,
                    )
                )
            ),
            rule_assumptions=rule.assumptions,
            rule_critiques=rule.critiques,
            rule_probability=(
                rule.calibrated_probability
                if rule.calibrated_probability is not None
                else rule.bootstrap_probability
            ),
            rule_probability_source=rule.probability_source,
        )
        stored = self.prediction_ledger.record(record)
        if self.semantic_store is not None:
            self.semantic_store.put_prediction(stored)
        return predicted_state, stored

    def grade_prediction(
        self,
        *,
        prediction_id: str,
        outcome_sequence: int,
        outcome_channel: OutcomeChannel,
        evaluator: PredictionEvaluator,
    ) -> PredictionRecord:
        prediction = self.prediction_ledger.get(prediction_id)
        predicted = prediction.predicted_effects[0]
        observed = outcome_channel.read()
        grade = evaluator.evaluate(predicted, observed)
        closed = self.prediction_ledger.grade(
            prediction_id,
            outcome_sequence=outcome_sequence,
            outcome=observed,
            grade=grade.score,
        )
        prior_probability = self.rule_store.get(prediction.rule_id).calibrated_probability
        evidence_records: list[EvidenceRecord] = []
        source = ProvenanceRef.create(
            source_id=prediction_id,
            provider="prediction_evaluator",
            sequence=outcome_sequence,
            metadata={"evaluator_evidence": list(grade.evidence)},
        )
        evidence_detail = {
            "prediction_id": prediction_id,
            "expected": predicted,
            "observed": observed,
            "grade": grade.score,
        }
        if grade.score > 0.0:
            evidence_records.append(
                EvidenceRecord.create(
                    subject_id=prediction.rule_id,
                    polarity=EvidencePolarity.SUPPORTS,
                    source=source,
                    weight=grade.score,
                    detail=evidence_detail,
                    created_sequence=outcome_sequence,
                )
            )
        if grade.score < 1.0:
            evidence_records.append(
                EvidenceRecord.create(
                    subject_id=prediction.rule_id,
                    polarity=EvidencePolarity.CONTRADICTS,
                    source=source,
                    weight=1.0 - grade.score,
                    detail=evidence_detail,
                    created_sequence=outcome_sequence,
                )
            )
        supporting_ids = tuple(
            record.evidence_id
            for record in evidence_records
            if record.polarity is EvidencePolarity.SUPPORTS
        )
        contradicting_ids = tuple(
            record.evidence_id
            for record in evidence_records
            if record.polarity is EvidencePolarity.CONTRADICTS
        )
        refined = self.rule_store.record_prediction_grade(
            prediction.rule_id,
            prediction_id=prediction_id,
            grade=grade.score,
            supporting_evidence_ids=supporting_ids,
            contradicting_evidence_ids=contradicting_ids,
        )
        if self.semantic_store is not None:
            for evidence_record in evidence_records:
                self.semantic_store.put_evidence(evidence_record)
            self.semantic_store.put_prediction_grade(
                PredictionGradeRecord(
                    prediction_id=prediction_id,
                    rule_id=prediction.rule_id,
                    outcome_sequence=outcome_sequence,
                    outcome=observed,
                    grade=grade.score,
                    evidence=grade.evidence,
                    evidence_record_ids=tuple(
                        record.evidence_id for record in evidence_records
                    ),
                    prior_probability=prior_probability,
                    calibrated_probability=refined.calibrated_probability,
                )
            )
        return closed
