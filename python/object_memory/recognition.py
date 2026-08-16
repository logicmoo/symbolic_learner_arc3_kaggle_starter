from __future__ import annotations

from typing import Mapping

from .models import (
    InstanceParameters,
    MatchProposal,
    ObjectChange,
    ProvenanceRef,
    RecognitionAccount,
)


class InstanceMatcher:
    """Generate advisory correspondence proposals from normalized instances."""

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
        appearance_keys = sorted({*stored.appearance, *current.appearance})
        for key in appearance_keys:
            before = stored.appearance.get(key)
            after = current.appearance.get(key)
            field = f"appearance.{key}"
            if before == after:
                matched.append(field)
            else:
                changed[field] = {"from": before, "to": after}
                transformations.append("recolor" if key == "color" else "appearance_change")
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
