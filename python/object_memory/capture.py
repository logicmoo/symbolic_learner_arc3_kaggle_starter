from __future__ import annotations

from dataclasses import asdict, is_dataclass
from enum import Enum
from hashlib import sha256
from pathlib import Path
import json
from typing import Any, Callable, Mapping

from project_paths import PROJECT_ROOT
from swipl_bridge import SWIPrologBridge

from .adapters import GridAdapter
from .forms import CellLogoForm, FitResult
from .integration import Phase2LearnerPayloadBuilder
from .learning import (
    OutcomeChannel,
    PredictionEvaluator,
    PredictionGrade,
    PredictionGradeStatus,
    RuleExecutor,
)
from .memory import SingleWriter
from .models import (
    ArtifactRef,
    CommittedAtom,
    EncounterRecord,
    InstanceParameters,
    ProvenanceRef,
    RecognitionAccount,
    TurtleProgramRef,
    deterministic_identifier,
)
from .recognition import (
    EncounterChangeSession,
    RecognitionSession,
    RegistryCorrespondenceAuthority,
    TurtleReconstructionEvidenceBuilder,
)
from .replay import ActionTreeSemanticReplay
from .store import InMemorySemanticBackend, SymbolicStore


def standard_semantic_grid_observer(
    *, learner_plugin: Any | None = None
) -> "SemanticGridCaptureObserver":
    """Compose the canonical live grid observer without coupling it to Phase 1."""

    from workbench.server.runtime import analyze_grid

    from .memory import SymbolicMemory
    from .providers import PythonProvider

    semantic_store = SymbolicStore(InMemorySemanticBackend())
    if learner_plugin is None:
        from .integration import (
            PipelineGameObjectLearnerPlugin,
            phase2_rule_inducer,
            phase2_rule_ranker,
            phase2_transformation_learner,
            phase2_transition_analyzer,
        )
        from .learning import GameLearningPipeline
        from .prediction import PredictionLedger, RuleStore

        learner_plugin = PipelineGameObjectLearnerPlugin(
            GameLearningPipeline(
                phase2_transition_analyzer(),
                phase2_transformation_learner(),
                phase2_rule_inducer(),
                phase2_rule_ranker(),
                RuleStore(),
                PredictionLedger(),
                semantic_store,
            )
        )

    return SemanticGridCaptureObserver(
        GridAdapter(analyze_grid, PythonProvider({})),
        grid_selector=lambda runner: runner.current_grid(),
        symbolic_store=semantic_store,
        identity_writer=SingleWriter(SymbolicMemory()),
        learner_plugin=learner_plugin,
    )


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
        turtle_form_factory: Callable[[str], CellLogoForm] | None = None,
        identity_writer: SingleWriter | None = None,
        learner_plugin: Any | None = None,
    ) -> None:
        self.adapter = adapter
        self.grid_selector = grid_selector
        self.symbolic_store = symbolic_store or SymbolicStore(InMemorySemanticBackend())
        self.recognition = RecognitionSession(self.symbolic_store)
        self.changes = EncounterChangeSession(self.symbolic_store)
        self.turtle_evidence = TurtleReconstructionEvidenceBuilder()
        self.identity_writer = identity_writer
        self.learner_plugin = learner_plugin
        self.learner_results: list[Any] = []
        self._pending_prediction: tuple[str, Any] | None = None
        pipeline = getattr(learner_plugin, "pipeline", None)
        if pipeline is not None and pipeline.semantic_store is None:
            pipeline.semantic_store = self.symbolic_store
        if turtle_form_factory is None:
            bridge = SWIPrologBridge(PROJECT_ROOT / "prolog" / "arc3_agent.pl")
            turtle_form_factory = lambda source: CellLogoForm(source, swi_bridge=bridge)
        self.turtle_form_factory = turtle_form_factory
        self._latest_by_candidate: dict[str, str] = {}
        self._latest_observation_id: str | None = None
        self._loaded_level_roots: set[Path] = set()
        self._pending_authorizations: dict[
            str,
            tuple[Any, Any, str, tuple[str, ...]],
        ] = {}

    def _load_level_history(self, store: Any) -> None:
        """Replay one level once and restore the observer's encounter cursors."""

        level_root = store.level_root.resolve()
        if level_root in self._loaded_level_roots:
            return
        ActionTreeSemanticReplay().replay(level_root, self.symbolic_store)
        self._rehydrate_identity_writer()
        encounters = tuple(
            encounter
            for encounter in self.symbolic_store.encounters.records()
            if Path(encounter.action_tree_node).resolve().is_relative_to(level_root)
        )
        referenced = {
            encounter.previous_encounter_id
            for encounter in encounters
            if encounter.previous_encounter_id is not None
        }
        terminals = tuple(
            encounter for encounter in encounters if encounter.encounter_id not in referenced
        )
        for encounter in terminals:
            if encounter.candidate_identity_id is not None:
                self._latest_by_candidate[encounter.candidate_identity_id] = (
                    encounter.encounter_id
                )
        if terminals:
            latest = max(terminals, key=lambda item: item.action_tree_node)
            self._latest_observation_id = latest.observation_id
        self._loaded_level_roots.add(level_root)

    def _rehydrate_identity_writer(self) -> None:
        """Rebuild calibrated identity state from resolved, replayed accounts."""

        if self.identity_writer is None:
            return
        for account in self.symbolic_store.values("recognition_accounts"):
            identity_id = account.stored_identity_id
            if identity_id is None or account.decision_source == "unresolved":
                continue
            if self.identity_writer.memory.get(identity_id) is None:
                self.identity_writer.commit(
                    CommittedAtom(
                        identity_id,
                        "object",
                        {"authority": "action_tree_registry"},
                    )
                )
            for evidence_id in (
                *account.supporting_evidence_ids,
                *account.contradicting_evidence_ids,
            ):
                evidence = self.symbolic_store.get("evidence", evidence_id)
                if evidence is not None:
                    self.identity_writer.apply_evidence(identity_id, evidence)

    def authorization_options(self) -> dict[str, tuple[str, ...]]:
        """Return explicit friendly-identity choices for unresolved candidates."""

        options: dict[str, tuple[str, ...]] = {}
        for candidate_id, (tree_store, _, _, proposal_ids) in self._pending_authorizations.items():
            friendly = tree_store.registry_identities()
            identities = tuple(
                proposal.stored_identity_id
                for proposal_id in proposal_ids
                if (proposal := self.symbolic_store.get("match_proposals", proposal_id))
                is not None
                and proposal.stored_identity_id in friendly
            )
            if identities:
                options[candidate_id] = identities
        return options

    def _persist_authorization_account(
        self,
        *,
        candidate_id: str,
        account: RecognitionAccount,
    ) -> None:
        tree_store, node, _, _ = self._pending_authorizations[candidate_id]
        self.symbolic_store.put_recognition(account)
        path = self._write_record(
            node.path / "semantic" / f"{account.account_id}.recognition-account.json",
            account,
        )
        tree_store.link_semantic_record(
            node,
            record_type="recognition_account",
            record_id=account.account_id,
            artifact_path=path,
            schema_version=account.schema_version,
            deterministic_hash=account.account_id.rsplit("-", 1)[-1],
        )

    def authorize_candidate(
        self,
        *,
        candidate_id: str,
        selected_identity_id: str,
        decision_id: str,
        decision_source: str = "explicit_registry_selection",
    ) -> RecognitionAccount:
        """Accept one pending proposal through the single identity writer."""

        if self.identity_writer is None:
            raise RuntimeError("identity writer is required for authorization")
        pending = self._pending_authorizations.get(candidate_id)
        if pending is None:
            raise KeyError(candidate_id)
        tree_store, _, encounter_id, proposal_ids = pending
        proposals = tuple(
            proposal
            for proposal_id in proposal_ids
            if (proposal := self.symbolic_store.get("match_proposals", proposal_id))
            is not None
        )
        selected = next(
            (
                proposal
                for proposal in proposals
                if proposal.stored_identity_id == selected_identity_id
            ),
            None,
        )
        if selected is None:
            raise ValueError("selected identity has no pending correspondence proposal")
        if selected_identity_id not in tree_store.registry_identities():
            raise ValueError("selected identity is not a friendly registry identity")
        if self.identity_writer.memory.get(selected_identity_id) is None:
            self.identity_writer.commit(
                CommittedAtom(
                    selected_identity_id,
                    "object",
                    {"authority": "action_tree_registry"},
                )
            )
        evidence = tuple(
            item
            for evidence_id in selected.evidence_ids
            if (item := self.symbolic_store.get("evidence", evidence_id)) is not None
        )
        account = RegistryCorrespondenceAuthority(
            self.identity_writer,
            tree_store,
        ).accept(
            candidate_id=candidate_id,
            selected_identity_id=selected_identity_id,
            proposals=proposals,
            evidence=evidence,
            encounter_id=encounter_id,
            decision_id=decision_id,
            decision_source=decision_source,
        )
        self._persist_authorization_account(candidate_id=candidate_id, account=account)
        del self._pending_authorizations[candidate_id]
        return account

    def reject_candidate(
        self,
        *,
        candidate_id: str,
        selected_identity_id: str,
        decision_id: str,
        decision_source: str = "explicit_registry_rejection",
    ) -> RecognitionAccount:
        """Reject one pending friendly-identity proposal without calibrating it."""

        pending = self._pending_authorizations.get(candidate_id)
        if pending is None:
            raise KeyError(candidate_id)
        tree_store, _, encounter_id, proposal_ids = pending
        proposals = tuple(
            proposal
            for proposal_id in proposal_ids
            if (proposal := self.symbolic_store.get("match_proposals", proposal_id))
            is not None
        )
        account = RegistryCorrespondenceAuthority(
            self.identity_writer,
            tree_store,
        ).reject(
            candidate_id=candidate_id,
            selected_identity_id=selected_identity_id,
            proposals=proposals,
            encounter_id=encounter_id,
            decision_id=decision_id,
            decision_source=decision_source,
        )
        self._persist_authorization_account(candidate_id=candidate_id, account=account)
        selected_proposal_id = next(
            proposal.proposal_id
            for proposal in proposals
            if proposal.stored_identity_id == selected_identity_id
        )
        remaining = tuple(
            proposal_id for proposal_id in proposal_ids if proposal_id != selected_proposal_id
        )
        if remaining:
            self._pending_authorizations[candidate_id] = (
                tree_store,
                pending[1],
                encounter_id,
                remaining,
            )
        else:
            del self._pending_authorizations[candidate_id]
        return account

    def _fit_turtle(self, source: str, candidate: Mapping[str, Any]) -> FitResult | None:
        """Regenerate a captured Turtle program without fabricating failed evidence."""

        try:
            return self.turtle_form_factory(source).fit_instance(candidate)
        except (OSError, RuntimeError, TypeError, ValueError) as exc:
            print(f"warning: unable to fit captured Turtle program: {exc}")
            return None

    @staticmethod
    def _write_record(path: Path, value: Any) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        source = json.dumps(_jsonable(value), indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        if path.exists() and path.read_text(encoding="utf-8") != source:
            raise RuntimeError(f"Semantic record conflict at {path}")
        path.write_text(source, encoding="utf-8")
        return path

    @staticmethod
    def _action_key(value: Any) -> str:
        if isinstance(value, Mapping):
            value = value.get("action", value.get("event", value))
        return str(value).strip().upper()

    def before_action(
        self,
        *,
        runner: Any,
        store: Any,
        node: Any,
        action: str,
        data: Mapping[str, Any],
    ) -> None:
        """Record a learned-rule prediction before Arc3Runner observes the outcome."""

        del runner
        pipeline = getattr(self.learner_plugin, "pipeline", None)
        if (
            pipeline is None
            or pipeline.semantic_store is None
            or self._pending_prediction is not None
        ):
            return
        rules = tuple(
            rule
            for rule in pipeline.rule_store.rules()
            if rule.predicted_effects
        )
        if not rules:
            return
        action_key = self._action_key(action)
        candidates = tuple(
            rule
            for rule in rules
            if self._action_key(rule.action_or_event) == action_key
        )
        created_sequence = len(self.symbolic_store.encounters.records()) + len(
            pipeline.prediction_ledger.records()
        ) + 1
        source_state_id = self._latest_observation_id or str(node.path)
        prediction_id = None
        if candidates:
            selected = pipeline.rule_ranker.rank(candidates)[0]
            prediction_id = deterministic_identifier(
                "prediction",
                {
                    "rule_id": selected.rule_id,
                    "source_state_id": source_state_id,
                    "action": action,
                    "data": dict(data),
                    "created_sequence": created_sequence,
                },
            )
            predicted, _record = pipeline.predict(
                prediction_id=prediction_id,
                rule_id=selected.rule_id,
                source_state_id=source_state_id,
                state={"action": action, "data": dict(data)},
                created_sequence=created_sequence,
                executor=RuleExecutor(
                    pipeline.rule_store,
                    checker=lambda _rule, _state: True,
                    executor=lambda rule, _state: rule.predicted_effects[0],
                ),
            )
            self._pending_prediction = (prediction_id, predicted)

        recommendation = pipeline.recommend_action(
            source_state_id=source_state_id,
            attempted_action={"action": action, "data": dict(data)},
            created_sequence=created_sequence,
            prediction_id=prediction_id,
        )
        if recommendation is not None:
            recommendation_path = self._write_record(
                node.path
                / "semantic"
                / f"{recommendation.recommendation_id}.action_recommendation.json",
                recommendation,
            )
            store.link_semantic_record(
                node,
                record_type="action_recommendation",
                record_id=recommendation.recommendation_id,
                artifact_path=recommendation_path,
                schema_version=recommendation.schema_version,
                deterministic_hash=sha256(
                    recommendation_path.read_bytes()
                ).hexdigest(),
            )
        if prediction_id is not None:
            store.link_prediction_history(node, pipeline.semantic_store, prediction_id)

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
        self._load_level_history(store)
        previous_observation_id = self._latest_observation_id
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
            turtle_fit = self._fit_turtle(turtle_source, details)
            turtle_ref = TurtleProgramRef(
                turtle_artifact,
                fit_score=(1.0 - turtle_fit.residual) if turtle_fit is not None else None,
                distance=turtle_fit.residual if turtle_fit is not None else None,
                residual_score=turtle_fit.residual if turtle_fit is not None else None,
                description_length=(
                    float(
                        turtle_fit.parameters.get(
                            "description_length",
                            len(turtle_source.encode("utf-8")),
                        )
                    )
                    if turtle_fit is not None
                    else None
                ),
            )
            turtle_evidence = None
            if turtle_fit is not None:
                turtle_evidence = self.turtle_evidence.build(
                    identity_id=candidate.candidate_id,
                    fit=turtle_fit,
                    source=ProvenanceRef.create(
                        source_id=turtle_artifact.artifact_id,
                        provider="swi_prolog.turtle_dsl",
                        action_tree_node=str(node.path),
                        artifact_id=turtle_artifact.artifact_id,
                        metadata={"observation_id": batch.observation.observation_id},
                    ),
                    artifact_id=turtle_artifact.artifact_id,
                )
                self.symbolic_store.put_evidence(turtle_evidence)
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
                    relationships=tuple(
                        {
                            "target": str(item.get("target")),
                            "relation": str(item.get("relation")),
                        }
                        for item in sorted(
                            details.get("relationships") or (),
                            key=lambda value: (
                                str(value.get("relation")),
                                str(value.get("target")),
                            ),
                        )
                    ),
                ),
                turtle_programs=(turtle_ref,),
                evidence_ids=(
                    (turtle_evidence.evidence_id,) if turtle_evidence is not None else ()
                ),
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
            if turtle_evidence is not None:
                evidence_path = self._write_record(
                    semantic_dir / f"{turtle_evidence.evidence_id}.evidence.json",
                    turtle_evidence,
                )
                store.link_semantic_record(
                    node,
                    record_type="evidence",
                    record_id=turtle_evidence.evidence_id,
                    artifact_path=evidence_path,
                    schema_version=turtle_evidence.schema_version,
                    deterministic_hash=turtle_evidence.evidence_id.rsplit("-", 1)[-1],
                )
            if self.recognition.latest_known_instances():
                proposals = self.recognition.propose(encounter.encounter_id)
                self._pending_authorizations[candidate.candidate_id] = (
                    store,
                    node,
                    encounter.encounter_id,
                    tuple(item.proposal_id for item in proposals),
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
        if previous_observation_id is not None:
            proposals, changes, residuals = self.changes.detect(
                previous_observation_id,
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
        if self.learner_plugin is not None:
            builder = Phase2LearnerPayloadBuilder(self.symbolic_store)
            current_payload = builder.for_observation(batch.observation.observation_id)
            if previous_observation_id is None:
                result = self.learner_plugin.consume_state(current_payload)
            else:
                result = self.learner_plugin.consume_transition(
                    builder.for_observation(previous_observation_id),
                    {"action": action, "data": dict(data)},
                    current_payload,
                )
            self.learner_results.append(result)
            pending_prediction = self._pending_prediction
            learning_value = getattr(result, "value", None)
            learning_step = getattr(learning_value, "learning_step", None)
            if pending_prediction is not None and learning_step is not None:
                prediction_id, predicted = pending_prediction
                observed_changes = list(learning_step.transition.changes)
                pipeline = getattr(self.learner_plugin, "pipeline", None)
                if pipeline is not None:
                    pipeline.grade_prediction(
                        prediction_id=prediction_id,
                        outcome_sequence=len(self.symbolic_store.encounters.records()),
                        outcome_channel=OutcomeChannel(lambda: observed_changes),
                        evaluator=PredictionEvaluator(
                            lambda expected, observed: PredictionGrade(
                                1.0 if expected in observed else 0.0,
                                evidence=(
                                    "independent_arc3_transition",
                                    *tuple(str(item) for item in observed),
                                ),
                                status=(
                                    PredictionGradeStatus.SUCCESS
                                    if expected in observed
                                    else PredictionGradeStatus.CONTRADICTION
                                    if observed
                                    else PredictionGradeStatus.FAILURE
                                ),
                            )
                        ),
                    )
                    store.link_prediction_history(
                        node, pipeline.semantic_store, prediction_id
                    )
                    self._pending_prediction = None
            result_payload = _jsonable(result)
            encoded = json.dumps(
                result_payload,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            ) + "\n"
            result_hash = sha256(encoded.encode("utf-8")).hexdigest()
            result_path = semantic_dir / f"learner-result-{result_hash[:16]}.json"
            if result_path.exists() and result_path.read_text(encoding="utf-8") != encoded:
                raise RuntimeError(f"Learner result conflict at {result_path}")
            result_path.write_text(encoded, encoding="utf-8")
            store.link_semantic_record(
                node,
                record_type="learner_result",
                record_id=f"learner-result-{result_hash}",
                artifact_path=result_path,
                schema_version="1.0.0",
                deterministic_hash=result_hash,
            )
            value_payload = (
                result_payload.get("value", result_payload)
                if isinstance(result_payload, Mapping)
                else {}
            )
            learning_step = (
                value_payload.get("learning_step")
                if isinstance(value_payload, Mapping)
                else None
            )
            if isinstance(learning_step, Mapping):
                learner_records = [
                    ("learner_transition", learning_step.get("transition")),
                    *(
                        ("transformation_candidate", item)
                        for item in learning_step.get("candidates") or ()
                    ),
                    *(
                        ("transition_rule", item)
                        for item in learning_step.get("rules") or ()
                    ),
                ]
                for record_type, record_payload in learner_records:
                    if not isinstance(record_payload, Mapping):
                        continue
                    record_encoded = json.dumps(
                        record_payload,
                        indent=2,
                        ensure_ascii=False,
                        sort_keys=True,
                    ) + "\n"
                    record_hash = sha256(record_encoded.encode("utf-8")).hexdigest()
                    record_id = str(
                        record_payload.get("rule_id")
                        or record_payload.get("candidate_id")
                        or f"learner-transition-{record_hash}"
                    )
                    record_path = semantic_dir / (
                        f"{record_type}-{record_hash[:16]}.json"
                    )
                    if (
                        record_path.exists()
                        and record_path.read_text(encoding="utf-8") != record_encoded
                    ):
                        raise RuntimeError(f"Learner record conflict at {record_path}")
                    record_path.write_text(record_encoded, encoding="utf-8")
                    store.link_semantic_record(
                        node,
                        record_type=record_type,
                        record_id=record_id,
                        artifact_path=record_path,
                        schema_version="1.0.0",
                        deterministic_hash=record_hash,
                    )
        self._latest_observation_id = batch.observation.observation_id
