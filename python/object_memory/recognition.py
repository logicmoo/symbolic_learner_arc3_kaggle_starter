from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Mapping

from .forms import FitResult
from .models import (
    EvidencePolarity,
    EvidenceRecord,
    InstanceParameters,
    MatchProposal,
    ObjectChange,
    ProvenanceRef,
    RecognitionAccount,
    ResidualCandidate,
    ResidualDisposition,
)
from .memory import ResidualGate, SingleWriter
from .store import SymbolicStore


@dataclass(frozen=True)
class PartialVisibilityCompletion:
    """A reconstructed instance that keeps inferred and observed data distinct."""

    candidate_id: str
    stored_identity_id: str
    observed: InstanceParameters
    completed: InstanceParameters
    inferred_fields: tuple[str, ...]
    proposal_id: str
    evidence_ids: tuple[str, ...] = ()


class InstanceMatcher:
    """Generate advisory correspondence proposals from normalized instances."""

    @staticmethod
    def change_transformation(field: str) -> str:
        if field == "position":
            return "translation"
        if field == "orientation":
            return "rotation"
        if field == "scale":
            return "scale"
        if field == "appearance.color":
            return "recolor"
        if field == "reflection":
            return "reflection"
        if field == "visibility":
            return "partial_visibility"
        if field == "noise_score":
            return "noise"
        if field == "geometry":
            return "geometry_change"
        if field == "topology":
            return "topology_change"
        if field == "relationships":
            return "relationship_change"
        return "appearance_change"

    def compare(
        self,
        *,
        candidate_id: str,
        current: InstanceParameters,
        stored_identity_id: str,
        stored: InstanceParameters,
        provenance: tuple[ProvenanceRef, ...] = (),
    ) -> MatchProposal:
        matched: list[str] = []
        changed: dict[str, object] = {}
        transformations: list[str] = []

        def compare_field(name: str, before: object, after: object, transform: str) -> None:
            if before == after:
                matched.append(name)
            else:
                changed[name] = {"from": before, "to": after}
                transformations.append(transform)

        compare_field("position", stored.position, current.position, "translation")
        compare_field("orientation", stored.orientation, current.orientation, "rotation")
        compare_field("scale", stored.scale, current.scale, "scale")
        if stored.reflection is not None or current.reflection is not None:
            compare_field("reflection", stored.reflection, current.reflection, "reflection")
        if stored.visibility != 1.0 or current.visibility != 1.0:
            compare_field("visibility", stored.visibility, current.visibility, "partial_visibility")
        if stored.noise_score != 0.0 or current.noise_score != 0.0:
            compare_field("noise_score", stored.noise_score, current.noise_score, "noise")
        if stored.geometry or current.geometry:
            compare_field("geometry", stored.geometry, current.geometry, "geometry_change")
        if stored.topology or current.topology:
            compare_field("topology", stored.topology, current.topology, "topology_change")
        if stored.relationships or current.relationships:
            compare_field(
                "relationships",
                stored.relationships,
                current.relationships,
                "relationship_change",
            )
        appearance_keys = sorted({*stored.appearance, *current.appearance})
        for key in appearance_keys:
            before = stored.appearance.get(key)
            after = current.appearance.get(key)
            field = f"appearance.{key}"
            if before == after:
                matched.append(field)
            else:
                changed[field] = {"from": before, "to": after}
                transformations.append(
                    "partial_visibility"
                    if key not in current.appearance and current.visibility < stored.visibility
                    else ("recolor" if key == "color" else "appearance_change")
                )
        denominator = len(matched) + len(changed)
        similarity = len(matched) / denominator if denominator else 1.0
        allowed = tuple(
            item
            for item in dict.fromkeys(transformations)
            if item in stored.supported_transformations
            or item in current.supported_transformations
        )
        return MatchProposal.create(
            candidate_id=candidate_id,
            stored_identity_id=stored_identity_id,
            matched_properties=tuple(matched),
            changed_properties=changed,
            allowed_transformations=allowed,
            similarity=similarity,
            provenance=provenance,
        )

    def proposals(
        self,
        *,
        candidate_id: str,
        current: InstanceParameters,
        stored: Mapping[str, InstanceParameters],
        provenance: tuple[ProvenanceRef, ...] = (),
        retrieval_scores: Mapping[str, float] | None = None,
        retrieval_source: str | None = None,
    ) -> tuple[MatchProposal, ...]:
        proposals = []
        for identity_id, instance in stored.items():
            proposal = self.compare(
                candidate_id=candidate_id,
                current=current,
                stored_identity_id=identity_id,
                stored=instance,
                provenance=provenance,
            )
            if retrieval_scores is not None and identity_id in retrieval_scores:
                score = float(retrieval_scores[identity_id])
                if not 0.0 <= score <= 1.0:
                    raise ValueError("embedding retrieval scores must be between 0 and 1")
                proposal = replace(
                    proposal,
                    retrieval_score=score,
                    retrieval_source=retrieval_source or "embedding_retrieval",
                )
                proposal = replace(
                    proposal,
                    proposal_id=MatchProposal.create(
                        candidate_id=proposal.candidate_id,
                        stored_identity_id=proposal.stored_identity_id,
                        matched_properties=proposal.matched_properties,
                        changed_properties=proposal.changed_properties,
                        allowed_transformations=proposal.allowed_transformations,
                        similarity=proposal.similarity,
                        retrieval_score=proposal.retrieval_score,
                        retrieval_source=proposal.retrieval_source,
                        provenance=proposal.provenance,
                    ).proposal_id,
                )
            proposals.append(proposal)
        return tuple(
            sorted(
                proposals,
                key=lambda item: (
                    -(item.similarity if item.similarity is not None else -1.0),
                    -(item.retrieval_score if item.retrieval_score is not None else -1.0),
                    item.stored_identity_id,
                ),
            )
        )

    def recognition_account(
        self,
        *,
        candidate_id: str,
        proposals: tuple[MatchProposal, ...],
        selected_identity_id: str | None = None,
        decision_source: str = "unresolved",
    ) -> RecognitionAccount:
        selected = next(
            (
                item
                for item in proposals
                if item.stored_identity_id == selected_identity_id
            ),
            None,
        )
        return RecognitionAccount.create(
            candidate_id=candidate_id,
            stored_identity_id=selected_identity_id,
            matched_properties=selected.matched_properties if selected else (),
            changed_properties=selected.changed_properties if selected else {},
            allowed_transformations=selected.allowed_transformations if selected else (),
            rival_proposal_ids=tuple(
                item.proposal_id for item in proposals if item is not selected
            ),
            decision_source=decision_source,
        )


