from __future__ import annotations

from dataclasses import replace
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
)
from .memory import SingleWriter
from .store import SymbolicStore


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
    ) -> tuple[MatchProposal, ...]:
        proposals = [
            self.compare(
                candidate_id=candidate_id,
                current=current,
                stored_identity_id=identity_id,
                stored=instance,
                provenance=provenance,
            )
            for identity_id, instance in stored.items()
        ]
        return tuple(
            sorted(
                proposals,
                key=lambda item: (
                    -(item.similarity if item.similarity is not None else -1.0),
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
        latest: dict[str, InstanceParameters] = {}
        for encounter in self.store.encounters.records():
            if encounter.object_identity_id is not None:
                previous = latest.get(encounter.object_identity_id)
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
                latest[encounter.object_identity_id] = current
        return latest

    def propose(self, encounter_id: str) -> tuple[MatchProposal, ...]:
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
    """Classify explicit before/after correspondences into semantic changes."""

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

    def __init__(self, writer: SingleWriter, action_tree_store: object) -> None:
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
