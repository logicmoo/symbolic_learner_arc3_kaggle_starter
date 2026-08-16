from __future__ import annotations

from typing import Mapping

from .models import InstanceParameters, MatchProposal, ProvenanceRef, RecognitionAccount


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
