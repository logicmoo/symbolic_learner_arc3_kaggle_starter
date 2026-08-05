from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Protocol, Sequence
from uuid import uuid4


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mapping(value: Mapping[str, Any] | None) -> Mapping[str, Any]:
    return MappingProxyType(dict(value or {}))


class SiloStatus(str, Enum):
    OBSERVED = "observed"
    GENERATED = "generated"
    HYPOTHETICAL = "hypothetical"
    VALIDATED = "validated"
    REJECTED = "rejected"


@dataclass(frozen=True)
class ProducerRef:
    task: str
    implementation: str
    run_id: str | None = None


@dataclass(frozen=True)
class SiloRecord:
    """One immutable version of a named, typed information silo."""

    silo_id: str
    version: int
    semantic_type: str
    representation_type: str
    value: Any
    subject: str | None = None
    status: SiloStatus = SiloStatus.GENERATED
    confidence: float = 1.0
    produced_by: ProducerRef | None = None
    derived_from: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if not self.silo_id.strip():
            raise ValueError("silo_id must not be empty")
        if self.version < 1:
            raise ValueError("version must be at least 1")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        object.__setattr__(self, "metadata", _mapping(self.metadata))

    @property
    def reference(self) -> str:
        return f"{self.silo_id}:v{self.version}"


@dataclass(frozen=True)
class Observation:
    observation_id: str
    payload: Any
    source: str
    representation_type: str = "json_object"
    observed_at: str = field(default_factory=_now)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _mapping(self.metadata))


@dataclass(frozen=True)
class Intervention:
    """An action observed in or applied to an external world."""

    intervention_id: str
    actor: str
    action: str
    parameters: Mapping[str, Any] = field(default_factory=dict)
    observed_at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        object.__setattr__(self, "parameters", _mapping(self.parameters))


@dataclass(frozen=True)
class DemonstrationStep:
    """A before/action/after example observed from a human demonstrator."""

    step_id: str
    before_observation: str
    intervention: Intervention
    after_observation: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _mapping(self.metadata))


@dataclass(frozen=True)
class Goal:
    goal_id: str
    description: str
    criteria: Mapping[str, Any]
    priority: float = 1.0
    source: str = "supplied"

    def __post_init__(self) -> None:
        if not 0.0 <= self.priority <= 1.0:
            raise ValueError("goal priority must be between 0 and 1")
        object.__setattr__(self, "criteria", _mapping(self.criteria))


@dataclass(frozen=True)
class WorldModel:
    model_id: str
    revision: int
    state: Mapping[str, Any]
    entities: tuple[Any, ...] = ()
    dynamics: tuple[Any, ...] = ()
    evidence: tuple[str, ...] = ()
    confidence: float = 0.0

    def __post_init__(self) -> None:
        if self.revision < 1:
            raise ValueError("world-model revision must be at least 1")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("world-model confidence must be between 0 and 1")
        object.__setattr__(self, "state", _mapping(self.state))


@dataclass(frozen=True)
class SimulationRequest:
    simulation_id: str
    world_model_id: str
    goal_ids: tuple[str, ...]
    intervention: Mapping[str, Any]
    horizon: int = 1
    assumptions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.horizon < 1:
            raise ValueError("simulation horizon must be at least 1")
        object.__setattr__(self, "intervention", _mapping(self.intervention))


@dataclass(frozen=True)
class SimulationResult:
    simulation_id: str
    predicted_state: Mapping[str, Any]
    goal_scores: Mapping[str, float]
    evidence: tuple[str, ...] = ()
    confidence: float = 0.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("simulation confidence must be between 0 and 1")
        scores = dict(self.goal_scores)
        if any(not 0.0 <= score <= 1.0 for score in scores.values()):
            raise ValueError("goal scores must be between 0 and 1")
        object.__setattr__(self, "predicted_state", _mapping(self.predicted_state))
        object.__setattr__(self, "goal_scores", MappingProxyType(scores))


