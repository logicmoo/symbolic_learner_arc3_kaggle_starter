"""SoW Appendix A.2 ``core/encounter_log.py`` / §9 — the encounter log.

Append-only observations, action IDs, prediction IDs, candidate IDs, decision
records, and evaluation annotations, kept by reference and deterministically
replayable (SoW §9, A.1.8). Implementation:
:class:`object_memory.memory.EncounterLog`.
"""

from object_memory.memory import EncounterLog

__all__ = ["EncounterLog"]