class RecognitionSession:
    """Persist unresolved proposals between a candidate and known encounter histories."""

    def __init__(self, store: SymbolicStore, matcher: InstanceMatcher | None = None) -> None:
        self.store = store
        self.matcher = matcher or InstanceMatcher()

    def latest_known_instances(self) -> dict[str, InstanceParameters]:
        resolved_candidates = {
            account.candidate_id: account.stored_identity_id
            for account in self.store.values("recognition_accounts")
            if account.stored_identity_id is not None
            and account.decision_source != "unresolved"
        }
        latest: dict[str, InstanceParameters] = {}
        for encounter in self.store.encounters.records():
            identity_id = encounter.object_identity_id
            if identity_id is None and encounter.candidate_identity_id is not None:
                identity_id = resolved_candidates.get(encounter.candidate_identity_id)
            if identity_id is not None:
                previous = latest.get(identity_id)
                current = encounter.instance
                if previous is not None and (
                    current.visibility < previous.visibility
                    or current.noise_score > previous.noise_score
                ):
                    current = replace(
                        previous,
                        position=current.position or previous.position,
                        supported_transformations=tuple(
                            dict.fromkeys(
                                (
                                    *previous.supported_transformations,
                                    *current.supported_transformations,
                                )
                            )
                        ),
                    )
                latest[identity_id] = current
        return latest

    def complete_partial(
        self,
        encounter_id: str,
        stored_identity_id: str,
    ) -> PartialVisibilityCompletion:
        """Complete an occluded encounter from one prior durable identity form."""

        encounter = self.store.encounters.get(encounter_id)
        if encounter is None:
            raise KeyError(encounter_id)
        history = tuple(
            item
            for item in self.store.encounters.records()
            if item.encounter_id != encounter_id
            and item.object_identity_id == stored_identity_id
        )
        if not history:
            raise ValueError(
                f"No prior form exists for identity {stored_identity_id!r}"
            )
        stored = max(
            history,
            key=lambda item: (
                item.instance.visibility,
                -item.instance.noise_score,
                len(item.instance.appearance),
                len(item.instance.geometry),
                len(item.instance.topology),
            ),
        ).instance
        observed = encounter.instance
        candidate_id = encounter.candidate_identity_id or f"completion:{encounter_id}"
        proposal = self.matcher.compare(
            candidate_id=candidate_id,
            current=observed,
            stored_identity_id=stored_identity_id,
            stored=stored,
            provenance=encounter.provenance,
        )
        if "partial_visibility" not in proposal.allowed_transformations:
            raise ValueError("Encounter does not declare a supported partial visibility change")
        source = (
            encounter.provenance[0]
            if encounter.provenance
            else ProvenanceRef(encounter_id, "partial_visibility_completion")
        )
        evidence = CorrespondenceEvidenceBuilder().build(proposal, source=source)
        for item in evidence:
            self.store.put_evidence(item)
        proposal = replace(
            proposal,
            evidence_ids=tuple(item.evidence_id for item in evidence),
        )
        self.store.put_match_proposal(proposal)

        appearance = {**stored.appearance, **observed.appearance}
        inferred_values = [
            f"appearance.{key}"
            for key in stored.appearance
            if key not in observed.appearance
        ]
        if stored.geometry and observed.visibility < 1.0:
            inferred_values.append("geometry")
        if stored.topology and observed.visibility < 1.0:
            inferred_values.append("topology")
        if stored.relationships and not observed.relationships:
            inferred_values.append("relationships")
        inferred = tuple(sorted(inferred_values))
        completed = replace(
            stored,
            position=observed.position or stored.position,
            orientation=observed.orientation or stored.orientation,
            scale=observed.scale or stored.scale,
            reflection=observed.reflection or stored.reflection,
            appearance=appearance,
            geometry=(stored.geometry if observed.visibility < 1.0 else observed.geometry),
            topology=(stored.topology if observed.visibility < 1.0 else observed.topology),
            relationships=observed.relationships or stored.relationships,
            supported_transformations=tuple(
                dict.fromkeys(
                    (*stored.supported_transformations, *observed.supported_transformations)
                )
            ),
            visibility=1.0,
            noise_score=0.0,
        )
        return PartialVisibilityCompletion(
            candidate_id=candidate_id,
            stored_identity_id=stored_identity_id,
            observed=observed,
            completed=completed,
            inferred_fields=inferred,
            proposal_id=proposal.proposal_id,
            evidence_ids=proposal.evidence_ids,
        )

    def propose(
        self,
        encounter_id: str,
        *,
        retrieval_scores: Mapping[str, float] | None = None,
        retrieval_source: str | None = None,
    ) -> tuple[MatchProposal, ...]:
        encounter = self.store.encounters.get(encounter_id)
        if encounter is None:
            raise KeyError(encounter_id)
        if encounter.candidate_identity_id is None:
            raise ValueError("recognition proposals require a candidate encounter")
        proposals = self.matcher.proposals(
            candidate_id=encounter.candidate_identity_id,
            current=encounter.instance,
            stored=self.latest_known_instances(),
            provenance=encounter.provenance,
            retrieval_scores=retrieval_scores,
            retrieval_source=retrieval_source,
        )
        source = (
            encounter.provenance[0]
            if encounter.provenance
            else ProvenanceRef(encounter.encounter_id, "property_matcher")
        )
        enriched: list[MatchProposal] = []
        builder = CorrespondenceEvidenceBuilder()
        for proposal in proposals:
            evidence = builder.build(proposal, source=source)
            for item in evidence:
                self.store.put_evidence(item)
            proposal = replace(
                proposal,
                evidence_ids=tuple(item.evidence_id for item in evidence),
            )
            self.store.put_match_proposal(proposal)
            enriched.append(proposal)
        proposals = tuple(enriched)
        self.store.put_recognition(
            self.matcher.recognition_account(
                candidate_id=encounter.candidate_identity_id,
                proposals=proposals,
            )
        )
        return proposals

    def unresolved_account(self, candidate_id: str) -> RecognitionAccount | None:
        accounts = self.store.values("recognition_accounts")
        return next(
            (
                account
                for account in reversed(accounts)
                if account.candidate_id == candidate_id
                and account.decision_source == "unresolved"
            ),
            None,
        )


