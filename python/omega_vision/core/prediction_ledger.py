"""SoW Appendix A.2 ``core/prediction_ledger.py`` / §10 — the prediction ledger.

A prediction is a durable record that must exist *before* the outcome, which makes
hindsight rule-credit structurally impossible (SoW §10, A.1.7). Implementation:
:class:`object_memory.prediction.PredictionLedger`; the exact-identity rule
registry is :class:`object_memory.prediction.RuleStore`.
"""

from object_memory.models import PredictionRecord
from object_memory.prediction import PredictionLedger, RuleStore

__all__ = ["PredictionLedger", "RuleStore", "PredictionRecord"]
