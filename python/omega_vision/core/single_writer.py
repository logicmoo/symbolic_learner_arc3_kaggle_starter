"""SoW Appendix A.2 ``core/single_writer.py`` / A.1.1 — the single writer.

Only this code path commits durable atoms, truth values, merge decisions,
tombstones, or rule evidence, and it runs every admission check on every commit.
Implementation: :class:`object_memory.memory.SingleWriter`.
"""

from object_memory.memory import SingleWriter

__all__ = ["SingleWriter"]