class CorrespondenceEvidenceBuilder:
    """Create attributable signed evidence from a proposal's property explanation."""

    def build(
        self,
        proposal: MatchProposal,
        *,
        source: ProvenanceRef,
        created_sequence: int = 0,
    ) -> tuple[EvidenceRecord, ...]:
        evidence: list[EvidenceRecord] = []
        for field in sorted(proposal.matched_properties):
            evidence.append(
                EvidenceRecord.create(
                    subject_id=proposal.stored_identity_id,
                    polarity=EvidencePolarity.SUPPORTS,
                    source=source,
                    detail={
                        "proposal_id": proposal.proposal_id,
                        "property": field,
                        "assessment": "exact_match",
                    },
                    created_sequence=created_sequence,
                )
            )
        allowed = set(proposal.allowed_transformations)
        for field, change in sorted(proposal.changed_properties.items()):
            transformation = InstanceMatcher.change_transformation(field)
            if (
                transformation == "appearance_change"
                and isinstance(change, Mapping)
                and change.get("to") is None
                and "partial_visibility" in allowed
            ):
                transformation = "partial_visibility"
            explained = transformation in allowed
            evidence.append(
                EvidenceRecord.create(
                    subject_id=proposal.stored_identity_id,
                    polarity=(
                        EvidencePolarity.SUPPORTS
                        if explained
                        else EvidencePolarity.CONTRADICTS
                    ),
                    source=source,
                    detail={
                        "proposal_id": proposal.proposal_id,
                        "property": field,
                        "change": change,
                        "transformation": transformation,
                        "assessment": (
                            "allowed_transformation"
                            if explained
                            else "unexplained_change"
                        ),
                    },
                    created_sequence=created_sequence,
                )
            )
        return tuple(evidence)