class WorldAnalysisState:
    """Append-only analysis state shared by workbench processing resources.

    Processors enrich the state by writing new silo versions. Older versions
    remain available for provenance, comparison, replay, and debugging.
    """

    def __init__(self, analysis_id: str | None = None) -> None:
        self.analysis_id = analysis_id or f"analysis-{uuid4().hex[:12]}"
        self._silos: dict[str, list[SiloRecord]] = defaultdict(list)

    def put(
        self,
        silo_id: str,
        *,
        semantic_type: str,
        representation_type: str,
        value: Any,
        subject: str | None = None,
        status: SiloStatus = SiloStatus.GENERATED,
        confidence: float = 1.0,
        produced_by: ProducerRef | None = None,
        derived_from: Iterable[str] = (),
        metadata: Mapping[str, Any] | None = None,
    ) -> SiloRecord:
        record = SiloRecord(
            silo_id=silo_id,
            version=len(self._silos[silo_id]) + 1,
            semantic_type=semantic_type,
            representation_type=representation_type,
            value=value,
            subject=subject,
            status=status,
            confidence=confidence,
            produced_by=produced_by,
            derived_from=tuple(derived_from),
            metadata=metadata or {},
        )
        self._silos[silo_id].append(record)
        return record

    def latest(self, silo_id: str) -> SiloRecord:
        try:
            return self._silos[silo_id][-1]
        except (KeyError, IndexError) as exc:
            raise KeyError(f"No silo named {silo_id!r}") from exc

    def get(self, reference: str) -> SiloRecord:
        silo_id, marker, raw_version = reference.rpartition(":v")
        if not marker or not raw_version.isdigit():
            return self.latest(reference)
        history = self._silos.get(silo_id, [])
        version = int(raw_version)
        if version < 1 or version > len(history):
            raise KeyError(f"No silo version {reference!r}")
        return history[version - 1]

    def history(self, silo_id: str) -> tuple[SiloRecord, ...]:
        return tuple(self._silos.get(silo_id, ()))

    def latest_silos(self) -> Mapping[str, SiloRecord]:
        return MappingProxyType(
            {silo_id: records[-1] for silo_id, records in self._silos.items() if records}
        )

    def record_observation(
        self,
        observation: Observation,
        *,
        producer: ProducerRef | None = None,
    ) -> SiloRecord:
        return self.put(
            f"observation/{observation.observation_id}",
            semantic_type="observation",
            representation_type=observation.representation_type,
            value=observation,
            subject=observation.source,
            status=SiloStatus.OBSERVED,
            produced_by=producer,
            metadata=observation.metadata,
        )

    def set_world_model(
        self,
        model: WorldModel,
        *,
        derived_from: Iterable[str] = (),
        producer: ProducerRef | None = None,
    ) -> SiloRecord:
        return self.put(
            "world/model",
            semantic_type="world_model",
            representation_type="python_object",
            value=model,
            subject=model.model_id,
            status=SiloStatus.HYPOTHETICAL,
            confidence=model.confidence,
            produced_by=producer,
            derived_from=derived_from,
        )

    def set_goals(
        self,
        goals: Sequence[Goal],
        *,
        derived_from: Iterable[str] = (),
        producer: ProducerRef | None = None,
    ) -> SiloRecord:
        return self.put(
            "goals/active",
            semantic_type="goal_set",
            representation_type="python_object",
            value=tuple(goals),
            status=SiloStatus.GENERATED,
            produced_by=producer,
            derived_from=derived_from,
        )

    def record_simulation(
        self,
        request: SimulationRequest,
        result: SimulationResult,
        *,
        derived_from: Iterable[str] = (),
        producer: ProducerRef | None = None,
    ) -> SiloRecord:
        if request.simulation_id != result.simulation_id:
            raise ValueError("simulation request and result IDs do not match")
        return self.put(
            f"simulation/{request.simulation_id}",
            semantic_type="simulation_result",
            representation_type="python_object",
            value={"request": request, "result": result},
            subject=request.world_model_id,
            status=SiloStatus.HYPOTHETICAL,
            confidence=result.confidence,
            produced_by=producer,
            derived_from=derived_from,
        )

    def record_demonstration_step(
        self,
        step: DemonstrationStep,
        *,
        producer: ProducerRef | None = None,
    ) -> SiloRecord:
        before = self.get(step.before_observation)
        after = self.get(step.after_observation)
        if before.semantic_type != "observation" or after.semantic_type != "observation":
            raise ValueError("demonstration endpoints must reference observations")
        return self.put(
            f"demonstration/{step.step_id}",
            semantic_type="demonstration_step",
            representation_type="python_object",
            value=step,
            subject=before.subject,
            status=SiloStatus.OBSERVED,
            confidence=1.0,
            produced_by=producer,
            derived_from=(before.reference, after.reference),
            metadata={"actor": step.intervention.actor, **dict(step.metadata)},
        )


