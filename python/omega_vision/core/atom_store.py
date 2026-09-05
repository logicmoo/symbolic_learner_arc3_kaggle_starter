"""SoW Appendix A.2 ``core/atom_store.py`` / §9 — the persistent symbolic store.

The store has three layers (SoW §9): the Atomspace layer (committed atoms, links,
truth values), the encounter log, and the artifact store/index. ``AtomStore`` is the
SoW name for the Atomspace layer, implemented by
:class:`object_memory.memory.SymbolicMemory`; the backend-neutral record facade is
:class:`object_memory.store.SymbolicStore`; the artifact index is
:class:`object_memory.store.ArtifactIndex`.
"""

from object_memory.memory import SymbolicMemory
from object_memory.store import (
    ArtifactIndex,
    InMemorySemanticBackend,
    SemanticStoreBackend,
    SymbolicStore,
)

# SoW A.2 filename is atom_store.py; the Atomspace layer is SymbolicMemory.
AtomStore = SymbolicMemory

__all__ = [
    "AtomStore",
    "SymbolicMemory",
    "SymbolicStore",
    "ArtifactIndex",
    "InMemorySemanticBackend",
    "SemanticStoreBackend",
]