class EncounterChangeSession:
    """Persist correspondences, evidence, and changes across two observations."""

    def __init__(self, store: SymbolicStore, matcher: InstanceMatcher | None = None) -> None:
        self.store = store
        self.matcher = matcher or InstanceMatcher()
        self.residual_analyzer = ResidualAnalyzer()

    def detect(
        self,
        previous_observation_id: str,
        current_observation_id: str,
    ) -> tuple[
        tuple[MatchProposal, ...],
        tuple[ObjectChange, ...],
        tuple[ResidualCandidate, ...],
    ]:
        previous = {
            item.candidate_identity_id: item
            for item in self.store.encounters.records()
            if item.observation_id == previous_observation_id
            and item.candidate_identity_id is not None
        }
        current = {
            item.candidate_identity_id: item
            for item in self.store.encounters.records()
            if item.observation_id == current_observation_id
            and item.candidate_identity_id is not None
        }
        correspondence = StructuralCorrespondenceInferer().infer(previous, current)
        proposals: list[MatchProposal] = []
        proposal_by_candidate: dict[str, MatchProposal] = {}
        property_proposals: list[MatchProposal] = []
        identity_use_count = {
            identity_id: sum(
                identity_id in identities for identities in correspondence.values()
            )
            for identities in correspondence.values()
            for identity_id in identities
        }
        for candidate_id, identity_ids in sorted(correspondence.items()):
            for identity_id in identity_ids:
                proposal = self.matcher.compare(
                    candidate_id=candidate_id,
                    current=current[candidate_id].instance,
                    stored_identity_id=identity_id,
                    stored=previous[identity_id].instance,
                    provenance=current[candidate_id].provenance,
                )
                source = (
                    current[candidate_id].provenance[0]
                    if current[candidate_id].provenance
                    else ProvenanceRef(
                        current[candidate_id].encounter_id, "transition_matcher"
                    )
                )
                evidence = CorrespondenceEvidenceBuilder().build(proposal, source=source)
                for item in evidence:
                    self.store.put_evidence(item)
                proposal = replace(
                    proposal,
                    evidence_ids=tuple(item.evidence_id for item in evidence),
                )
                self.store.put_match_proposal(proposal)
                proposals.append(proposal)
                if len(identity_ids) == 1 and identity_use_count[identity_id] == 1:
                    proposal_by_candidate[candidate_id] = proposal
                    property_proposals.append(proposal)
        changes = ChangeDetector().detect(
            proposals=proposal_by_candidate,
            correspondence=correspondence,
            before_identity_ids=tuple(sorted(previous)),
            after_candidate_ids=tuple(sorted(current)),
            provenance=tuple(
                item for encounter in current.values() for item in encounter.provenance
            ),
        )
        for change in changes:
            self.store.put_object_change(change)
        residuals = tuple(
            residual
            for proposal in property_proposals
            for residual in self.residual_analyzer.from_proposal(proposal)
        )
        for residual in residuals:
            self.store.put_residual(residual)
        return tuple(proposals), changes, residuals


