"""SoW Appendix A.2 ``core/identity_merge.py`` / §5, A.1.3 — committed identity.

A handle, once assigned, is the same atom thereafter and is exact at query time;
similarity may *propose* a match but may never *be* the identity relation. Merges
and splits are decisions committed through the single writer and carry evidence
and provenance. The decision records live in :mod:`object_memory.models`
(:class:`MergeDecision`, :class:`SplitDecision`); the registry authority that only
applies a selection when attributable evidence exists is
:class:`object_memory.recognition.RegistryCorrespondenceAuthority`.

``IdentityMerge`` is a thin façade over the single writer's merge/split path (the
"factory method or two" that belongs in the SoW entry layer).
"""

from __future__ import annotations

from object_memory.memory import SingleWriter
from object_memory.models import IdentityDecision, MergeDecision, SplitDecision
from object_memory.recognition import RegistryCorrespondenceAuthority


class IdentityMerge:
    """Commit identity merges/splits through the one writer (SoW §5, A.1.1/3)."""

    def __init__(self, writer: SingleWriter) -> None:
        self._writer = writer

    def merge(self, decision: MergeDecision, resulting_atom):
        return self._writer.merge_identities(decision, resulting_atom)

    def split(self, decision: SplitDecision, resulting_atoms):
        return self._writer.split_identity(decision, tuple(resulting_atoms))

    def reverse(self, decision_id: str, reason: str) -> None:
        self._writer.reverse_identity_decision(decision_id, reason)


__all__ = [
    "IdentityMerge",
    "MergeDecision",
    "SplitDecision",
    "IdentityDecision",
    "RegistryCorrespondenceAuthority",
]