class ObservationAnalyzer(Protocol):
    def analyze(
        self, observation: Observation, state: WorldAnalysisState
    ) -> Iterable[SiloRecord]: ...


class WorldModelLearner(Protocol):
    def update(
        self, observation: Observation, state: WorldAnalysisState
    ) -> WorldModel: ...


class GoalProvider(Protocol):
    def goals(self, state: WorldAnalysisState, model: WorldModel) -> Sequence[Goal]: ...


class SimulationPolicy(Protocol):
    def select(
        self,
        state: WorldAnalysisState,
        model: WorldModel,
        goals: Sequence[Goal],
    ) -> Iterable[SimulationRequest]: ...


class Simulator(Protocol):
    def simulate(self, request: SimulationRequest, model: WorldModel) -> SimulationResult: ...


class WorldLearningWorkbench:
    """Coordinates analysis, world learning, goals, and selected simulation."""

    def __init__(
        self,
        *,
        learner: WorldModelLearner,
        goal_provider: GoalProvider,
        simulation_policy: SimulationPolicy,
        simulator: Simulator,
        analyzers: Sequence[ObservationAnalyzer] = (),
        state: WorldAnalysisState | None = None,
    ) -> None:
        self.learner = learner
        self.goal_provider = goal_provider
        self.simulation_policy = simulation_policy
        self.simulator = simulator
        self.analyzers = tuple(analyzers)
        self.state = state or WorldAnalysisState()

    def process(self, observation: Observation) -> tuple[SimulationResult, ...]:
        observed = self.state.record_observation(
            observation,
            producer=ProducerRef("observe_world", "environment_adapter"),
        )
        for analyzer in self.analyzers:
            tuple(analyzer.analyze(observation, self.state))

        model = self.learner.update(observation, self.state)
        model_record = self.state.set_world_model(
            model,
            derived_from=(observed.reference,),
            producer=ProducerRef("update_world_model", type(self.learner).__name__),
        )
        goals = tuple(self.goal_provider.goals(self.state, model))
        goal_record = self.state.set_goals(
            goals,
            derived_from=(model_record.reference,),
            producer=ProducerRef("identify_goals", type(self.goal_provider).__name__),
        )

        results = []
        for request in self.simulation_policy.select(self.state, model, goals):
            unknown = set(request.goal_ids) - {goal.goal_id for goal in goals}
            if unknown:
                raise ValueError(f"simulation references unknown goals: {sorted(unknown)}")
            result = self.simulator.simulate(request, model)
            self.state.record_simulation(
                request,
                result,
                derived_from=(model_record.reference, goal_record.reference),
                producer=ProducerRef("simulate_candidates", type(self.simulator).__name__),
            )
            results.append(result)
        return tuple(results)


class HumanDemonstrationObserver:
    """Collect human play as learning examples without choosing actions itself."""

    def __init__(
        self,
        *,
        analyzers: Sequence[ObservationAnalyzer] = (),
        state: WorldAnalysisState | None = None,
    ) -> None:
        self.analyzers = tuple(analyzers)
        self.state = state or WorldAnalysisState()
        self.current_observation: SiloRecord | None = None

    def _record_and_analyze(self, observation: Observation) -> SiloRecord:
        record = self.state.record_observation(
            observation,
            producer=ProducerRef("observe_world", "environment_adapter"),
        )
        for analyzer in self.analyzers:
            tuple(analyzer.analyze(observation, self.state))
        return record

    def begin(self, observation: Observation) -> SiloRecord:
        """Record and objectify the first observation of an episode."""
        self.current_observation = self._record_and_analyze(observation)
        return self.current_observation

    def observe_human_step(
        self,
        intervention: Intervention,
        resulting_observation: Observation,
        *,
        step_id: str | None = None,
    ) -> DemonstrationStep:
        """Record a human-selected action and the observation it produced."""
        if self.current_observation is None:
            raise RuntimeError("begin() must record an initial observation first")
        previous = self.current_observation
        current = self._record_and_analyze(resulting_observation)
        step = DemonstrationStep(
            step_id=step_id or f"step-{uuid4().hex[:12]}",
            before_observation=previous.reference,
            intervention=intervention,
            after_observation=current.reference,
            metadata={"learning_mode": "human_demonstration"},
        )
        self.state.record_demonstration_step(
            step,
            producer=ProducerRef("observe_human_intervention", "demonstration_observer"),
        )
        self.current_observation = current
        return step