class StructuralCorrespondenceInferer:
    """Infer only exact one-to-one, split, or merge cell-set correspondences."""

    @staticmethod
    def _absolute_cells(encounter: Any) -> frozenset[tuple[float, float]]:
        instance = encounter.instance
        cells = instance.geometry.get("cells") or instance.geometry.get(
            "boundary_cells"
        )
        if not cells:
            return frozenset()
        x = float(instance.position[0]) if len(instance.position) > 0 else 0.0
        y = float(instance.position[1]) if len(instance.position) > 1 else 0.0
        return frozenset(
            (round(x + float(cell[0]), 9), round(y + float(cell[1]), 9))
            for cell in cells
        )

    @staticmethod
    def _disjoint(groups: list[frozenset[tuple[float, float]]]) -> bool:
        combined: set[tuple[float, float]] = set()
        for group in groups:
            if combined.intersection(group):
                return False
            combined.update(group)
        return True

    def infer(
        self, previous: Mapping[str, Any], current: Mapping[str, Any]
    ) -> dict[str, tuple[str, ...]]:
        correspondence = {
            candidate_id: (candidate_id,)
            for candidate_id in sorted(set(previous) & set(current))
        }
        unmatched_previous = set(previous) - set(correspondence)
        unmatched_current = set(current) - set(correspondence)
        previous_cells = {
            item_id: self._absolute_cells(encounter)
            for item_id, encounter in previous.items()
        }
        current_cells = {
            item_id: self._absolute_cells(encounter)
            for item_id, encounter in current.items()
        }

        for candidate_id in sorted(tuple(unmatched_current)):
            target = current_cells[candidate_id]
            parts = [
                identity_id
                for identity_id in sorted(unmatched_previous)
                if previous_cells[identity_id]
                and previous_cells[identity_id].issubset(target)
            ]
            groups = [previous_cells[item_id] for item_id in parts]
            if len(parts) > 1 and self._disjoint(groups) and frozenset().union(*groups) == target:
                correspondence[candidate_id] = tuple(parts)
                unmatched_current.remove(candidate_id)
                unmatched_previous.difference_update(parts)

        for identity_id in sorted(tuple(unmatched_previous)):
            target = previous_cells[identity_id]
            parts = [
                candidate_id
                for candidate_id in sorted(unmatched_current)
                if current_cells[candidate_id]
                and current_cells[candidate_id].issubset(target)
            ]
            groups = [current_cells[item_id] for item_id in parts]
            if len(parts) > 1 and self._disjoint(groups) and frozenset().union(*groups) == target:
                for candidate_id in parts:
                    correspondence[candidate_id] = (identity_id,)
                unmatched_current.difference_update(parts)
                unmatched_previous.remove(identity_id)

        for candidate_id in sorted(tuple(unmatched_current)):
            exact = [
                identity_id
                for identity_id in sorted(unmatched_previous)
                if current_cells[candidate_id]
                and current_cells[candidate_id] == previous_cells[identity_id]
            ]
            if len(exact) == 1:
                correspondence[candidate_id] = (exact[0],)
                unmatched_previous.remove(exact[0])
        return correspondence


class ResidualAnalyzer:
    """Separate unexplained proposal structure from recognized transformations."""

    def __init__(self, gate: ResidualGate | None = None) -> None:
        self.gate = gate or ResidualGate()
        self._recurrence: dict[tuple[str, str], int] = {}

    def from_proposal(self, proposal: MatchProposal) -> tuple[ResidualCandidate, ...]:
        allowed = set(proposal.allowed_transformations)
        residuals: list[ResidualCandidate] = []
        for field, change in sorted(proposal.changed_properties.items()):
            transformation = InstanceMatcher.change_transformation(field)
            if (
                transformation == "appearance_change"
                and isinstance(change, Mapping)
                and change.get("to") is None
                and "partial_visibility" in allowed
            ):
                transformation = "partial_visibility"
            if transformation in allowed:
                continue
            key = (proposal.candidate_id, field)
            recurrence = self._recurrence.get(key, 0) + 1
            self._recurrence[key] = recurrence
            residual = ResidualCandidate.create(
                source_candidate_id=proposal.candidate_id,
                disposition=ResidualDisposition.PROVISIONAL,
                residual_length=1.0,
                structured=True,
                recurrence_count=recurrence,
                provenance=(
                    proposal.proposal_id,
                    f"field:{field}",
                    f"recurrence:{recurrence}",
                ),
            )
            residuals.append(replace(residual, disposition=self.gate.evaluate(residual)))
        return tuple(residuals)


