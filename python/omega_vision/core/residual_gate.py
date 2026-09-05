"""SoW Appendix A.2 ``core/residual_gate.py`` / §7 — reduction and the salience gate.

Reads the description length the account leaves uncovered and turns it into the
three-way disposition ``absorbed | provisional | commit_request`` (SoW §7). The
gate decision is :class:`object_memory.memory.ResidualGate`; the analyzer that
separates unexplained structure from recognized transformations into
:class:`~object_memory.models.ResidualCandidate` objects is
:class:`object_memory.recognition.ResidualAnalyzer`.
"""

from object_memory.memory import ResidualGate
from object_memory.models import ResidualCandidate, ResidualDisposition
from object_memory.recognition import ResidualAnalyzer

__all__ = ["ResidualGate", "ResidualAnalyzer", "ResidualCandidate", "ResidualDisposition"]
