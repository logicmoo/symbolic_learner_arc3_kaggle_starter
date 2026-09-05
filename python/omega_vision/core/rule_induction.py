"""SoW Appendix A.2 ``core/rule_induction.py`` / §10 — rules over committed objects.

Rules begin low-order and grow toward conjunctions only as evidence forces them;
a rule is an atom whose truth is the record of its predictions (SoW §10). The
staged, replaceable providers live in :mod:`object_memory.learning`; the connected
Phase-3 flow is :class:`object_memory.learning.GameLearningPipeline`.
"""

from object_memory.learning import (
    GameLearningPipeline,
    RuleEvidence,
    RuleExecutor,
    RuleInducer,
    RuleRanker,
    RuleRivalSet,
    TransformationCandidate,
    TransformationLearner,
    TransitionAnalyzer,
    TransitionRecord,
)

__all__ = [
    "TransitionAnalyzer",
    "TransformationLearner",
    "RuleInducer",
    "RuleRanker",
    "RuleExecutor",
    "GameLearningPipeline",
    "RuleEvidence",
    "RuleRivalSet",
    "TransitionRecord",
    "TransformationCandidate",
]