class TurtleReconstructionEvidenceBuilder:
    """Represent an exact or residual Turtle reconstruction fit as signed evidence."""

    def build(
        self,
        *,
        identity_id: str,
        fit: FitResult,
        source: ProvenanceRef,
        artifact_id: str | None = None,
        created_sequence: int = 0,
    ) -> EvidenceRecord:
        exact = fit.residual == 0.0
        return EvidenceRecord.create(
            subject_id=identity_id,
            polarity=(
                EvidencePolarity.SUPPORTS if exact else EvidencePolarity.CONTRADICTS
            ),
            source=source,
            detail={
                "assessment": "exact_turtle_reconstruction" if exact else "turtle_residual",
                "artifact_id": artifact_id,
                "residual": fit.residual,
                "parameters": fit.parameters,
            },
            created_sequence=created_sequence,
        )


class ChangeDetector:
    """Classify resolved before/after correspondences into semantic changes."""

    PROPERTY_KINDS = {
        "position": "moved",
        "scale": "resized",
        "orientation": "reoriented",
        "appearance.color": "recolored",
        "appearance.shape": "reshaped",
    }

    def detect(
        self,
        *,
        proposals: Mapping[str, MatchProposal],
        correspondence: Mapping[str, tuple[str, ...]],
        before_identity_ids: tuple[str, ...],
        after_candidate_ids: tuple[str, ...],
        provenance: tuple[ProvenanceRef, ...] = (),
    ) -> tuple[ObjectChange, ...]:
        changes: list[ObjectChange] = []
        matched_before = {
            identity_id
            for identities in correspondence.values()
            for identity_id in identities
        }
        for identity_id in sorted(set(before_identity_ids) - matched_before):
            changes.append(
                ObjectChange.create(
                    kind="disappeared",
                    before_identity_ids=(identity_id,),
                    provenance=provenance,
                )
            )
        for candidate_id in sorted(set(after_candidate_ids) - set(correspondence)):
            changes.append(
                ObjectChange.create(
                    kind="appeared",
                    after_candidate_ids=(candidate_id,),
                    provenance=provenance,
                )
            )
        for candidate_id, identities in sorted(correspondence.items()):
            if len(identities) > 1:
                changes.append(
                    ObjectChange.create(
                        kind="merged",
                        before_identity_ids=identities,
                        after_candidate_ids=(candidate_id,),
                        provenance=provenance,
                    )
                )
            proposal = proposals.get(candidate_id)
            if proposal is None:
                continue
            for field, value in sorted(proposal.changed_properties.items()):
                changes.append(
                    ObjectChange.create(
                        kind=self.PROPERTY_KINDS.get(field, "property_changed"),
                        before_identity_ids=identities,
                        after_candidate_ids=(candidate_id,),
                        properties={field: value},
                        evidence_ids=proposal.evidence_ids,
                        provenance=provenance,
                    )
                )
        candidates_by_identity: dict[str, list[str]] = {}
        for candidate_id, identities in correspondence.items():
            for identity_id in identities:
                candidates_by_identity.setdefault(identity_id, []).append(candidate_id)
        for identity_id, candidates in sorted(candidates_by_identity.items()):
            if len(candidates) > 1:
                changes.append(
                    ObjectChange.create(
                        kind="split",
                        before_identity_ids=(identity_id,),
                        after_candidate_ids=tuple(sorted(candidates)),
                        provenance=provenance,
                    )
                )
        return tuple(
            sorted(
                changes,
                key=lambda item: (
                    item.kind,
                    item.before_identity_ids,
                    item.after_candidate_ids,
                    item.change_id,
                ),
            )
        )


class RegistryCorrespondenceAuthority:
    """Apply an explicit registry selection only when attributable evidence exists."""

    def __init__(self, writer: SingleWriter | None, action_tree_store: object) -> None:
        self.writer = writer
        self.action_tree_store = action_tree_store

    def accept(
        self,
        *,
        candidate_id: str,
        selected_identity_id: str,
        proposals: tuple[MatchProposal, ...],
        evidence: tuple[EvidenceRecord, ...],
        encounter_id: str,
        decision_id: str,
        decision_source: str,
    ) -> RecognitionAccount:
        if self.writer is None:
            raise RuntimeError("identity writer is required for authorization")
        selected = next(
            (
                proposal
                for proposal in proposals
                if proposal.stored_identity_id == selected_identity_id
            ),
            None,
        )
        if selected is None:
            raise ValueError("selected identity has no correspondence proposal")
        if not evidence:
            raise ValueError("registry correspondence requires attributable evidence")
        registry = self.action_tree_store.registry_identities()
        if selected_identity_id not in registry:
            raise ValueError("selected identity is not a friendly registry identity")
        if self.writer.memory.get(selected_identity_id) is None:
            raise KeyError(selected_identity_id)
        prior_atom = self.writer.memory.get(selected_identity_id)
        assert prior_atom is not None
        decision_confidence = prior_atom.confidence
        for item in evidence:
            if item.subject_id != selected_identity_id:
                raise ValueError("correspondence evidence must target the selected identity")
            self.writer.apply_evidence(selected_identity_id, item)
        atom = self.writer.memory.get(selected_identity_id)
        assert atom is not None
        supporting = tuple(
            item.evidence_id
            for item in evidence
            if item.polarity is EvidencePolarity.SUPPORTS
        )
        contradicting = tuple(
            item.evidence_id
            for item in evidence
            if item.polarity is EvidencePolarity.CONTRADICTS
        )
        account = RecognitionAccount.create(
            candidate_id=candidate_id,
            stored_identity_id=selected_identity_id,
            matched_properties=selected.matched_properties,
            changed_properties=selected.changed_properties,
            allowed_transformations=selected.allowed_transformations,
            supporting_evidence_ids=supporting,
            contradicting_evidence_ids=contradicting,
            rival_proposal_ids=tuple(
                item.proposal_id for item in proposals if item is not selected
            ),
            calibrated_confidence=atom.confidence,
            decision_confidence=decision_confidence,
            decision_outcome=True,
            decision_source=decision_source,
            provenance=selected.provenance,
        )
        self.action_tree_store.record_semantic_identity_decision(
            identity_id=selected_identity_id,
            encounter_id=encounter_id,
            decision_id=decision_id,
            status="accepted",
            evidence_ids=tuple(item.evidence_id for item in evidence),
        )
        return account

    def reject(
        self,
        *,
        candidate_id: str,
        selected_identity_id: str,
        proposals: tuple[MatchProposal, ...],
        encounter_id: str,
        decision_id: str,
        decision_source: str,
        evidence_ids: tuple[str, ...] = (),
    ) -> RecognitionAccount:
        selected = next(
            (
                proposal
                for proposal in proposals
                if proposal.stored_identity_id == selected_identity_id
            ),
            None,
        )
        if selected is None:
            raise ValueError("selected identity has no correspondence proposal")
        if selected_identity_id not in self.action_tree_store.registry_identities():
            raise ValueError("selected identity is not a friendly registry identity")
        self.action_tree_store.record_semantic_identity_decision(
            identity_id=selected_identity_id,
            encounter_id=encounter_id,
            decision_id=decision_id,
            status="rejected",
            evidence_ids=evidence_ids,
        )
        atom = self.writer.memory.get(selected_identity_id) if self.writer else None
        return RecognitionAccount.create(
            candidate_id=candidate_id,
            stored_identity_id=None,
            rival_proposal_ids=tuple(item.proposal_id for item in proposals),
            decision_confidence=atom.confidence if atom is not None else 0.0,
            decision_outcome=False,
            decision_source=decision_source,
            provenance=selected.provenance,
        )

    def reverse(
        self,
        *,
        identity_id: str,
        encounter_id: str,
        decision_id: str,
        evidence_ids: tuple[str, ...],
    ) -> None:
        if not evidence_ids:
            raise ValueError("reversal requires attributable evidence")
        self.action_tree_store.record_semantic_identity_decision(
            identity_id=identity_id,
            encounter_id=encounter_id,
            decision_id=decision_id,
            status="reversed",
            evidence_ids=evidence_ids,
        )
